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


class RecruiterProfile(models.Model):
    class Priority(models.TextChoices):
        LOW = "LOW", "Low"
        MEDIUM = "MEDIUM", "Medium"
        HIGH = "HIGH", "High"

    user = models.OneToOneField("accounts.User", on_delete=models.CASCADE, related_name="recruiter_profile")
    company_name = models.CharField(max_length=255)
    website = models.URLField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    about = models.TextField(blank=True)

    # Recommendation weighting (per recruiter)
    weight_skill = models.PositiveIntegerField(default=100)
    weight_experience = models.PositiveIntegerField(default=10)
    weight_location = models.PositiveIntegerField(default=5)

    # Simpler priority controls (override weights at runtime)
    skill_priority = models.CharField(max_length=6, choices=Priority.choices, default=Priority.MEDIUM)
    experience_priority = models.CharField(max_length=6, choices=Priority.choices, default=Priority.MEDIUM)
    location_priority = models.CharField(max_length=6, choices=Priority.choices, default=Priority.MEDIUM)

    def __str__(self):
        return self.company_name or self.user.username
