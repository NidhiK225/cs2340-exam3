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
from .models import TripPost
from .forms import TripPostForm

@login_required
@roadtripper_required
def create_trip_post(request):
    if request.method == 'POST':
        form = TripPostForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            trip_post = form.save(commit=False)
            trip_post.user = request.user
            trip_post.save()
            form.save_m2m()
            messages.success(request, "Trip post created successfully!")
            return redirect('roadTripper.trip_feed')
    else:
        form = TripPostForm(user=request.user)

    return render(request, 'roadTripper/createTrip.html', {'form': form})




@login_required
def trip_feed(request):
    """Show all trip posts from all road trippers."""
    posts = TripPost.objects.select_related('author').prefetch_related('tagged_friends').order_by('-created_at')
    template_data = {'posts': posts}
    return render(request, 'roadTripper/tripFeed.html', {'template_data': template_data})


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




