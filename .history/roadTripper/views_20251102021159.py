from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import TripPost, roadTripper
from .forms import TripPostForm

@login_required
def create_trip_post(request):
    # Ensure the logged-in user has a roadTripper profile
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
            trip_post.roadtripper = roadtripper  # ✅ assign roadTripper, not user
            trip_post.save()
            form.save_m2m()
            messages.success(request, "Trip post created successfully!")
            return redirect("roadTripper.feed")  # make sure your feed URL name matches
    else:
        form = TripPostForm()

    return render(request, "roadTripper/createTrip.html", {"form": form})



@login_required
def trip_feed(request):
    posts = TripPost.objects.select_related("roadtripper").all().order_by("-created_at")
    template_data = {"posts": posts}
    return render(request, "roadTripper/tripFeed.html", {"template_data": template_data})


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
    roadTripper = get_object_or_404(RoadTripperModel, id=id)

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

    template_data = {"form": form, "roadTripper": roadTripper}
    return render(request, "roadTripper/edit.html", {"template_data": template_data})


@login_required
@roadtripper_required
def add_link(request):
    roadTripper = get_object_or_404(RoadTripperModel, user=request.user)

    name = (request.POST.get("name") or "").strip()
    if not name:
        return HttpResponseBadRequest("name required.")

    link = Link(url=name)
    link.save()
    roadTripper.links.add(link)
    roadTripper.save()

    return redirect("roadTripper.edit_profile")
