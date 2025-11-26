import json
import os
from typing import Any, Dict, List

import time
import requests


def suggest(trip, prompt: str, max_items: int = 8) -> Dict[str, Any]:
    """Call Google Gemini (Generative Language API) to get JSON activities.

    Env vars:
      - GEMINI_API_KEY (required)
      - GEMINI_MODEL (default: gemini-1.5-flash)

    Returns {"activities": [...], "provider": "gemini", "error": str|None}
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {"activities": [], "provider": "gemini", "error": "GEMINI_API_KEY not set"}

    model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    base = os.getenv("GEMINI_BASE_URL", "https://generativelanguage.googleapis.com")
    url = f"{base.rstrip('/')}/v1beta/models/{model}:generateContent?key={api_key}"

    body = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "text": (
                            "You are a travel planner assistant. Respond ONLY with a strict JSON object.\n"
                            "Schema: {\n  \"activities\": [\n    {\n      \"name\": str, \"category\": str, \"description\": str, \"suggested_time\": str, \"location\": str, \"cost_estimate\": str, \"tags\": [str]\n    }\n  ]\n}\n\n"
                            + prompt
                        )
                    }
                ],
            }
        ],
        "generationConfig": {"temperature": 0.7},
    }

    try:
        timeout_s = float(os.getenv("LLM_TIMEOUT_SECONDS", "25"))
        retries = int(os.getenv("LLM_RETRIES", "2"))
        last_err = None
        for attempt in range(retries):
            try:
                resp = requests.post(url, json=body, timeout=timeout_s)
                break
            except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError) as e:  # noqa: PERF203
                last_err = e
                time.sleep(1.5 * (attempt + 1))
                resp = None
        if resp is None:
            return {"activities": [], "provider": "gemini", "error": f"Gemini request failed: {last_err}"}
        if resp.status_code != 200:
            detail = None
            try:
                detail = resp.json()
            except Exception:
                detail = resp.text[:300]
            return {"activities": [], "provider": "gemini", "error": f"Gemini error {resp.status_code}: {detail}"}

        data = resp.json()
        # Gemini text output lives at candidates[0].content.parts[0].text
        text = (
            ((data.get("candidates") or [{}])[0]
             .get("content", {})
             .get("parts", [{}])[0]
             .get("text", "{}"))
        )
        try:
            parsed = json.loads(text)
        except Exception:
            # try to extract first JSON object
            start = text.find("{")
            end = text.rfind("}")
            parsed = json.loads(text[start:end+1]) if start != -1 and end != -1 else {"activities": []}

        activities = parsed.get("activities") or []
        norm: List[Dict[str, Any]] = []
        for a in activities[:max_items]:
            norm.append({
                "name": a.get("name"),
                "category": a.get("category"),
                "description": a.get("description"),
                "suggested_time": a.get("suggested_time"),
                "location": a.get("location") or getattr(trip, 'location', None),
                "cost_estimate": a.get("cost_estimate"),
                "tags": a.get("tags") or [],
            })
        return {"activities": norm, "provider": "gemini", "error": None}
    except Exception as exc:  # noqa: BLE001
        return {"activities": [], "provider": "gemini", "error": str(exc)}
