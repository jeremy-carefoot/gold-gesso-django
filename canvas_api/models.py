from django.db import models
from apps.authentication.models import CustomUser
import json

class PrettyJSONEncoder(json.JSONEncoder):
    """This class is used to overwrite the encoder for JSONField objects."""
    def __init__(self, *args, indent, sort_keys, **kwargs):
        super().__init__(*args, indent=2, sort_keys=True, **kwargs)
class Course(models.Model):
    id = models.IntegerField(primary_key=True)
    uuid = models.CharField()
    name = models.CharField()
    # grading_standard_id = ???
    calendar = models.JSONField(default=dict, encoder=PrettyJSONEncoder)
    # TIME_ZONE_CHOICES = [] # Not gonna worry about the choices for now 
    time_zone = models.CharField()

    user_ref = models.ManyToManyField(CustomUser, related_name='courses')

    def __repr__(self):
        return self.name
    
    def __str__(self):
        return self.name

class Assignment(models.Model):
    assignment_id = models.IntegerField(null=True)
    name = models.CharField()
    description = models.TextField()
    due_at = models.DateTimeField(null=True)
    unlock_at = models.DateTimeField(null=True)
    lock_at = models.DateTimeField(null=True)
    points_possible = models.IntegerField()
    grade_group_students_individually = models.BooleanField(default=False)
    allowed_attempts = models.IntegerField()
    has_submitted_submissions = models.BooleanField(default=False)
    course_id = models.IntegerField()
    GRADING_TYPE_CHOICES = [("pass_fail","Pass fail"), ("percent", "Percent"), ("letter_grade", "Letter grade"), ("gpa_scale", "GPA scale"), ("points", "Points"), ("not_graded", "Not graded")]
    grading_type = models.CharField(choices=GRADING_TYPE_CHOICES, default="percent")

    course_ref = models.ForeignKey(Course, on_delete=models.CASCADE)
    user_ref = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    def __repr__(self):
        return f"{self.course_ref.name} {self.name}"
    
    def __str__(self):
        return f"{self.course_ref.name} {self.name}"