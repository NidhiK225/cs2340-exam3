from django.contrib import admin
from .models import roadTripper, Institution, Experience, Skill, Link, CandidateSearch

class roadTripperAdmin(admin.ModelAdmin):
    search_fields = ['firstName', 'lastName', 'headline']
    autocomplete_fields = ('user',)
    filter_horizontal = ("skills",)  # many-to-many pickers
    list_display = ("full_name", "location", "years_experience", "open_to_work")
    list_filter = ("open_to_work",)

class InstitutionAdmin(admin.ModelAdmin):
    search_fields = ("name", "location")   # needed for autocomplete

class ExperienceAdmin(admin.ModelAdmin):
    search_fields = ("name", "location")   # needed for autocomplete

class SkillAdmin(admin.ModelAdmin):
    search_fields = ['name']

class LinkAdmin(admin.ModelAdmin):
    search_fields = ['name']

class CandidateSearchAdmin(admin.ModelAdmin):
    search_fields = ['user']

admin.site.register(roadTripper, roadTripperAdmin)
admin.site.register(Institution, InstitutionAdmin)
admin.site.register(Experience, ExperienceAdmin)
admin.site.register(Skill, SkillAdmin)
admin.site.register(Link, LinkAdmin)
admin.site.register(CandidateSearch, CandidateSearchAdmin)
