from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='roadTripper.index'),
    path('create_post/', views.create_trip_post, name='roadTripper.create_trip_post'),
    path('feed/', views.trip_feed, name='roadTripper.trip_feed'),
]
