from django.db import models
from django.conf import settings
from roadTripper.models import RoadTripper

class Trip(models.Model):
    planner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE, related_name = "planned_trips")
    title = models.CharField(max_length = 200)
    description = models.TextField()
    location = models.CharField(max_length = 200)
    start_date = models.DateField()
    end_date = models.DateField()
    approximate_budget = models.DecimalField(max_digits = 10, decimal_places = 2)
    max_capacity =  models.PositiveIntegerField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_trips",
        limit_choices_to={"role": "PLANNER"},
    )
    created_at = models.DateTimeField(auto_now_add=True)

    roadTrippers = models.ManyToManyField(RoadTripper, related_name="joined_trippers", blank="True")
    numSignedUp = models.PositiveIntegerField(default=0)

    @property
    def spots_left(self):
        return self.max_capacity - self.numSignedUp
    
    def __str__(self):
        return self.title
    

class Stop(models.Model):
    trip = models.ForeignKey(
        'Trip',
        on_delete = models.CASCADE,
        related_name='stops'
    )

    title = models.CharField(max_length = 255)
    description = models.TextField(blank = True)
    cost = models.CharField(max_length = 50, blank = True)

    date = models.DateField()

    # latitude = models.DecimalField(max_digits = 9, decimal_places = 6)
    # longitude = models.DecimalField(max_digits = 9, decimal_places =6)

    created_at = models.DateTimeField(auto_now_add = True)
    def __str__(self):
        return f"{self.title} ({self.date})"