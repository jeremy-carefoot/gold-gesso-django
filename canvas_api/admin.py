from django.contrib import admin
from .models import Course, Assignment

# Register your models here.
admin.site.register(Course)
# admin.site.register(Assignment)

@admin.action(description="Duplicate selected assignments and assign duplicated to current user.")
def duplicate_assignments(modeladmin, request, queryset):
    for assignment in queryset:
        assignment.id = None
        assignment.user_ref = request.user
        assignment.save()

class AssignmentAdmin(admin.ModelAdmin):
    actions=[duplicate_assignments]

admin.site.register(Assignment, AssignmentAdmin)

