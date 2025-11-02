# roadTripper/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from accounts.decorators import recruiter_required, roadtripper_required
from .models import roadTripper as RoadTripperModel
from .models import Link
from .forms import RoadTripperForm
from django.db.models import Q, Count
from django.urls import reverse
from urllib.parse import urlencode


@login_required
@recruiter_required
def index(request):
    """List all job seekers (for recruiters only)."""
    name_term = request.GET.get("name", "")
    location_term = request.GET.get("location", "")

    template_data = {
        "title": "Job Seekers",
        "roadTripper": roadTripper,
    }
    return render(request, "roadTripper/index.html", {"template_data": template_data})



@login_required
@recruiter_required
def show(request, id):
    """Show details of a single job seeker (for recruiters only)."""
    roadTripper = get_object_or_404(roadTripper, id=id)

    template_data = {
        "roadTripper": roadTripper,
        "name": f"{roadTripper.firstName} {roadTripper.lastName}",
        "links": roadTripper.links.all(),
        "hide_profile": roadTripper.hide_profile,
    }

    return render(request, "roadTripper/show.html", {"template_data": template_data})


@login_required
@roadtripper_required
def my_profile(request):
    """Allow a roadTripper to view their own profile."""
    roadTripper = get_object_or_404(RoadTripperModel, user=request.user) 

    template_data = {
        "roadTripper": roadTripper,
        "name": f"{roadTripper.firstName} {roadTripper.lastName}",
        "travel_budget": roadTripper.travel_budget,
        "interests": roadTripper.interests,
        "destinations": roadTripper.destinations,
        "links": roadTripper.links.all(),
    }
    return render(request, "roadTripper/show.html", {"template_data": template_data})

@login_required
@roadtripper_required
def edit_profile(request):
    """Allow a roadTripper to edit their own profile."""
    roadTripper = get_object_or_404(RoadTripperModel, user=request.user)  

    if request.method == "POST":
        form = RoadTripperForm(request.POST, request.FILES, instance=roadTripper)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("roadTripper.my_profile")
    else:
        form = RoadTripperForm(instance=roadTripper)

    template_data = {}
    template_data['form'] = form
    template_data['roadTripper'] = roadTripper

    return render(request, "roadTripper/edit.html", {"template_data": template_data})

@login_required
@roadtripper_required
def add_link(request):
    roadTripper = get_object_or_404(RoadTripperModel, user=request.user)

    name = (request.POST.get("name") or "").strip()
    if not name:
        return HttpResponseBadRequest(" name required.")

    link = Link()
    link.url = name
    link.save()
    roadTripper.links.add(link)
    roadTripper.save()

    # redirect back to your editor page (adjust the URL name/args to your project)
    return redirect("roadTripper.edit_profile")




