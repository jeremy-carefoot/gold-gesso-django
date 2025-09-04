from django.db import models
from django.contrib.auth.models import User
import json

class PrettyJSONEncoder(json.JSONEncoder):
    """This class is used to overwrite the encoder for JSONField objects."""
    def __init__(self, *args, indent, sort_keys, **kwargs):
        super().__init__(*args, indent=2, sort_keys=True, **kwargs)
class Course(models.Model):
    id = models.IntegerField(primary_key=True)
    uuid = models.IntegerField()
    name = models.CharField()
    # grading_standard_id = ???
    calendar = models.JSONField(default={}, encoder=PrettyJSONEncoder)
    # TIME_ZONE_CHOICES = [] # Not gonna worry about the choices for now 
    time_zone = models.CharField()

    user_ref = models.ForeignKey(User, on_delete=models.CASCADE) # Need this for prod but annoying right now
    # Because these models are repersenting the response of the canvas API, the API doesn't return the user id that we are using in Django currently

class Assignment(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField()
    description = models.TextField()
    due_at = models.DateTimeField()
    unlock_at = models.DateTimeField()
    lock_at = models.DateTimeField()
    points_possible = models.IntegerField()
    grade_group_students_individually = models.BooleanField(default=False)
    allowed_attempts = models.IntegerField()
    has_submitted_submissions = models.BooleanField(default=False)
    course_id = models.IntegerField()
    GRADING_TYPE_CHOICES = [("pass_fail","Pass fail"), ("percent", "Percent"), ("letter_grade", "Letter grade"), ("gpa_scale", "GPA scale"), ("points", "Points"), ("not_graded", "Not graded")]
    grading_type = models.CharField(choices=GRADING_TYPE_CHOICES, default="percent")

    course_ref = models.ForeignKey(Course, on_delete=models.CASCADE) # Must make this value work in the Assignment serializer. 
    user_ref = models.ForeignKey(User, on_delete=models.CASCADE) # See above