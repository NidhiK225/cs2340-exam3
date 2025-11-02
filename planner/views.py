# planner/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from accounts.decorators import recruiter_required, roadtripper_required
from .models import Planner
from .forms import PlannerForm
from django.db.models import Q, Count
from django.urls import reverse
from urllib.parse import urlencode


# @login_required
# @recruiter_required
# def index(request):
#     """List all job seekers (for recruiters only)."""
#     name_term = request.GET.get("name", "")
#     location_term = request.GET.get("location", "")

#     template_data = {
#         "title": "Job Seekers",
#         "planner": Planner,
#     }
#     return render(request, "planner/index.html", {"template_data": template_data})



@login_required
@recruiter_required
def show(request, id):
    """Show details of a single job seeker (for recruiters only)."""
    planner = get_object_or_404(Planner, id=id)

    template_data = {
        "planner": planner,
        "name": f"{planner.firstName} {planner.lastName}",
        "links": planner.links.all(),
        "hide_profile": planner.hide_profile,
    }

    return render(request, "planner/show.html", {"template_data": template_data})


@login_required
@roadtripper_required
def my_profile(request):
    """Allow a planner to view their own profile."""
    planner = get_object_or_404(Planner, user=request.user) 

    template_data = {
        "planner": planner,
        "name": f"{planner.firstName} {planner.lastName}",
        "travel_budget": planner.travel_budget,
        "interests": planner.interests,
        "destinations": planner.destinations,
        "links": planner.links.all(),
    }
    return render(request, "planner/show.html", {"template_data": template_data})

@login_required
@roadtripper_required
def edit_profile(request):
    """Allow a planner to edit their own profile."""
    planner = get_object_or_404(Planner, user=request.user)  

    if request.method == "POST":
        form = PlannerForm(request.POST, request.FILES, instance=planner)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("planner.my_profile")
    else:
        form = PlannerForm(instance=planner)

    template_data = {}
    template_data['form'] = form
    template_data['planner'] = planner

    return render(request, "planner/edit.html", {"template_data": template_data})