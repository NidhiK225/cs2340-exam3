# roadTripper/models.py
from django.db import models
from django.conf import settings  # use settings.AUTH_USER_MODEL
from django.urls import reverse
from django.contrib.auth.models import User


class roadTripper(models.Model):
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="roadTripper_profile"
    )

    # general personal information
    firstName = models.CharField("First Name", max_length=255)
    lastName  = models.CharField("Last Name", max_length=255)
    location  = models.CharField("Home Location", max_length=255, blank=True)
    image     = models.ImageField("Profile Image", upload_to='roadTripper_images/', null=True, blank=True)

    # travel-related
    TRAVEL_BUDGET_CHOICES = [
        ('LOW', 'Budget-Friendly (Under $50/day)'),
        ('MID', 'Mid-Range (Approx. $50 - $150/day)'),
        ('HIGH', 'Luxury (Over $150/day)'),
        ('FLEX', 'Flexible / Varies'),
    ]
    travel_headline = models.CharField("Travel Tagline", max_length=255, blank=True,
        help_text="A short, catchy phrase about your travel style."
    )
    travel_budget = models.CharField("Travel Budget", max_length=4, choices=TRAVEL_BUDGET_CHOICES, default='MID')
    interests = models.ManyToManyField("Interest", related_name="trippers_with_interest", blank=True)
    destinations = models.ManyToManyField("Destination", related_name="trippers_want_to_visit", blank=True)

    links = models.ManyToManyField("Link", related_name="roadTripper", blank=True)

    #privacy
    hide_image = models.BooleanField(default=False)
    hide_travel_headline = models.BooleanField(default=False)
    hide_travel_budget = models.BooleanField(default=False)
    hide_profile = models.BooleanField(default=False)
    hide_location = models.BooleanField(default=False)

    def get_absolute_url(self):
        return reverse("roadTripper.show", args=[self.id])
    
    def __str__(self):
        return f"{self.firstName} {self.lastName}"

    @property
    def full_name(self):
        return f"{self.firstName} {self.lastName}"

class Interest(models.Model):
    """Specific travel interests (e.g., 'Hiking', 'Cuisine', 'History', 'Adventure')."""
    name = models.CharField(max_length=100, unique=True)
    def __str__(self): return self.name

class Destination(models.Model):
    """Desired travel locations (e.g., 'Kyoto', 'Patagonia', 'Paris')."""
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100)
    
    def __str__(self):
        if self.city:
            return f"{self.city}, {self.country}"
        return self.country

class Link(models.Model):
    url        = models.URLField()
    def __str__(self): return self.url

class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name="notifications")
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        indexes = [models.Index(fields=["user", "-created_at"])]

class TripPost(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='trip_posts'
    )
    photo = models.ImageField(upload_to='trip_photos/')
    location = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    tagged_friends = models.ManyToManyField('roadTripper', blank=True, related_name='tagged_in_posts')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s trip to {self.location}"

    def get_absolute_url(self):
        return reverse('roadTripper.trip_detail', args=[self.id])
