import os
from datetime import date
from typing import Any, Dict

from .providers import local as local_provider
from .providers import gemini as gemini_provider
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
    """Top-level suggestion service with dual provider support.

    Selection order:
    - If LLM_PROVIDER is set (gemini|openai), try that first, then the other, then local.
    - Else auto-detect: if GEMINI_API_KEY -> gemini; elif OPENAI_API_KEY -> openai; else local.
    """
    prompt = _build_prompt(trip, preferences, max_items)

    provider_pref = (os.getenv("LLM_PROVIDER") or "").strip().lower()
    has_gemini = bool(os.getenv("GEMINI_API_KEY"))
    has_openai = bool(os.getenv("OPENAI_API_KEY"))

    def try_gemini():
        return gemini_provider.suggest(trip, prompt, max_items=max_items)

    def try_openai():
        return openai_provider.suggest(trip, prompt, max_items=max_items)

    # Build ordered list of providers to attempt
    order = []
    if provider_pref in ("gemini", "openai"):
        order = [provider_pref, "openai" if provider_pref == "gemini" else "gemini"]
    else:
        if has_gemini:
            order.append("gemini")
        if has_openai:
            order.append("openai")

    # Try providers in order
    for p in order:
        if p == "gemini" and has_gemini:
            res = try_gemini()
            if res.get("activities"):
                return res
            last_error = res.get("error")
        elif p == "openai" and has_openai:
            res = try_openai()
            if res.get("activities"):
                return res
            last_error = res.get("error")

    # Fallback to local heuristic
    local = local_provider.suggest(trip, preferences, max_items=max_items)
    # Attach last provider error if any
    try:
        if 'last_error' in locals() and last_error:
            local["error"] = last_error
    except Exception:
        pass
    return local
