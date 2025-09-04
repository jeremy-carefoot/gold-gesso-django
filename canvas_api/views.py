from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings
from .tasks import refreash_assignments, refreash_courses
from .models import Assignment, Course

from .services import CanvasAPIService
from .serializers import (
    CourseSerializer,
    AssignmentSerializer,
    CalendarEventSerializer,
    UserProfileSerializer
)


class HealthCheckView(APIView):
    """Health check endpoint"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        return Response({
            'status': 'healthy',
            'canvas_configured': bool(settings.CANVAS_API_BASE_URL and settings.CANVAS_API_TOKEN)
        })


class CoursesView(APIView):
    """View for handling course-related operations"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get list of courses"""
        try:
            user=self.request.user
            refreash_courses.delay(user.id)
            queryset = Course.objects.filter(user_ref=user.id)
            serializedData = CourseSerializer(queryset, many=True).data
            return Response(serializedData, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CourseDetailView(APIView):
    """View for handling specific course operations"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, course_id):
        """Get details of a specific course"""
        try:
            service = CanvasAPIService()
            course = service.get_course(course_id)
            serializer = CourseSerializer(course)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CourseAssignmentsView(APIView):
    """View for handling assignment-related operations"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, course_id):
        """Get assignments for a specific course"""
        try:
            service = CanvasAPIService()
            assignments = service.get_course_assignments(course_id)
            serializer = AssignmentSerializer(assignments, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
class AllAssignmentsView(APIView):
    """View which returns all assignments for all courses."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get all assignments for all courses"""
        try:
            user=self.request.user
            refreash_courses.delay(user.id)
            refreash_assignments.delay(user.id)
            queryset = Assignment.objects.filter(user_ref=user.id).order_by("due_at")
            serializedData = AssignmentSerializer(queryset, many=True).data
            return Response(serializedData, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request):
        pass
        # THis method will be used to allow the manual assignmnt addition

        

# This should actually be a model view because we don't care to pass the course id when we are looking at a specific assignment.
class AssignmentDetailView(APIView):
    """View for handling specific assignment operations"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, course_id, assignment_id):
        """Get details of a specific assignment"""
        try:
            service = CanvasAPIService()
            assignment = service.get_assignment(course_id, assignment_id)
            serializer = AssignmentSerializer(assignment)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CalendarEventsView(APIView):
    """View for handling calendar events"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get calendar events"""
        try:
            service = CanvasAPIService()
            start_date = request.query_params.get('start_date')
            end_date = request.query_params.get('end_date')
            events = service.get_calendar_events(start_date=start_date, end_date=end_date)
            serializer = CalendarEventSerializer(events, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserProfileView(APIView):
    """View for handling user profile"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get current user's profile"""
        try:
            service = CanvasAPIService()
            profile = service.get_user_profile()
            serializer = UserProfileSerializer(profile)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )