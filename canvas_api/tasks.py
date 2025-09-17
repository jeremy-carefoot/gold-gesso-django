# from celery import shared_task
from .services import CanvasAPIService
from .models import Assignment, Course
from apps.authentication.models import CustomUser
import asyncio
from asgiref.sync import async_to_sync

# @shared_task

def refresh_assignments(user_id):
    """This function processes the canvas API responses for assignments and creates Assignment model instances."""
    user = CustomUser.objects.get(id=user_id)
    courses = Course.objects.filter(user_ref=user.id)
    courses_ids = [course.id for course in courses]

    def run_async():
        # Use context manager to properly close session
        async def call_canvas_api():
            async with CanvasAPIService(user=user) as service:
                assignment_tasks = [service.get_course_assignments(course_id) for course_id in courses_ids]
                all_assignments = await asyncio.gather(*assignment_tasks)
            return all_assignments
        return asyncio.run(call_canvas_api())
    
    all_assignments = run_async()
    course_refs = {course.id: course for course in courses}

    assignments_to_create = []
    assignments_to_update = []

    existing_assignments = {
        (a.assignment_id, a.user_ref.id): a for a in Assignment.objects.filter(user_ref=user)
    }

    for course_assignments in all_assignments:
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
                # 'course_id': assignment.get('course_id'),
                'grading_type': assignment.get('grading_type', 'percent'),
                'is_submitted': False, # Assignments created by refresh will by default be is_submitted = False
                'is_custom': False, # Assignments fetched from canvas API will never be custom
                'course_ref': course_refs[assignment["course_id"]],
                'user_ref': user
            }
            # Remove None values
            assignment_data = {k: v for k, v in assignment_data.items() if v is not None}
            # Extract the lookup fields, use the rest as defaults
            assignment_id = assignment_data.pop('assignment_id')
            # user_ref = assignment_data.pop('user_ref')

            existing_key = (assignment_id, user.id)
            if existing_key in existing_assignments:
                existing_assignment = existing_assignments[existing_key]
                for field, value in assignment_data.items():
                    if not (field in ["user_ref","is_submitted"]): # Don't need to update the user_ref, should not change is_submitted
                        setattr(existing_assignment, field, value)
                assignments_to_update.append(existing_assignment)
            else:
                assignments_to_create.append(Assignment(assignment_id=assignment_id, **assignment_data))
            
    if assignments_to_create:
        Assignment.objects.bulk_create(assignments_to_create, ignore_conflicts=True)
            
    if assignments_to_update:
        Assignment.objects.bulk_update(assignments_to_update, fields=['name', 'description', 'due_at', 'unlock_at', 'lock_at','points_possible', 'grade_group_students_individually','allowed_attempts', 'grading_type', 'course_ref'])

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