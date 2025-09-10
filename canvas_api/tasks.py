# from celery import shared_task
from .services import CanvasAPIService
from .models import Assignment, Course
from apps.authentication.models import CustomUser
import asyncio
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .serializers import AssignmentSerializer

# @shared_task

def refresh_assignments(user_id):
    """This function processes the canvas API responses for assignments and creates Assignment model instances."""
    user = CustomUser.objects.get(id=user_id)
    channel_layer = get_channel_layer()
    group_name = f"user_{user_id}_assignments"
    
    # Send notification that refresh has started
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'assignment_update',
            'update_type': 'refresh_started',
            'message': 'Fetching latest assignments from Canvas...'
        }
    )

    def run_async():
        # Use context manager to properly close session
        async def call_canvas_api():
            async with CanvasAPIService(user=user) as service:
                courses = await service.get_courses()
                courses_ids = [course['id'] for course in courses]
                assignment_tasks = [service.get_course_assignments(course_id) for course_id in courses_ids]
                all_course_assignments = await asyncio.gather(*assignment_tasks)
            return all_course_assignments
        return asyncio.run(call_canvas_api())
    
    all_course_assignments = run_async()

    for course_assignments in all_course_assignments:
        for assignment in course_assignments:
            # Filter to only include fields that exist in the Assignment model
            assignment_data = {
                'assignment_id': assignment.get('id'),
                'name': assignment.get('name'),
                'description': assignment.get('description'),
                'due_at': assignment.get('due_at'),
                'unlock_at': assignment.get('unlock_at'),
                'lock_at': assignment.get('lock_at'),
                'points_possible': assignment.get('points_possible'),
                'grade_group_students_individually': assignment.get('grade_group_students_individually', False),
                'allowed_attempts': assignment.get('allowed_attempts'),
                'has_submitted_submissions': assignment.get('has_submitted_submissions', False),
                'course_id': assignment.get('course_id'),
                'grading_type': assignment.get('grading_type', 'percent'),
                'course_ref': Course.objects.get(id=assignment["course_id"]),
                'user_ref': user
            }
            # Remove None values
            assignment_data = {k: v for k, v in assignment_data.items() if v is not None}
            # Extract the lookup fields, use the rest as defaults
            assignment_id = assignment_data.pop('assignment_id')
            user_ref = assignment_data.pop('user_ref')
            
            newAssignment = Assignment.objects.update_or_create(
                assignment_id=assignment_id,
                user_ref=user_ref,
                defaults=assignment_data
            )
    
    # Get updated assignments and send via WebSocket
    updated_assignments = Assignment.objects.filter(user_ref=user_id).order_by("due_at")
    serialized_data = AssignmentSerializer(updated_assignments, many=True).data
    
    # Send notification that refresh is complete with updated data
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'assignment_update',
            'update_type': 'assignments_updated',
            'data': serialized_data,
            'message': 'Assignments have been updated'
        }
    )

# @shared_task
def refresh_courses(user_id):
    """This function processes the canvas API responses for courses and creates Course model instances."""
    user = CustomUser.objects.get(id=user_id)

    def run_async():
        # Use context manager to properly close session
        async def call_canvas_api():
            async with CanvasAPIService(user=user) as service:
                courses = await service.get_courses()
            return courses
        return asyncio.run(call_canvas_api())

    courses = run_async()

    for course in courses:
        # Filter to only include fields that exist in the Course model (excluding many2many)
        course_data = {
            'id': course.get('id'),
            'uuid': course.get('uuid'),
            'name': course.get('name'),
            'calendar': course.get('calendar', {}),
            'time_zone': course.get('time_zone'),
            # 'user_ref': user
        }
        # Remove None values
        course_data = {k: v for k, v in course_data.items() if v is not None}
        course_id = course_data.pop('id')
        course_obj, created = Course.objects.update_or_create(
            id = course_id,
            defaults=course_data
            )
        course_obj.user_ref.add(user)