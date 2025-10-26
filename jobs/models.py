from django.db import models
from django.conf import settings

class Job(models.Model):
    class RemoteType(models.TextChoices):
        ONSITE = "ONSITE", "On-site"
        REMOTE = "REMOTE", "Remote"
        HYBRID = "HYBRID", "Hybrid"

    title = models.CharField(max_length=200, db_index=True)
    description = models.TextField()
    location = models.CharField(max_length=200, db_index=True)
    address = models.CharField(max_length=200, db_index=True)
    remote_type = models.CharField(max_length=6, choices=RemoteType.choices)

    salary_min = models.PositiveIntegerField(null=True, blank=True)
    salary_max = models.PositiveIntegerField(null=True, blank=True)
    visa_sponsorship = models.BooleanField(default=False)
    min_experience = models.PositiveIntegerField(null=True, blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="jobs",
        limit_choices_to={"role": "RECRUITER"},
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Application(models.Model):
    class Status(models.TextChoices):
        APPLIED = 'APPLIED', 'Applied'
        REVIEWED = 'REVIEWED', 'Reviewed'
        INTERVIEW = 'INTERVIEW', 'Interview'
        OFFER = 'OFFER', 'Offer'
        CLOSED = 'CLOSED', 'Closed'

    class Meta:
        unique_together = ("job", "user")
    job = models.ForeignKey("jobs.Job", on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    applied_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.APPLIED,
    )


    def __str__(self):
        job_title = getattr(self.job, "title", "(no title)")
        username = getattr(self.user, "username", str(self.user_id))
        return f"Application by {username} for {job_title}"
