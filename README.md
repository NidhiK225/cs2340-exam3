
AI suggestions
- Set `OPENAI_API_KEY` in your environment to enable LLM-powered trip suggestions.
- Navigate to `Trips → AI Suggestions` from your dashboard to generate ideas.
- Without an API key, a local fallback provides generic suggestions.

LLM configuration
- Copy `.env.example` to `.env` (do not commit `.env`). Options:
  - OpenAI: set `OPENAI_API_KEY=...` and optionally `OPENAI_MODEL` and `OPENAI_BASE_URL`.
  - Ollama (no key): install Ollama, pull a model (e.g., `ollama pull llama3.1:8b`), set `OLLAMA_MODEL=llama3.1:8b`.
  - Optional: `LLM_PROVIDER=openai` or `LLM_PROVIDER=ollama` to force selection.
- Test from CLI: `python manage.py check_llm` to confirm provider and sample.

Branding image
- Place your logo image at `pitStop/static/img/brand.png`. It appears in the navbar and on the home hero background.
# cs2340-exam3
