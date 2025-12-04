from django.urls import path
from . import views

urlpatterns = [
    path("", views.trip_list, name="trip.list"),
    path("dashboard/", views.trip_dashboard, name="trip.dashboard"),
    path("create/", views.trip_create, name="trips.create"),
    path("<int:pk>/edit/", views.trip_edit, name="trip.edit"),
    path("<int:pk>/suggestions/", views.trip_suggestions, name="trip.suggestions"),
    path("trips/<int:trip_id>/remove_from_trip/<int:rt_id>/", views.remove_from_trip, name="trip.remove_from_trip"),
    path("trips/<int:trip_id>/add_to_trip/<int:rt_id>/", views.add_to_trip, name="trip.add_to_trip"),
]
