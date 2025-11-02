from django.urls import path
from .views import signup_choice, roadTripper_signup, planner_signup, RoleLoginView, logout_view

urlpatterns = [
    path("signup/", signup_choice, name="signup.choice"),
    path("signup/roadTripper/", roadTripper_signup, name="signup.roadTripper"),
    path("signup/planner/", planner_signup, name="signup.planner"),
    path("map/roadTripper/", planner_signup, name="map.index"),
    path("login/", RoleLoginView.as_view(), name="login"),
    path("logout/", logout_view, name="logout"),  # ✅ use custom view
    #path("settings/recommendations/", recommendation_settings, name="accounts.recommendation_settings"),
]
