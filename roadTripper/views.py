# roadTripper/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from accounts.decorators import roadtripper_required
from .models import RoadTripper
from .models import Link
from .forms import RoadTripperForm
from django.db.models import Q, Count
from django.urls import reverse
from urllib.parse import urlencode
from .models import TripPost
from .forms import TripPostForm
from .forms import RoadTripperForm, TripPostForm  # include TripPostForm
from .models import RoadTripper, TripPost  # include TripPost model
import requests
from math import radians, cos
from django.http import JsonResponse


@login_required
@roadtripper_required
def map_view(request):
    return render(request, 'roadTripper/map.html')
@login_required
@roadtripper_required
def create_trip_post(request):
    roadtripper = get_object_or_404(RoadTripper, user=request.user)

    if request.method == "POST":
        form = TripPostForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            trip_post = form.save(commit=False)

            trip_post.roadtripper = roadtripper

            api_key ="AIzaSyCB1Yppcqoe9_A8euT_t-Pz2odNPTlBtw0"
            location_text = trip_post.location
            url = f"https://maps.googleapis.com/maps/api/geocode/json?address={location_text}&key={api_key}"

            response = requests.get(url)
            data = response.json()
            if data["status"] == "OK":
                coords = data["results"][0]["geometry"]["location"]
                trip_post.lat = coords["lat"]
                trip_post.lng = coords["lng"]

            trip_post.user = request.user
            trip_post.save()
            form.save_m2m()
            messages.success(request, "Trip post created successfully!")
            return redirect("roadTripper.trip_feed")
    else:
        form = TripPostForm(user=request.user)

    template_data = {"form": form}
    return render(request, "roadTripper/createTrip.html", {"template_data": template_data})


@login_required
def trip_feed(request):
    posts = TripPost.objects.select_related("roadtripper").prefetch_related("tagged_friends").all().order_by("-created_at")
    return render(request, "roadTripper/tripFeed.html", {"posts": posts})



@login_required
# @roadtripper_required
def index(request):
    """List all job seekers (for road trippers only)."""
    roadTripper = get_object_or_404(RoadTripper, id=id)
    name_term = request.GET.get("name", "")
    location_term = request.GET.get("location", "")

    template_data = {
        "title": "Job Seekers",
        "roadTripper": roadTripper,
    }
    return render(request, "roadTripper/index.html", {"template_data": template_data})



@login_required
# @roadtripper_required
def show(request, id):
    """Show details of a single job seeker (for recruiters only)."""
    roadTripper = get_object_or_404(RoadTripper, id=id)

    template_data = {
        "roadTripper": roadTripper,
        "name": f"{roadTripper.firstName} {roadTripper.lastName}",
        "links": roadTripper.links.all(),
        "hide_profile": roadTripper.hide_profile,
    }

    return render(request, "roadTripper/show.html", {"template_data": template_data})


@login_required
# @roadtripper_required
def my_profile(request):
    """Allow a roadTripper to view their own profile."""
    roadTripper = get_object_or_404(RoadTripper, user=request.user)

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
    roadTripper = get_object_or_404(RoadTripper, user=request.user)

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
    roadTripper = get_object_or_404(RoadTripper, user=request.user)

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



def posts_api(request):
    lat = float(request.GET.get('lat'))
    lng = float(request.GET.get('lng'))
    radius = float(request.GET.get('radius', 10))

    lat_range = radius / 111
    lng_range = radius / (111 * cos(radians(lat)))

    posts = TripPost.objects.filter(
        lat__range = (lat-lat_range, lat+lat_range),
        lng__range=(lng - lng_range, lng + lng_range),
        roadtripper__isnull=False
    )

    data = [{
        "lat": p.lat,
        "lng": p.lng,
        "username": p.roadtripper.user.username,
        "caption":p.description,
        "image":p.photo.url if p.photo else "",
        "timestamp":int(p.created_at.timestamp()*1000),

        "tagged_friends": [
            friend.user.username
            for friend in p.tagged_friends.all()
            if friend.user is not None
        ]
    } for p in posts]

    # print("--- DEBUG TAGGED FRIENDS ---")
    # for post_data in data:
    #     if post_data.get("taggedFriends"):
    #         print(f"Post by {post_data['username']} has tags: {post_data['taggedFriends']}")
    # print("----------------------------")
    return JsonResponse(data, safe = False)