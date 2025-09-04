from rest_framework import serializers
from .models import Assignment, Course


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'


class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = '__all__'


class CalendarEventSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    title = serializers.CharField(read_only=True)
    start_at = serializers.DateTimeField(read_only=True)
    end_at = serializers.DateTimeField(read_only=True)
    all_day = serializers.BooleanField(read_only=True)
    context_code = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True, allow_blank=True)


class UserProfileSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    short_name = serializers.CharField(read_only=True)
    sortable_name = serializers.CharField(read_only=True)
    login_id = serializers.CharField(read_only=True)
    primary_email = serializers.EmailField(read_only=True)
    avatar_url = serializers.URLField(read_only=True, allow_null=True)