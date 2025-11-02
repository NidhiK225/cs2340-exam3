from django import forms
from .models import roadTripper, TripPost

class RoadTripperForm(forms.ModelForm):
    class Meta:
        model = roadTripper
        fields = [
            "image",
            "firstName",
            "lastName",
            "location",
            "travel_headline",
            "travel_budget",
            "interests",
            "destinations",
            "hide_profile",
            "hide_image",
            "hide_travel_headline",
            "hide_location",
            "hide_travel_budget",
        ]
        widgets = {
            'hide_location': forms.CheckboxInput(),
            'hide_image': forms.CheckboxInput(),
            'hide_travel_headline': forms.CheckboxInput(),
            'hide_profile': forms.CheckboxInput(),
            'hide_travel_budget': forms.CheckboxInput(),
        }
        labels = {
            'hide_image': "Keep your image private",
            'hide_travel_headline': "Keep your headline private",
            'hide_profile': "Keep profile hidden",
            'hide_location': "Hide your location",
            'hide_travel_budget': "Hide budget",
        }


class TripPostForm(forms.ModelForm):
    class Meta:
        model = TripPost
        fields = ['photo', 'location', 'description', 'tagged_friends']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # ✅ Make all fields optional
        for field in self.fields.values():
            field.required = False

        if user:
            # ✅ Only show roadtrippers and exclude the current user
            self.fields['tagged_friends'].queryset = roadTripper.objects.exclude(user=user)
