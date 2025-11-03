from django.urls import path
from . import views
urlpatterns = [
    # path('', views.index, name='planner.index'),
    path('<int:id>/', views.show, name='planner.show'),
    path("me/", views.my_profile, name="planner.my_profile"), 
    path("me/edit/", views.edit_profile, name="planner.edit_profile"),
]