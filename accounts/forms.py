from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from roadTripper.models import roadTripper
from .models import RecruiterProfile

class roadTripperignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Roles.JOB_SEEKER
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
            roadTripper.objects.create(user=user, firstName=user.first_name, lastName=user.last_name)
        return user


class RecruiterSignUpForm(UserCreationForm):
    company_name = forms.CharField(max_length=255, required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Roles.RECRUITER
        if commit:
            user.save()
            RecruiterProfile.objects.create(user=user, company_name=self.cleaned_data["company_name"])
        return user


class RecommendationWeightsForm(forms.ModelForm):
    class Meta:
        model = RecruiterProfile
        fields = ("weight_skill", "weight_experience", "weight_location")
        labels = {
            "weight_skill": "Skill weight (per matched skill)",
            "weight_experience": "Experience weight (meets min exp)",
            "weight_location": "Location weight (soft bonus)",
        }


class RecommendationPriorityForm(forms.ModelForm):
    class Meta:
        model = RecruiterProfile
        fields = ("skill_priority", "experience_priority", "location_priority")
        labels = {
            "skill_priority": "Skill priority",
            "experience_priority": "Experience priority",
            "location_priority": "Location priority",
        }
        help_texts = {
            "skill_priority": "How strongly to favor skill matches.",
            "experience_priority": "Boost when candidate meets min experience.",
            "location_priority": "Soft bonus for location match.",
        }
        help_texts = {
            "weight_skill": "Default 100. Higher means skills dominate ranking.",
            "weight_experience": "Default 10. Bonus if candidate meets min experience.",
            "weight_location": "Default 5. Small bonus for location match.",
        }
