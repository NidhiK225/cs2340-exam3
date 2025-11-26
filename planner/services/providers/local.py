from datetime import date
from typing import Any, Dict, List


def suggest(trip, preferences: Dict[str, Any], max_items: int = 8) -> Dict[str, Any]:
    """Local heuristic suggestions (no network). Always succeeds.

    Returns a dict: {"activities": [...], "provider": "local", "error": None}
    """
    location = getattr(trip, "location", "the destination") or "the destination"
    start = getattr(trip, "start_date", None)
    end = getattr(trip, "end_date", None)

    interests = [s.strip().lower() for s in (preferences.get("interests") or "").split(",") if s.strip()]
    vibe = (preferences.get("vibe") or "balanced").lower()
    party = (preferences.get("party") or "adults").lower()

    items: List[Dict[str, Any]] = []

    def add(name, category, desc, when, cost, tags=None):
        items.append({
            "name": name,
            "category": category,
            "description": desc,
            "suggested_time": when,
            "location": location,
            "cost_estimate": cost,
            "tags": tags or [],
        })

    add("City Highlights Walk", "Sightseeing", "Self-guided loop of notable landmarks and photo spots.", "Morning", "Free - $15", ["outdoors"])  # noqa
    if "food" in interests or vibe in ("relaxed", "balanced"):
        add("Local Eats Crawl", "Food", "Sample 3–4 well-rated neighborhood spots.", "Lunch/Dinner", "$20 - $60", ["culinary"])  # noqa
    if "museum" in interests or party == "adults":
        add("Museum or Gallery", "Culture", "Check featured exhibits and late hours.", "Afternoon", "$10 - $30", ["indoors"])  # noqa
    if party in ("family", "kids"):
        add("Park & Playground", "Family", "Picnic time with a nearby playground.", "Afternoon", "Free - $10", ["family"])  # noqa
    if "nature" in interests or vibe == "active":
        add("Sunset Viewpoint", "Outdoors", "Short trail to an overlook; bring layers.", "Golden Hour", "Free", ["hiking"])  # noqa
    add("Community Event", "Entertainment", "Browse local calendar for a market, music, or festival.", "Evening", "$0 - $40", ["live"])  # noqa

    return {"activities": items[:max_items], "provider": "local", "error": None}

