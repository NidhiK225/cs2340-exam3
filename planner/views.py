# planner/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from accounts.decorators import planner_required
from .models import Planner
from .forms import PlannerForm
from django.db.models import Q, Count
from django.urls import reverse
from urllib.parse import urlencode

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST

from datetime import datetime



from django.db.models import Q, Count
from django.urls import reverse
from urllib.parse import urlencode

import requests
from math import radians, cos
from django.http import JsonResponse
from .services.suggestions import suggest_activities
from trip.models import Trip, Stop

# @login_required
# @planner_required
# def index(request):
#     """List all job seekers (for recruiters only)."""
#     name_term = request.GET.get("name", "")
#     location_term = request.GET.get("location", "")

#     template_data = {
#         "title": "Job Seekers",
#         "planner": Planner,
#     }
#     return render(request, "planner/index.html", {"template_data": template_data})

# @login_required
# @planner_required
# def map_view(request):
#     return render(request, 'planner/map.html')

@login_required
@planner_required
def trip_map_and_suggestions(request):
    #trip = get_object_or_404(Trip, pk=pk, created_by=request.user)
    user_trips = Trip.objects.filter(created_by = request.user)
    suggestions = None
    provider = None
    error = None
    vibe_options = ["relaxed", "balanced", "active"]
    party_options = ["adults", "family", "kids"]
    budget_options = ["conservative", "moderate", "splurge"]

    default_preferences = {
        "interests":"",
        "vibe": "balanced",
        "party": "adults",
        "budget_flexibility": "moderate",
    }

    if request.method == "POST":
        lat = request.POST.get("latitude")
        lng = request.POST.get("longitude")
        if not lat or not lng:
            error = "Please search for a location on the map before getting suggestions."
            preferences = default_preferences
        else:
            preferences = {
                "interests": request.POST.get("interests", "").strip(),
                "vibe": request.POST.get("vibe", "balanced").strip(),
                "party": request.POST.get("party", "adults").strip(),
                "budget_flexibility": request.POST.get("budget_flexibility", "moderate").strip(),
            }
            try:
                res = suggest_activities(
                    latitude = float(lat),
                    longitude = float(lng),
                    preferences = preferences,
                    max_items = 8
                )
                suggestions = res.get("activities", [])
                provider = res.get("provider")
                error = res.get("error")

            except Exception as e:
                error = f"Suggestion service error. Check suggest_activities function. Error: {e}"
    else:
        preferences = default_preferences

    return render (
        request,
        "planner/map.html",
        {
            "suggestions": suggestions,
            "provider": provider,
            "error": error,
            "preferences": preferences,
            "vibe_options": vibe_options,
            "party_options": party_options,
            "budget_options": budget_options,
            'user_trips':user_trips,
        },
    )
@login_required
@planner_required
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
@planner_required
def my_profile(request):
    """Allow a planner to view their own profile."""
    planner = get_object_or_404(Planner, user=request.user)

    template_data = {
        "planner": planner,
        "name": f"{planner.firstName} {planner.lastName}",
        # "travel_budget": planner.travel_budget,
        # "interests": planner.interests,
        # "destinations": planner.destinations,
        # "links": planner.links.all(),
    }
    return render(request, "planner/show.html", {"template_data": template_data})

@login_required
@planner_required
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


@login_required
@require_POST
def add_stop_to_trip(request):
    try:
        title = request.POST.get("title")
        description = request.POST.get("description")
        cost = request.POST.get("cost")
        date_str = request.POST.get("date")
        trip_id = request.POST.get("trip_id")
        latitude = request.POST.get("stop_latitude")
        longitude = request.POST.get("stop_longitude")

        if not all([title, date_str, trip_id]):
            return JsonResponse({"status": "error", "message":"Missing required fields."}, status=400)

        stop_date = datetime.strptime(date_str, "%Y-%m-%d").date()

        trip = Trip.objects.get(pk=trip_id, created_by=request.user)

        Stop.objects.create(
            trip=trip,
            title=title,
            description=description,
            cost=cost,
            date=stop_date,
            # latitude=float(latitude),
            # longitude = float(longitude)
        )

        return JsonResponse({"status":"success", "message":f"Stop '{title}' added!"})
    except Trip.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Trip not found or unauthorized."}, status=404)
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)
