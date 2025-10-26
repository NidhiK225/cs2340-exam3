from django.contrib import admin
from .models import roadTripper, Link

class roadTripperAdmin(admin.ModelAdmin):
    search_fields = ['firstName', 'lastName', 'headline']
    autocomplete_fields = ('user',)
    list_display = ("full_name", "location")


class LinkAdmin(admin.ModelAdmin):
    search_fields = ['name']

admin.site.register(roadTripper, roadTripperAdmin)
admin.site.register(Link, LinkAdmin)
