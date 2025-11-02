from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseBadRequest
from .models import TripPost, roadTripper
from .forms import TripPostForm

@login_required
def create_trip_post(request):
    roadtripper, created = roadTripper.objects.get_or_create(
        user=request.user,
        defaults={
            "firstName": request.user.first_name or "First",
            "lastName": request.user.last_name or "Last",
        },
    )

    if request.method == "POST":
        form = TripPostForm(request.POST, request.FILES)
        if form.is_valid():
            trip_post = form.save(commit=False)
            trip_post.roadtripper = roadtripper
            trip_post.save()
            form.save_m2m()
            messages.success(request, "Trip post created successfully!")
            return redirect("roadTripper.trip_feed")
    else:
        form = TripPostForm()

    return render(request, "roadTripper/createTrip.html", {"form": form})

@login_required
def trip_feed(request):
    posts = TripPost.objects.select_related("roadtripper").all().order_by("-created_at")
    return render(request, "roadTripper/tripFeed.html", {"posts": posts})

@login_required
def index(request):
    roadtrippers = roadTripper.objects.all()
    return render(request, "roadTripper/index.html", {"roadtrippers": roadtrippers})

@login_required
def show(request, id):
    roadtripper = get_object_or_404(roadTripper, id=id)
    return render(request, "roadTripper/show.html", {"roadtripper": roadtripper})

@login_required
def my_profile(request):
    roadtripper = get_object_or_404(roadTripper, user=request.user)
    return render(request, "roadTripper/show.html", {"roadtripper": roadtripper})

@login_required
def edit_profile(request):
    roadtripper = get_object_or_404(roadTripper, user=request.user)
    if request.method == "POST":
        form = RoadTripperForm(request.POST, request.FILES, instance=roadtripper)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("roadTripper.my_profile")
    else:
        form = RoadTripperForm(instance=roadtripper)
    return render(request, "roadTripper/edit.html", {"form": form, "roadtripper": roadtripper})
s