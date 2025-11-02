from django.shortcuts import render
from trip.models import Trip, Application
import requests
import json


def index(request):
    qs = Trip.objects.all().prefetch_related("s")

    trips_with_coords = []
    for trip in qs:
        if trip.address:
            try:
                response = requests.get(
                    "https://nominatim.openstreetmap.org/search",
                    params={"format": "json", "q": trip.address},
                    headers={"User-Agent": "trip-finder/1.0"}
                )
                data = response.json()
                if data:
                    trip.lat = float(data[0]["lat"])
                    trip.lng = float(data[0]["lon"])
                    trips_with_coords.append(trip)
            except Exception:
                continue

    trips_json = json.dumps([
        {
            "id": trip.id,
            "title": trip.title,
            "location": trip.location,
            "remote_type": trip.get_remote_type_display(),
            "visa": trip.visa_sponsorship,
            "salary_min": trip.salary_min,
            "salary_max": trip.salary_max,
            "s": [s.name for s in trip.s.all()],
            "description": trip.description,
            "lat": trip.lat,
            "lng": trip.lng,
        }
        for trip in trips_with_coords
        if getattr(trip, "lat", None) is not None and getattr(trip, "lng", None) is not None
    ])

    applied_ids = []
    if request.user.is_authenticated and getattr(request.user, 'is_roadTripper', False):
        applied_ids = list(Application.objects.filter(user=request.user).values_list('trip_id', flat=True))

    return render(request, "map/index.html", {
        "trips_json": trips_json,
        "applied_ids": json.dumps(applied_ids),
        "user_is_authenticated": request.user.is_authenticated,
        "user_is_roadTripper": getattr(request.user, 'is_roadTripper', False),
    })
