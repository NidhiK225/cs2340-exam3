# accounts/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    class Roles(models.TextChoices):
        RECRUITER = "RECRUITER", "Recruiter"
        JOB_SEEKER = "JOB_SEEKER", "Job Seeker"

    role = models.CharField(
        max_length=20, choices=Roles.choices, default=Roles.JOB_SEEKER, db_index=True
    )

    @property
    def is_recruiter(self) -> bool:
        return self.role == self.Roles.RECRUITER

    @property
    def is_roadTripper(self) -> bool:
        return self.role == self.Roles.JOB_SEEKER


class PlannerProfile(models.Model):
    user = models.OneToOneField("accounts.User", on_delete=models.CASCADE, related_name="recruiter_profile")
    #company_name = models.CharField(max_length=255)
    website = models.URLField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    about = models.TextField(blank=True)

