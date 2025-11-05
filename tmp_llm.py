import os
import json
import re
from datetime import date
from typing import Any, Dict

import requests
from pathlib import Path
from django.conf import settings


def _fallback_suggestions(trip, preferences: Dict[str, Any], max_items: int) -> Dict[str, Any]:
    interests = [s.strip().lower() for s in (preferences.get("interests") or "").split(",") if s.strip()]
    party = (preferences.get("party") or "adults").lower()
    vibe = (preferences.get("vibe") or "balanced").lower()
    location = trip.location or "the destination"

    base: list[Dict[str, Any]] = []

    def add(name, category, desc, when, cost, tags=None):
        base.append({
            "name": name,
            "category": category,
            "description": desc,
            "suggested_time": when,
            "location": location,
            "cost_estimate": cost,
            "tags": tags or [],
        })

    # Generic anchors
    add("Local Highlights Walking Tour", "Sightseeing",
        "Self-guided loop hitting top landmarks and scenic photo spots.",
        "Morning", "Free - $15", ["outdoors", "photography"])  # noqa

    if "food" in interests or vibe in ("balanced", "relaxed"):
        add("Neighborhood Food Crawl", "Food",
            "Try 3–4 well-rated local eateries with regional specialties.",
            "Lunch/Dinner", "$20 - $60", ["culinary"])  # noqa

    if "museum" in interests or party == "adults":
        add("Museum or Gallery", "Culture",
            "Explore a curated collection; check special exhibitions.",
            "Afternoon", "$10 - $30", ["indoors"])  # noqa

    if party in ("family", "kids"):
        add("Park + Playground Stop", "Family",
            "Playground time and picnic in a central park.",
            "Afternoon", "Free - $10", ["family", "outdoors"])  # noqa

    if "nature" in interests or vibe in ("active",):
        add("Sunset Viewpoint Hike", "Outdoors",
            "Short hike to a scenic overlook; pack layers.",
            "Golden Hour", "Free", ["hiking", "sunset"])  # noqa

    add("Local Event", "Entertainment",
        "Check community calendar for a concert, market, or festival.",
        "Evening", "$0 - $40", ["live", "local"])  # noqa

    return {"activities": base[:max_items], "provider": "fallback", "error": None}


def _build_prompt(trip, preferences: Dict[str, Any], max_items: int) -> str:
    start = getattr(trip, "start_date", None)
    end = getattr(trip, "end_date", None)
    duration = None
    if start and end and isinstance(start, date) and isinstance(end, date):
        duration = (end - start).days + 1

    lines = [
        "You are a travel planner assistant.",
        "Return a strict JSON object with key 'activities' (array).",
        "Schema for each item: name, category, description, suggested_time, location, cost_estimate, tags (array).",
        "Specificity requirement: Use real, specific places when widely known (e.g., 'Louvre Museum, Paris' or 'Pike Place Market, Seattle'). Include neighborhood or street address in 'location' where possible.",
        "If you are not confident a venue exists, avoid fabricating. Prefer landmark categories with clear search hints instead (but still provide concrete, actionable guidance).",
        f"Max items: {max_items}.",
        "Avoid duplicates. Keep concise and practical.",
        "",
        "Trip:",
        f"- Title: {trip.title}",
        f"- Description: {trip.description}",
        f"- Location: {trip.location}",
        f"- Start: {start}",
        f"- End: {end}",
        f"- DurationDays: {duration}",
        f"- Budget: {trip.approximate_budget}",
        f"- Capacity: {trip.max_capacity}",
        "",
        "Planner preferences:",
        f"- Interests: {preferences.get('interests')}",
        f"- Vibe: {preferences.get('vibe')}",
        f"- Party: {preferences.get('party')}",
        f"- BudgetFlex: {preferences.get('budget_flexibility')}",
    ]
    return "\n".join(lines)


def _parse_json_loose(text: str) -> Dict[str, Any]:
    """Attempt to parse JSON; if it fails, extract the first top-level JSON object.

    Returns an empty dict on failure.
    """
    try:
        return json.loads(text)
    except Exception:
        pass
    # crude extraction: find first '{' ... matching '}'
    start = text.find('{')
    if start != -1:
        # try last '}'
        end = text.rfind('}')
        if end != -1 and end > start:
            snippet = text[start:end+1]
            try:
                return json.loads(snippet)
            except Exception:
                # attempt to strip code fences
                snippet = re.sub(r"^```[a-zA-Z]*|```$", "", snippet.strip())
                try:
                    return json.loads(snippet)
                except Exception:
                    return {}
    return {}


def _ollama_suggest(trip, preferences: Dict[str, Any], max_items: int) -> Dict[str, Any]:
    """Call a local Ollama server at http://localhost:11434 (no API key).

    Enable by setting OLLAMA_MODEL (e.g., "llama3.1:8b").
    """
    model = os.getenv("OLLAMA_MODEL") or "llama3.1:8b"
    if not model:
        return None  # type: ignore[return-value]

    prompt = _build_prompt(trip, preferences, max_items)
    try:
        resp = requests.post(
            "http://127.0.0.1:11434/api/chat",
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": "You are a concise, structured travel planning assistant."},
                    {"role": "user", "content": prompt},
                ],
                "options": {"temperature": 0.7},
                "stream": False,
            },
            timeout=20,
        )
        if resp.status_code != 200:
            return {"activities": [], "provider": "ollama", "error": f"Ollama error {resp.status_code}"}
        data = resp.json()
        content = data.get("message", {}).get("content") or data.get("choices", [{}])[0].get("message", {}).get("content", "{}")
        parsed = _parse_json_loose(content)
        activities = parsed.get("activities") or []
        norm = []
        for a in activities[:max_items]:
            norm.append({
                "name": a.get("name"),
                "category": a.get("category"),
                "description": a.get("description"),
                "suggested_time": a.get("suggested_time"),
                "location": a.get("location") or trip.location,
                "cost_estimate": a.get("cost_estimate"),
                "tags": a.get("tags") or [],
            })
        return {"activities": norm, "provider": "ollama", "error": None}
    except Exception as exc:  # noqa: BLE001
        return {"activities": [], "provider": "ollama", "error": str(exc)}


def suggest_activities(trip, preferences: Dict[str, Any], max_items: int = 8) -> Dict[str, Any]:
    """Suggest activities via OpenAI if API key present; else fallback.

    Returns a dict: {"activities": [...], "provider": "openai"|"fallback", "error": str|None}
    """
    # Preferred provider order: explicit LLM_PROVIDER -> Ollama -> OpenAI -> fallback
    provider = (os.getenv("LLM_PROVIDER") or "").lower().strip()

    if provider == "ollama" or os.getenv("OLLAMA_MODEL"):
        res = _ollama_suggest(trip, preferences, max_items)
        if res and res.get("activities"):
            return res
        # if ollama failed, continue to OpenAI

    def _read_key_file():
        try:
            base = Path(__file__).resolve().parents[2]
            p = base / 'pitStop' / 'openai.key'
            if p.exists():
                return p.read_text(encoding='utf-8').strip()
        except Exception:
            return None
        return None

    api_key = os.getenv("OPENAI_API_KEY") or getattr(settings, 'OPENAI_API_KEY', None) or _read_key_file()
    if provider == "openai" and not api_key:
        return _fallback_suggestions(trip, preferences, max_items) | {"error": "OPENAI_API_KEY not set"}
    if not api_key and provider != "openai":
        # no explicit provider or not set; try fallback directly
        # (or continue to fallback after ollama failure)
        if not os.getenv("OPENAI_API_KEY"):
            return _fallback_suggestions(trip, preferences, max_items)

    prompt = _build_prompt(trip, preferences, max_items)

    try:
        base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        org = os.getenv("OPENAI_ORG") or os.getenv("OPENAI_ORGANIZATION") or getattr(settings, 'OPENAI_ORG', '')
        if org:
            headers["OpenAI-Organization"] = org
        project = os.getenv("OPENAI_PROJECT") or os.getenv("OPENAI_PROJECT_ID") or getattr(settings, 'OPENAI_PROJECT', '')
        if project:
            headers["OpenAI-Project"] = project

        resp = requests.post(
            f"{base_url.rstrip('/')}/chat/completions",
            headers=headers,
            json={
                "model": model,
                # response_format not supported on older models
                "messages": [
                    {"role": "system", "content": "You are a concise, structured travel planning assistant."},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.7,
            },
            timeout=20,
        )
        if resp.status_code != 200:
            detail = None
            try:
                detail = resp.json()
            except Exception:
                detail = resp.text[:300]
            return _fallback_suggestions(trip, preferences, max_items) | {"error": f"OpenAI error {resp.status_code}: {detail}"}
        data = resp.json()
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "{}")
        parsed = _parse_json_loose(content)
        activities = parsed.get("activities") or []
        # Normalize a bit
        norm = []
        for a in activities[:max_items]:
            norm.append({
                "name": a.get("name"),
                "category": a.get("category"),
                "description": a.get("description"),
                "suggested_time": a.get("suggested_time"),
                "location": a.get("location") or trip.location,
                "cost_estimate": a.get("cost_estimate"),
                "tags": a.get("tags") or [],
            })
        return {"activities": norm, "provider": "openai", "error": None}
    except Exception as exc:  # noqa: BLE001
        return _fallback_suggestions(trip, preferences, max_items) | {"error": str(exc)}

