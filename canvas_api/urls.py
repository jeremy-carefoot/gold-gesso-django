from django.urls import path
from .views import (
    HealthCheckView,
    CoursesView,
    CourseDetailView,
    CourseAssignmentsView,
    AssignmentDetailView,
    CalendarEventsView,
    UserProfileView,
    RefreshAssignmentsView,
    CachedCoursesView,
    CachedAssignmentsView,
    UpdateAssignmentView,
    CreateAssignmentView,
    DeleteAssignmentView
)

app_name = 'canvas_api'

urlpatterns = [
    path('health/', HealthCheckView.as_view(), name='health-check'), # Change the path of this to "update-db/cron-target/"
    path('courses/', CoursesView.as_view(), name='courses'),
    path('cached-courses/', CachedCoursesView.as_view(), name='cached-courses'),
    path('courses/<int:course_id>/', CourseDetailView.as_view(), name='course-detail'),
    path('courses/<int:course_id>/assignments/', CourseAssignmentsView.as_view(), name='assignments'),
    # path('courses/<int:course_id>/assignments/<int:assignment_id>/', AssignmentDetailView.as_view(), name='assignment-detail'),
    path('all-assignments/update/', RefreshAssignmentsView.as_view(), name="refresh-assignments"), # want to change this path to all-assignments/refresh/
    path('all-assignments/cached/', CachedAssignmentsView.as_view(), name="cached-assignments"),
    path('update-assignment/', UpdateAssignmentView.as_view(), name="update-assignment"),
    path('create-assignment/', CreateAssignmentView.as_view(), name="create-assignment"),
    # path('delete-assignment/<int:id>/', DeleteAssignmentView.as_view(), name="delete-assignment"), # In case we want to use the id
    path('delete-assignments/', DeleteAssignmentView.as_view(), name="delete-assignment"), # Using the assignment_id for now can change later
    path('calendar-events/', CalendarEventsView.as_view(), name='calendar-events'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
]