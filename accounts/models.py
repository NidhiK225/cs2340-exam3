# accounts/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    class Roles(models.TextChoices):
        PLANNER = "PLANNER", "Planner"
        ROAD_TRIPPER = "ROAD_TRIPPER", "Road Tripper"

    role = models.CharField(
        max_length=20, choices=Roles.choices, default=Roles.ROAD_TRIPPER, db_index=True
    )

    @property
    def is_planner(self) -> bool:
        return self.role == self.Roles.PLANNER

    @property
    def is_roadTripper(self) -> bool:
        return self.role == self.Roles.ROAD_TRIPPER
