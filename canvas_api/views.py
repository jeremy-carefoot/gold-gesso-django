from rest_framework import status
import asyncio
import threading
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings
from asgiref.sync import sync_to_async, async_to_sync
from .tasks import refresh_assignments, refresh_courses
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
            'canvas_configured': bool(settings.CANVAS_API_BASE_URL)
        })


class CoursesView(APIView):
    """View for handling course-related operations"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get list of courses"""
        try:
            user=self.request.user
            # Fire and forget using thread - non-blocking
            thread = threading.Thread(
                target=lambda: asyncio.run(refresh_courses(user.id))
            )
            thread.daemon = True
            thread.start()
            
            # Return stale data immediately
            queryset = Course.objects.filter(user_ref=user.id)
            serializedData = CourseSerializer(queryset, many=True).data
            return Response(serializedData, status=status.HTTP_200_OK)
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
            # Fire and forget using threads - non-blocking
            async def run_both_tasks():
                await asyncio.gather(
                    refresh_courses(user.id),
                    refresh_assignments(user.id)
                )
            
            def run_in_thread():
                asyncio.run(run_both_tasks())
            
            thread = threading.Thread(target=run_in_thread)
            thread.daemon = True  # Don't wait for thread to complete
            thread.start()
            
            # Return stale data immediately
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
        # This method will be used to allow the manual assignmnt addition


class CachedCoursesView(APIView):
    """View for handling course-related operations"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get list of courses"""
        try:
            user=self.request.user
            queryset = Course.objects.filter(user_ref=user.id)
            serializedData = CourseSerializer(queryset, many=True).data
            return Response(serializedData, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# None of the views below are being used
class CourseDetailView(APIView):
    """View for handling specific course operations"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, course_id):
        """Get details of a specific course"""
        try:
            service = CanvasAPIService(user=request.user)
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
            service = CanvasAPIService(user=request.user)
            assignments = service.get_course_assignments(course_id)
            serializer = AssignmentSerializer(assignments, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

# This should actually be a model view because we don't care to pass the course id when we are looking at a specific assignment.
class AssignmentDetailView(APIView):
    """View for handling specific assignment operations"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, course_id, assignment_id):
        """Get details of a specific assignment"""
        try:
            service = CanvasAPIService(user=request.user)
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
            service = CanvasAPIService(user=request.user)
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
            service = CanvasAPIService(user=request.user)
            profile = service.get_user_profile()
            serializer = UserProfileSerializer(profile)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )