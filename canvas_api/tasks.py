from celery import shared_task
from .services import CanvasAPIService
from .models import Assignment, Course
from django.contrib.auth.models import User

@shared_task
def create_assignments(user_id):
    """This function processes the canvas API responses for assignments and creates Assignment model instances."""
    user = User.objects.get(id=user_id)
    service = CanvasAPIService()
    courses = service.get_courses()
    courses_ids = [course['id'] for course in courses]
    for course_id in courses_ids:
        course_assignments = service.get_course_assignments(course_id)
        for assignment in course_assignments:
            # Filter to only include fields that exist in the Assignment model
            assignment_data = {
                'id': assignment.get('id'),
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
            newAssignment = Assignment.objects.create(**assignment_data)

@shared_task
def create_courses(user_id):
    """This function processes the canvas API responses for courses and creates Course model instances."""
    user = User.objects.get(id=user_id)
    service = CanvasAPIService()
    courses = service.get_courses()
    for course in courses:
        # Filter to only include fields that exist in the Course model
        course_data = {
            'id': course.get('id'),
            'uuid': course.get('uuid'),
            'name': course.get('name'),
            'calendar': course.get('calendar', {}),
            'time_zone': course.get('time_zone'),
            'user_ref': user
        }
        # Remove None values
        course_data = {k: v for k, v in course_data.items() if v is not None}
        newCourse = Course.objects.create(**course_data)
