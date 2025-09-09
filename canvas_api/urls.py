from django.urls import path
from .views import (
    HealthCheckView,
    CoursesView,
    CourseDetailView,
    CourseAssignmentsView,
    AssignmentDetailView,
    CalendarEventsView,
    UserProfileView,
    AllAssignmentsView,
    CachedCoursesView,
)

app_name = 'canvas_api'

urlpatterns = [
    path('health/', HealthCheckView.as_view(), name='health-check'),
    path('courses/', CoursesView.as_view(), name='courses'),
    path('cached-courses/', CachedCoursesView.as_view(), name='cached-courses'),
    path('courses/<int:course_id>/', CourseDetailView.as_view(), name='course-detail'),
    path('courses/<int:course_id>/assignments/', CourseAssignmentsView.as_view(), name='assignments'),
    # path('courses/<int:course_id>/assignments/<int:assignment_id>/', AssignmentDetailView.as_view(), name='assignment-detail'),
    path('all-assignments/', AllAssignmentsView.as_view(), name="all-assignments"),
    path('calendar-events/', CalendarEventsView.as_view(), name='calendar-events'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
]