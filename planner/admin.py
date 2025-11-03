from django.contrib import admin
from .models import Planner

class PlannerAdmin(admin.ModelAdmin):
    search_fields = ['firstName', 'lastName', 'headline']
    autocomplete_fields = ('user',)
    list_display = ("full_name", "location")

admin.site.register(Planner, PlannerAdmin)