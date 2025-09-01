from rest_framework import serializers


class CourseSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    course_code = serializers.CharField(read_only=True)
    enrollment_term_id = serializers.IntegerField(read_only=True)
    start_at = serializers.DateTimeField(read_only=True, allow_null=True)
    end_at = serializers.DateTimeField(read_only=True, allow_null=True)
    enrollments = serializers.ListField(read_only=True, required=False)


class AssignmentSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True, allow_blank=True)
    due_at = serializers.DateTimeField(read_only=True, allow_null=True)
    points_possible = serializers.FloatField(read_only=True)
    course_id = serializers.IntegerField(read_only=True)
    submission_types = serializers.ListField(read_only=True)
    has_submitted_submissions = serializers.BooleanField(read_only=True, required=False)


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