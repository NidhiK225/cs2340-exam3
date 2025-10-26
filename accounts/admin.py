from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, RecruiterProfile

class RecruiterProfileInline(admin.StackedInline):
    model = RecruiterProfile
    can_delete = True
    verbose_name_plural = "Recruiter Profiles"

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

@admin.register(RecruiterProfile)
class RecruiterProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "company_name", "location")
    search_fields = ("company_name", "user__username")
