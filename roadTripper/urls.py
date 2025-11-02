from django.urls import path
from . import views
urlpatterns = [
    path('', views.index, name='roadTripper.index'),
    path('<int:id>/me/', views.show, name='roadTripper.show'),
    path("me/", views.my_profile, name="roadTripper.my_profile"), 
    path("me/edit/", views.edit_profile, name="roadTripper.edit_profile"),
]