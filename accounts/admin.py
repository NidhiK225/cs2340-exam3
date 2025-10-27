from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, PlannerProfile

class RecruiterProfileInline(admin.StackedInline):
    model = PlannerProfile
    can_delete = True
    verbose_name_plural = "Planner Profiles"

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Role", {"fields": ("role",)}),
    )
    inlines = []

    # Show the RecruiterProfile inline only if the user is a recruiter
    def get_inlines(self, request, obj=None):
        if obj and getattr(obj, "role", None) == User.Roles.RECRUITER:
            return [RecruiterProfileInline]
        return []

@admin.register(PlannerProfile)
class RecruiterProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "location")
    search_fields = ("company_name", "user__username")
