from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings
from .tasks import refresh_assignments, refresh_courses
from .models import Assignment, Course
import traceback
import hashlib

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
            refresh_courses(user.id)
            queryset = Course.objects.filter(user_ref=user.id)
            serializedData = CourseSerializer(queryset, many=True).data
            return Response(serializedData, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': str(e),
                 "Traceback": traceback.format_exc()},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RefreshAssignmentsView(APIView):
    """View which updates the cached assignments for all courses."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get all assignments for all courses"""
        try:
            user=self.request.user
            refresh_courses(user.id)
            refresh_assignments(user.id)
            # queryset = Assignment.objects.filter(user_ref=user.id).order_by("due_at")
            # serializedData = AssignmentSerializer(queryset, many=True).data
            # return Response(serializedData, status=status.HTTP_200_OK)
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': str(e),
                 "Traceback": traceback.format_exc()},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

class CachedAssignmentsView(APIView):
    """View for getting cached assignments"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get list of cached assignments"""
        try:
            user=self.request.user
            queryset = Assignment.objects.filter(user_ref=user.id)
            serializedData = AssignmentSerializer(queryset, many=True).data
            return Response(serializedData, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': str(e),
                 "Traceback": traceback.format_exc()},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


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
                {'error': str(e),
                 "Traceback": traceback.format_exc()},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
class UpdateAssignmentView(APIView):
    """View for handling assignment update post requests"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Update respective assignment with new given values"""
        try:
            user=self.request.user
            assignment_response_objects = self.request.data.get("assignments")
            for aro in assignment_response_objects:
                assignment_id = aro.get("assignment_id")
                if (not assignment_id) or (assignment_id is None):
                    raise Exception("Must pass assignment_id in post request")
                assignment = Assignment.objects.get(user_ref=user.id, assignment_id=assignment_id)
                vaild_assignment_fields = [field.name for field in Assignment._meta.fields]
                if all(elem in vaild_assignment_fields for elem in aro):
                    for field, value in aro.items():
                        setattr(assignment, field, value)
                    assignment.save()
                else:
                    raise Exception("Invalid assignment field passed in post request")
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': str(e),
                 "Traceback": traceback.format_exc()},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

class CreateAssignmentView(APIView):
    """View for handling assignment creation post requests"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user = self.request.user
            # self.request.data.get("assignment") # ?? or just straight up one thing?
            data = request.data.copy()
            data["user_ref"] = user.id
            data["is_custom"] = True
            serializer = AssignmentSerializer(data=data)
            if serializer.is_valid(raise_exception=True):
                created_assignment = serializer.save()
                unique_string = f"{user.id}_{created_assignment.id}_{user.username}"
                hash_value = int(hashlib.md5(unique_string.encode()).hexdigest()[:8], 16)
                created_assignment.assignment_id = hash_value
                created_assignment.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': str(e),
                 "Traceback": traceback.format_exc()},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DeleteAssignmentView(APIView):
    """View for handling assignment delete requests"""
    permission_classes = [IsAuthenticated]

    def delete(self, request, **kwargs):
        try:
            user = self.request.user

            query = request.GET.get("ids")
            assignment_ids = query.split(",")
            Assignment.objects.filter(assignment_id__in=assignment_ids, user_ref=user.id).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response(
                {'error': str(e),
                 "Traceback": traceback.format_exc()},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DeleteAllView(APIView):
    """View for deleting all the courses (and thus assignments) for a user"""
    permission_classes = [IsAuthenticated]

    # Normally used when starting a new semester. So that the database is not full of old assignments and non-active courses
    # We rely on refresh to repopulate only the active courses and their assignments
    def delete(self, request, **kwargs):
        try:
            user = self.request.user
            # user = CustomUser.objects.get(id=user.id) # I don't think this is needed
            # Remove user from all courses
            courses = Course.objects.filter(user_ref=user.id)
            for course in courses:
                course.user_ref.remove(user)
            # Delete all assignments for user
            Assignment.objects.filter(user_ref=user.id).delete()
            
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response(
                {'error': str(e),
                 "Traceback": traceback.format_exc()},
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
                {'error': str(e),
                 "Traceback": traceback.format_exc()},
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
                {'error': str(e),
                 "Traceback": traceback.format_exc()},
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
                {'error': str(e),
                 "Traceback": traceback.format_exc()},
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
                {'error': str(e),
                 "Traceback": traceback.format_exc()},
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
                {'error': str(e),
                 "Traceback": traceback.format_exc()},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )