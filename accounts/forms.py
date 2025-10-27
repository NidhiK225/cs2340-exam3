from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from roadTripper.models import roadTripper
from .models import PlannerProfile

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


class PlannerSignUpForm(UserCreationForm):
    #company_name = forms.CharField(max_length=255, required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Roles.RECRUITER
        if commit:
            user.save()
            PlannerProfile.objects.create(user=user)
        return user
