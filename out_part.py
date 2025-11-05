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

