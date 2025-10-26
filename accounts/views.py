# accounts/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.urls import reverse
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout

from .forms import roadTripperignUpForm, RecruiterSignUpForm, RecommendationPriorityForm
from .models import User, RecruiterProfile
from .decorators import recruiter_required


# ---------- Helpers ----------
def role_redirect(user):
    """Redirect users after login/signup based on their role."""
    if user.role == User.Roles.RECRUITER:
        return reverse("jobs.create")   # recruiter goes to job posting page (dashboard later)
    else:
        return reverse("jobs.list")     # job seeker goes to job listings


# ---------- Signup Views ----------
def signup_choice(request):
    """Page where user picks Job Seeker vs Recruiter signup."""
    return render(request, "accounts/signup_choice.html")


def roadTripper_signup(request):
    """Sign up flow for job seekers."""
    if request.method == "POST":
        form = roadTripperignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # log them in immediately
            return redirect(role_redirect(user))
    else:
        form = roadTripperignUpForm()
    return render(request, "accounts/signup.html", {"form": form, "role": "Job Seeker"})


def recruiter_signup(request):
    """Sign up flow for recruiters."""
    if request.method == "POST":
        form = RecruiterSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(role_redirect(user))
    else:
        form = RecruiterSignUpForm()
    return render(request, "accounts/signup.html", {"form": form, "role": "Recruiter"})


# ---------- Login View ----------
class RoleLoginView(LoginView):
    """Custom login view that redirects based on role."""
    template_name = "accounts/login.html"

    def get_success_url(self):
        return role_redirect(self.request.user)

# ---------- Logout View ----------

def logout_view(request):
    """Logs out user via GET and redirects home."""
    logout(request)
    return redirect("home.index")  # send them back to home


# ---------- Recruiter Settings ----------
@login_required
@recruiter_required
def recommendation_settings(request):
    profile, _ = RecruiterProfile.objects.get_or_create(user=request.user, defaults={
        "company_name": getattr(request.user, "username", "")
    })

    if request.method == "POST":
        form = RecommendationPriorityForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("jobs.dashboard")
    else:
        form = RecommendationPriorityForm(instance=profile)

    return render(request, "accounts/recommendation_settings.html", {"form": form})
