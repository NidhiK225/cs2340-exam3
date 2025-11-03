from django.urls import path
from . import views
urlpatterns = [
    path('', views.index, name='roadTripper.index'),
    path('<int:id>/', views.show, name='roadTripper.show'),
    path("me/", views.my_profile, name="roadTripper.my_profile"),
    path("me/edit/", views.edit_profile, name="roadTripper.edit_profile"),
     path('create_post/', views.create_trip_post, name='roadTripper.create_trip_post'),
    path('feed/', views.trip_feed, name='roadTripper.trip_feed'),
    path('map/', views.map_view, name = 'map'),
    path('posts/', views.posts_api, name='posts_api'),
]