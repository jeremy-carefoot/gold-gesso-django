# from celery import shared_task
from .services import CanvasAPIService
from .models import Assignment, Course
from apps.authentication.models import CustomUser
import asyncio

# @shared_task

async def refresh_assignments(user_id):
    """This function processes the canvas API responses for assignments and creates Assignment model instances."""
    user = await CustomUser.objects.aget(id=user_id)
    
    # Use context manager to properly close session
    async with CanvasAPIService(user=user) as service:
        courses = await service.get_courses() # Could make this get from DB instead of calling service but I think doing so would introduce a race condition when calling the all-assignments view if the user had a new course.
        # print(f"Found {len(courses)} courses")
        courses_ids = [course['id'] for course in courses]

        assignment_tasks = [service.get_course_assignments(course_id) for course_id in courses_ids]
        all_course_assignments = await asyncio.gather(*assignment_tasks)
        # print(f"Found {sum(len(assignments) for assignments in all_course_assignments)} total assignments")

        # for course_id in courses_ids:
        for course_assignments in all_course_assignments:
            # course_assignments = service.get_course_assignments(course_id)
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
                    'course_ref': await Course.objects.aget(id=assignment["course_id"]),
                    'user_ref': user
                }
                # Remove None values
                assignment_data = {k: v for k, v in assignment_data.items() if v is not None}
                # Extract the lookup fields, use the rest as defaults
                assignment_id = assignment_data.pop('assignment_id')
                user_ref = assignment_data.pop('user_ref')
                
                newAssignment = await Assignment.objects.aupdate_or_create(
                    assignment_id=assignment_id,
                    user_ref=user_ref,
                    defaults=assignment_data
                )

# @shared_task
async def refresh_courses(user_id):
    """This function processes the canvas API responses for courses and creates Course model instances."""
    user = await CustomUser.objects.aget(id=user_id)
    async with CanvasAPIService(user=user) as service:
        courses = await service.get_courses()
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
            course_obj, created = await Course.objects.aupdate_or_create(
                id = course_id,
                defaults=course_data
                )
            await course_obj.user_ref.aadd(user)