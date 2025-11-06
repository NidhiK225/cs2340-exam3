
AI suggestions (Gemini or OpenAI)
- Primary: set `GEMINI_API_KEY` (and optional `GEMINI_MODEL`, default `gemini-1.5-flash`).
- Alternative: set `OPENAI_API_KEY` (and optional `OPENAI_MODEL`).
- Optional: `LLM_PROVIDER=gemini|openai` to force provider. Without it, auto-detects: Gemini → OpenAI → local fallback.
- Navigate to `Trips → AI Suggestions` from your dashboard to generate ideas.
- Without a key, a local fallback provides generic suggestions.

LLM configuration
- Copy `.env.example` to `.env` (do not commit `.env`).
- Provide either `GEMINI_API_KEY` or `OPENAI_API_KEY` (or both). Set `LLM_PROVIDER` to prefer one.
- Open the Suggestions page to verify the provider badge.

Branding image
- Place your logo image at `pitStop/static/img/brand.png`. It appears in the navbar and on the home hero background.
# cs2340-exam3
