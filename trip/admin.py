# jobs/admin.py
from django.contrib import admin
from .models import Trip

@admin.register(Trip)
class JobAdmin(admin.ModelAdmin):
    list_display = ("title", "created_by", "location", "start_date", "end_date", "approximate_budget", "max_capacity")
    # list_filter = ("remote_type", "visa_sponsorship", "location")
    # search_fields = ("title", "description", "location")
    # autocomplete_fields = ("created_by",)
    # filter_horizontal = ("s",)
