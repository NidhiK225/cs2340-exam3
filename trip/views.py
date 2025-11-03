from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from accounts.decorators import planner_required
from django.contrib import messages
from .models import Trip
from .forms import TripForm
#from .services.recommendations import recommend_candidates_for_trip
# from .filters import JobFilter
import requests
import json

# List trips (everyone can see)
# def trip_list(request):
#     qs = Job.objects.all().select_related("created_by").prefetch_related("s")
#     f = JobFilter(request.GET, queryset=qs)
#     selected_remote_types = [v for v in request.GET.getlist("remote_type") if v]
#     applied_trips_preprocess = []
#     if request.user.is_authenticated and request.user.is_roadTripper:
#         applied_trips_preprocess = Application.objects.filter(user=request.user).values_list('trip_id', flat=True)

#     applied_trips_status = applied_trips_preprocess
#     applied_trips = json.dumps(list(applied_trips_preprocess))


#     # Map and geocoding moved to dedicated map app for speed.
#     return render(request, "trips/list.html", {
#         "filter": f,
#         "trips": f.qs,
#         # map data intentionally omitted to keep page fast
#         "selected_remote_types": selected_remote_types,
#         "applied_trips": applied_trips,
#         "applied_trips_status": applied_trips_status,
#     })

# Recruiter dashboard (see own trips only)
@login_required
@planner_required
def trip_dashboard(request):
    if request.user.is_planner:
        trips = Trip.objects.filter(created_by=request.user)
    # ?applications = Application.objects.filter(trip__in=trips)
        return render(request, 'trip/dashboard.html', {'trips':trips})
    else:
        return redirect('trips.list')

def trip_list(request):
    trips = Trip.objects.filter(created_by = request.user)
    return render(request, 'trip/dashboard.html', {'trips':trips})

# Create new trip
@login_required
@planner_required
def trip_create(request):
    if request.method == "POST":
        form = TripForm(request.POST)
        if form.is_valid():
            trip = form.save(commit=False)
            trip.planner = request.user
            trip.created_by = request.user
            trip.save()
            form.save_m2m()
            return redirect("trip.dashboard")
    else:
        form = TripForm()
    return render(request, "trip/create.html", {"form": form})

# Edit trip (only if recruiter owns it)
@login_required
@planner_required
def trip_edit(request, pk):
    trip = get_object_or_404(Trip, pk=pk, created_by=request.user)
    if request.method == "POST":
        form = TripForm(request.POST, instance=trip)
        if form.is_valid():
            form.save()
            return redirect("trip.dashboard")
    else:
        form = TripForm(instance=trip)

    return render(request, "trip/edit.html", {"form": form, "trip": trip})

#Apply Job
# @login_required
# @roadtripper_required
# def apply_trip(request, trip_id):
#     trip = get_object_or_404(Job, id=trip_id)
#     existing = Application.objects.filter(trip=trip, user=request.user).exists()
#     if existing:
#         messages.info(request, "You’ve already applied for this trip.")
#         return redirect("trips.list")
#     # Only process POST requests
#     if request.method == "POST":
#         message = request.POST.get("message")

#         # Create the application with default Applied status
#         Application.objects.create(
#             trip=trip,
#             user=request.user,
#             message=message,
#             status=Application.Status.APPLIED  # <- new
#         )

#         messages.success(request, "Your application has been sent!")
#         return redirect("trips.list")

#     # Redirect GET requests back to trip list
#     return redirect("trips.list")

#Status window
# @login_required
# def application_status(request, trip_id):
#     # Only allow trip seekers
#     if not request.user.is_roadTripper:
#         return redirect('trips.list')

#     # Get the application for this trip by this user
#     application = get_object_or_404(
#         Application,
#         trip_id=trip_id,
#         user=request.user
#     )

#     return render(request, 'trips/application_status.html', {
#         'application': application
#     })

# #Review Application
# @login_required
# @planner_required
# def trip_applications(request, trip_id):
#     trip = get_object_or_404(Job, id=trip_id, created_by=request.user)
#     applications = Application.objects.filter(trip=trip)

#     # Group applications by status
#     kanban_columns = {status: [] for status, _ in Application.Status.choices}
#     for app in applications:
#         kanban_columns[app.status].append(app)

#     return render(request, 'trips/trip_application_kanban.html', {
#         'trip': trip,
#         'kanban_columns': kanban_columns,
#         'status_choices': Application.Status.choices,  # list of (value, label)
#     })

# @login_required
# @planner_required
# def update_status(request, application_id):
#     application = get_object_or_404(Application, id=application_id)
#     if request.method == "POST":
#         new_status = request.POST.get("status")
#         if new_status in dict(Application.Status.choices).keys():
#             application.status = new_status
#             application.save()
#             messages.success(request, f"Status updated to {application.get_status_display()}.")
#         else:
#             messages.error(request, "Invalid status selected.")
#         return redirect('trip_applications', trip_id=application.trip.id)


# Show candidate recommendations for a trip (recruiter-owned only)
# @login_required
# @planner_required
# def trip_recommendations(request, pk):
#     trip = get_object_or_404(Job, pk=pk, created_by=request.user)
#     candidates = recommend_candidates_for_trip(trip)
#     return render(request, "trips/recommendations.html", {"trip": trip, "candidates": candidates})


# # Debug view to explain inclusion/exclusion reasons per candidate
# @login_required
# @planner_required
# def trip_recommendations_debug(request, pk):
#     trip = get_object_or_404(Job, pk=pk, created_by=request.user)

#     from django.db.models import Q, Count, IntegerField, Value
#     from roadTripper.models import roadTripper

#     trip__ids = list(trip.s.values_list('id', flat=True))
#     trip_min = trip.salary_min
#     trip_max = trip.salary_max

#     # Base candidates: only non-hidden profiles for privacy (may include not-open-to-work to show reason)
#     qs = roadTripper.objects.filter(hide_profile=False).prefetch_related('s')
#     if trip__ids:
#         qs = qs.annotate(_overlap=Count('s', filter=Q(s__in=trip__ids), distinct=True))
#     else:
#         qs = qs.annotate(_overlap=Value(0, output_field=IntegerField()))

#     data = []

#     # Prepare location token (soft factor only; no longer excludes)
#     remote = getattr(trip, 'remote_type', None) == getattr(trip.RemoteType, 'REMOTE', 'REMOTE')
#     city = (trip.location or '').split(',')[0].strip() if trip.location else ''
#     token = city or (trip.location or '')

#     min_exp = trip.min_experience or 0

#     for c in qs:
#         reasons = []

#         # open_to_work
#         open_ok = bool(c.open_to_work)
#         if not open_ok:
#             reasons.append('Not open to work')

#         # location check (soft): influences score but no longer excludes
#         if remote:
#             loc_ok = True
#         else:
#             if token:
#                 loc_ok = (c.location or '').lower().find(token.lower()) != -1
#             else:
#                 loc_ok = True
#         # Keep note but do not exclude candidates for location
#         if not loc_ok:
#             reasons.append('Location mismatch (soft)')

#         # salary overlap
#         if trip_min is None and trip_max is None:
#             sal_ok = True
#         else:
#             c_min = c.desired_salary_min
#             c_max = c.desired_salary_max
#             sal_ok_left = (trip_max is None) or (c_min is None) or (c_min <= trip_max)
#             sal_ok_right = (trip_min is None) or (c_max is None) or (c_max >= trip_min)
#             sal_ok = sal_ok_left and sal_ok_right
#         if not sal_ok:
#             reasons.append('Salary range does not overlap')

#         # experience meets
#         exp_ok = (c.years_experience or 0) >= min_exp

#         total_score = (getattr(c, '_overlap', 0) * 100) + (10 if exp_ok else 0)

#         # Inclusion no longer depends on location
#         included = open_ok and sal_ok

#         data.append({
#             'candidate': c,
#             'open_ok': open_ok,
#             'loc_ok': loc_ok,
#             'sal_ok': sal_ok,
#             '_overlap': getattr(c, '_overlap', 0),
#             'exp_ok': exp_ok,
#             'score': total_score,
#             'included': included,
#             'reasons': reasons,
#         })

#     # Sort primarily by included desc, then score desc
#     data.sort(key=lambda x: (x['included'], x['score']), reverse=True)

#     return render(request, "trips/recommendations_debug.html", {"trip": trip, "rows": data})
