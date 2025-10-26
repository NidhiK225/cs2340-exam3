from django import forms
from .models import roadTripper, Skill

class RoadTripperForm(forms.ModelForm):
    class Meta:
        model = roadTripper
        fields = [
            "firstName",
            "lastName",
            "location",
            "image",
            "years_experience",
            "open_to_work",
            "desired_salary_min",
            "desired_salary_max",
            "education",
            "degree",
            "startYear",
            "endYear",
            "headline",
            "hide_location",
            "hide_profile",
            "hide_image",
            "hide_headline"
        ]
        widgets = {
            "headline": forms.Textarea(attrs={"rows": 3}),
            'open_to_work': forms.CheckboxInput(),
            'hide_location': forms.CheckboxInput(),
            'hide_image': forms.CheckboxInput(),
            'hide_headline': forms.CheckboxInput(),
            'hide_profile': forms.CheckboxInput()
        }

        labels = {
            'hide_image': "Keep your image private",
            'hide_headline': "Keep your headline private",
            'hide_profile': "Keep profile hidden",
            'hide_location': "Hide your location",
        }

