# jobs/admin.py
from django.contrib import admin
from .models import Job

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("title", "location", "remote_type", "min_experience", "visa_sponsorship", "created_by", "created_at")
    list_filter = ("remote_type", "visa_sponsorship", "location")
    search_fields = ("title", "description", "location")
    autocomplete_fields = ("created_by",)
    filter_horizontal = ("skills",)
