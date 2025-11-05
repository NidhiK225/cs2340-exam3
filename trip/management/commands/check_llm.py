from types import SimpleNamespace
from datetime import date, timedelta
from django.core.management.base import BaseCommand

from trip.services.llm import suggest_activities


class Command(BaseCommand):
    help = "Check LLM configuration and fetch a sample of suggestions."

    def handle(self, *args, **options):
        sample_trip = SimpleNamespace(
            title="Sample Weekend in Seattle",
            description="Quick getaway focused on food and views.",
            location="Seattle, WA",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=2),
            approximate_budget=500,
            max_capacity=2,
        )
        prefs = {"interests": "food, views", "vibe": "balanced", "party": "adults", "budget_flexibility": "moderate"}
        res = suggest_activities(sample_trip, prefs, max_items=3)
        activities = res.get("activities", [])
        provider = res.get("provider")
        error = res.get("error")

        self.stdout.write(self.style.SUCCESS(f"Provider: {provider}  Items: {len(activities)}"))
        if error:
            self.stdout.write(self.style.WARNING(f"Error: {error}"))
        for i, a in enumerate(activities, 1):
            self.stdout.write(f"{i}. {a.get('name')} — {a.get('location')} ({a.get('category')})")

