from django.db import models
from django.conf import settings

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


    def __str__(self):
        return self.title

# class Application(models.Model):
#     class Status(models.TextChoices):
#         APPLIED = 'APPLIED', 'Applied'
#         REVIEWED = 'REVIEWED', 'Reviewed'
#         INTERVIEW = 'INTERVIEW', 'Interview'
#         OFFER = 'OFFER', 'Offer'
#         CLOSED = 'CLOSED', 'Closed'

#     class Meta:
#         unique_together = ("job", "user")
#     job = models.ForeignKey("jobs.Job", on_delete=models.CASCADE)
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     message = models.TextField()
#     applied_at = models.DateTimeField(auto_now_add=True)
#     status = models.CharField(
#         max_length=20,
#         choices=Status.choices,
#         default=Status.APPLIED,
# #     )
#     def __str__(self):
#         trip_title = getattr(self.title, "title", "(no title)")
#         username = getattr(self.created_by, "created_by", str(self.created_by))
#         return f"Application by {username} for {trip_title}"
