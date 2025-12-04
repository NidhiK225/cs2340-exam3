from django.db import models

# Create your models here.
# planner/models.py
from django.db import models
from django.conf import settings  # use settings.AUTH_USER_MODEL
from django.urls import reverse


class Planner(models.Model):
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="planner_profile"
    )

    # general personal information
    firstName = models.CharField("First Name", max_length=255)
    lastName  = models.CharField("Last Name", max_length=255)
    location  = models.CharField("Home Location", max_length=255, blank=True)
    image     = models.ImageField("Profile Image", upload_to='planner_images/', null=True, blank=True)

    # # travel-related
    # TRAVEL_BUDGET_CHOICES = [
    #     ('LOW', 'Budget-Friendly (Under $50/day)'),
    #     ('MID', 'Mid-Range (Approx. $50 - $150/day)'),
    #     ('HIGH', 'Luxury (Over $150/day)'),
    #     ('FLEX', 'Flexible / Varies'),
    # ]
    # travel_headline = models.CharField("Travel Tagline", max_length=255, blank=True,
    #     help_text="A short, catchy phrase about your travel style."
    # )
    # travel_budget = models.CharField("Travel Budget", max_length=4, choices=TRAVEL_BUDGET_CHOICES, default='MID')
    # interests = models.ManyToManyField("Interest", related_name="trippers_with_interest", blank=True)
    # destinations = models.ManyToManyField("Destination", related_name="trippers_want_to_visit", blank=True)

    # links = models.ManyToManyField("Link", related_name="planner", blank=True)

    #privacy
    hide_image = models.BooleanField(default=False)
    hide_travel_headline = models.BooleanField(default=False)
    hide_travel_budget = models.BooleanField(default=False)
    hide_profile = models.BooleanField(default=False)
    hide_location = models.BooleanField(default=False)

    def get_absolute_url(self):
        return reverse("planner.show", args=[self.id])
    
    def __str__(self):
        return f"{self.firstName} {self.lastName}"

    @property
    def full_name(self):
        return f"{self.firstName} {self.lastName}"
