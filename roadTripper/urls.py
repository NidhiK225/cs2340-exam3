from django.urls import path
from . import views
urlpatterns = [
    path('', views.index, name='roadTripper.index'),
    path('<int:id>/', views.show, name='roadTripper.show'),
    path("me/", views.my_profile, name="roadTripper.my_profile"), 
    path("me/edit/", views.edit_profile, name="roadTripper.edit_profile"),
    path("me/add_skill/", views.add_skill, name="roadTripper.add_skill"),
    path("me/add_link/", views.add_link, name="roadTripper.add_link"),
    path("me/add_experience/", views.add_experience, name="roadTripper.add_experience"),
    path("me/save_search/", views.save_candidate_search, name="roadTripper.save_candidate_search"),
    path("<int:id>/apply_search/", views.apply_candidate_search, name="roadTripper.apply_candidate_search"),
    path("<int:id>/delete_search/", views.delete_candidate_search, name="roadTripper.delete_candidate_search"),
    path("me/refresh_search/", views.refresh_candidate_searches, name="roadTripper.refresh_candidate_searches"),
]