from datetime import date
from typing import Any, Dict

from .providers import local as local_provider
from .providers import openai as openai_provider


def _build_prompt(trip, preferences: Dict[str, Any], max_items: int) -> str:
    start = getattr(trip, "start_date", None)
    end = getattr(trip, "end_date", None)
    duration = None
    if isinstance(start, date) and isinstance(end, date):
        duration = (end - start).days + 1

    lines = [
        "Return a strict JSON object with key 'activities' (array).",
        "Each item: name, category, description, suggested_time, location, cost_estimate, tags (array).",
        "Use specific, real venues if widely known. Include neighborhood/street when useful.",
        "If unsure, do not fabricate — provide actionable but generic local ideas instead.",
        f"Max items: {max_items}.",
        "",
        "Trip:",
        f"- Title: {getattr(trip, 'title', '')}",
        f"- Description: {getattr(trip, 'description', '')}",
        f"- Location: {getattr(trip, 'location', '')}",
        f"- Start: {start}",
        f"- End: {end}",
        f"- DurationDays: {duration}",
        f"- Budget: {getattr(trip, 'approximate_budget', '')}",
        f"- Capacity: {getattr(trip, 'max_capacity', '')}",
        "",
        "Planner preferences:",
        f"- Interests: {preferences.get('interests')}",
        f"- Vibe: {preferences.get('vibe')}",
        f"- Party: {preferences.get('party')}",
        f"- BudgetFlex: {preferences.get('budget_flexibility')}",
    ]
    return "\n".join(lines)


def suggest_activities(trip, preferences: Dict[str, Any], max_items: int = 8) -> Dict[str, Any]:
    """Top-level suggestion service.

    Order: OpenAI (if configured) else Local fallback.
    """
    prompt = _build_prompt(trip, preferences, max_items)
    # Try OpenAI first
    res = openai_provider.suggest(trip, prompt, max_items=max_items)
    if res.get("activities"):
        return res
    # Fallback to local heuristic
    local = local_provider.suggest(trip, preferences, max_items=max_items)
    # Propagate error message from provider if any, but include local activities
    if res.get("error") and local.get("activities"):
        local["error"] = res["error"]
    return local

