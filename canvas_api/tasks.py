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
            assignment["course_ref"] = Course.objects.get(id=assignment["course_id"])
            assignment["user_ref"] = user
            newAssignment = Assignment.objects.create(**assignment)

@shared_task
def create_courses(user_id):
    """This function processes the canvas API responses for courses and creates Course model instances."""
    user = User.objects.get(id=user_id)
    service = CanvasAPIService()
    courses = service.get_courses()
    for course in courses:
        course["user_ref"] = user
        newCourse = Course.objects.create(**course)
