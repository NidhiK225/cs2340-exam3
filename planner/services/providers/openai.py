import json
import os
from pathlib import Path
from typing import Any, Dict, List

import time
import requests
from django.conf import settings


def _read_key_file() -> str | None:
    try:
        base = Path(__file__).resolve().parents[3]
        p = base / 'pitStop' / 'openai.key'
        if p.exists():
            return p.read_text(encoding='utf-8').strip()
    except Exception:
        return None
    return None


def suggest(trip, prompt: str, max_items: int = 8) -> Dict[str, Any]:
    """Call OpenAI Chat Completions to get JSON activities.

    Returns {"activities": [...], "provider": "openai", "error": str|None}
    """
    api_key = os.getenv("OPENAI_API_KEY") or getattr(settings, 'OPENAI_API_KEY', '') or _read_key_file()
    if not api_key:
        return {"activities": [], "provider": "openai", "error": "OPENAI_API_KEY not set"}

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

    try:
        # Tunable timeouts and retries
        timeout_s = float(os.getenv("LLM_TIMEOUT_SECONDS", "25"))
        retries = int(os.getenv("LLM_RETRIES", "2"))
        last_err = None
        for attempt in range(retries):
            try:
                resp = requests.post(
                    f"{base_url.rstrip('/')}/chat/completions",
                    headers=headers,
                    json={
                        "model": model,
                        "messages": [
                            {"role": "system", "content": "You are a concise, structured travel planning assistant."},
                            {"role": "user", "content": prompt},
                        ],
                        "temperature": 0.7,
                    },
                    timeout=timeout_s,
                )
                break
            except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError) as e:  # noqa: PERF203
                last_err = e
                # simple backoff
                time.sleep(1.5 * (attempt + 1))
                resp = None
        if resp is None:
            return {"activities": [], "provider": "openai", "error": f"OpenAI request failed: {last_err}"}
        if resp.status_code != 200:
            detail = None
            try:
                detail = resp.json()
            except Exception:
                detail = resp.text[:300]
            return {"activities": [], "provider": "openai", "error": f"OpenAI error {resp.status_code}: {detail}"}

        data = resp.json()
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "{}")
        try:
            parsed = json.loads(content)
        except Exception:
            # Allow fenced or extra text — attempt to slice first JSON object
            start = content.find('{')
            end = content.rfind('}')
            parsed = json.loads(content[start:end+1]) if start != -1 and end != -1 else {"activities": []}

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
        return {"activities": norm, "provider": "openai", "error": None}
    except Exception as exc:  # noqa: BLE001
        return {"activities": [], "provider": "openai", "error": str(exc)}
