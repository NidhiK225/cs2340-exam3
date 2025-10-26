from django.shortcuts import render
from jobs.models import Job, Application
import requests
import json


def index(request):
    qs = Job.objects.all().prefetch_related("s")

    jobs_with_coords = []
    for job in qs:
        if job.address:
            try:
                response = requests.get(
                    "https://nominatim.openstreetmap.org/search",
                    params={"format": "json", "q": job.address},
                    headers={"User-Agent": "job-finder/1.0"}
                )
                data = response.json()
                if data:
                    job.lat = float(data[0]["lat"])
                    job.lng = float(data[0]["lon"])
                    jobs_with_coords.append(job)
            except Exception:
                continue

    jobs_json = json.dumps([
        {
            "id": job.id,
            "title": job.title,
            "location": job.location,
            "remote_type": job.get_remote_type_display(),
            "visa": job.visa_sponsorship,
            "salary_min": job.salary_min,
            "salary_max": job.salary_max,
            "s": [s.name for s in job.s.all()],
            "description": job.description,
            "lat": job.lat,
            "lng": job.lng,
        }
        for job in jobs_with_coords
        if getattr(job, "lat", None) is not None and getattr(job, "lng", None) is not None
    ])

    applied_ids = []
    if request.user.is_authenticated and getattr(request.user, 'is_roadTripper', False):
        applied_ids = list(Application.objects.filter(user=request.user).values_list('job_id', flat=True))

    return render(request, "map/index.html", {
        "jobs_json": jobs_json,
        "applied_ids": json.dumps(applied_ids),
        "user_is_authenticated": request.user.is_authenticated,
        "user_is_roadTripper": getattr(request.user, 'is_roadTripper', False),
    })
