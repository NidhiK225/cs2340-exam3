# accounts/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.urls import reverse
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout

from .forms import roadTripperignUpForm, PlannerSignUpForm
from .models import User
from .decorators import planner_required


# ---------- Helpers ----------
def role_redirect(user):
    """Redirect users after login/signup based on their role."""
    if user.is_superuser:
        return reverse("home.index")
    elif user.role == User.Roles.PLANNER:
        return reverse("planner.my_profile")
    elif user.role == User.Roles.ROAD_TRIPPER:
        return reverse("roadTripper.my_profile")     # road tripper goes to profile page


# ---------- Signup Views ----------
def signup_choice(request):
    """Page where user picks Road Tripper vs Planner signup."""
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
    return render(request, "accounts/signup.html", {"form": form, "role": "Road Tripper"})


def planner_signup(request):
    """Sign up flow for planners."""
    if request.method == "POST":
        form = PlannerSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            print("user created and is active")
            login(request, user)
            print("user is logged in")
            return redirect(role_redirect(user))
    else:
        form = PlannerSignUpForm()
    return render(request, "accounts/signup.html", {"form": form, "role": "Planner"})


# ---------- Login View ----------
class RoleLoginView(LoginView):
    """Custom login view that redirects based on role."""
    template_name = "accounts/login.html"

    def get_success_url(self):
        print(self.request.user.id)
        return role_redirect(self.request.user)

# ---------- Logout View ----------

def logout_view(request):
    """Logs out user via GET and redirects home."""
    logout(request)
    return redirect("home.index")  # send them back to home


# ---------- Planner Settings ----------
# @login_required
# @recruiter_required
# def recommendation_settings(request):
#     profile, _ = PlannerProfile.objects.get_or_create(user=request.user, defaults={
#         "company_name": getattr(request.user, "username", "")
#     })

#     if request.method == "POST":
#         form = RecommendationPriorityForm(request.POST, instance=profile)
#         if form.is_valid():
#             form.save()
#             return redirect("jobs.dashboard")
#     else:
#         form = RecommendationPriorityForm(instance=profile)

#     return render(request, "accounts/recommendation_settings.html", {"form": form})
