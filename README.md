# django-ai-starter

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![Django 5.1+](https://img.shields.io/badge/django-5.1+-green.svg)](https://djangoproject.com)
[![License: MIT](https://img.shields.io/badge/license-MIT-purple.svg)](LICENSE)

**Production-ready Django template with dual-mode LLM integration.**  
Runs on free local models (Ollama) in development, falls back to Claude API in production, and works in demo mode with zero configuration.

```
┌─────────────────────────────────────────────────┐
│                  Your Django App                │
│                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐  │
│  │ Lead     │  │ Summarize│  │ Classify     │  │
│  │ Scoring  │  │ Text     │  │ Intent       │  │
│  └────┬─────┘  └────┬─────┘  └──────┬───────┘  │
│       └──────────────┼───────────────┘          │
│                      ▼                          │
│              ┌──────────────┐                   │
│              │  SmartClient │                   │
│              │              │                   │
│              │  1. Ollama   │ ← free, local     │
│              │  2. Claude   │ ← paid, cloud     │
│              │  3. Demo     │ ← zero config     │
│              └──────┬───────┘                   │
│                     ▼                           │
│              ┌──────────────┐                   │
│              │  AIRequest   │ ← every call      │
│              │  (logging)   │   logged w/ cost   │
│              └──────────────┘                   │
└─────────────────────────────────────────────────┘
```

## Features

- **SmartClient** — Ollama → Claude API → demo fallback with automatic failover
- **Cost tracking** — every LLM call logged with token counts and USD cost
- **Pre-built tasks** — lead scoring, text summarization, intent classification, email drafting
- **Demo mode** — deterministic mock responses when no LLM is configured
- **Admin dashboard** — full Django admin for AI request logs
- **Example app** — interactive lead scorer with scoring UI

## Quick Start

```bash
# Clone and set up
git clone https://github.com/ruslandanelian/django-ai-starter.git
cd django-ai-starter
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Configure (optional — works without any LLM)
cp .env.example .env
# Edit .env to add Ollama URL or Claude API key

# Run
python manage.py migrate
python manage.py runserver
# Open http://localhost:8000 — submit a lead and see AI scoring
```

### With Ollama (free, local)

```bash
# Install Ollama: https://ollama.ai
ollama pull qwen3:8b
# Set in .env:
# OLLAMA_BASE_URL=http://localhost:11434
# OLLAMA_MODEL=qwen3:8b
```

### With Claude API (cloud)

```bash
pip install anthropic
# Set in .env:
# ANTHROPIC_API_KEY=sk-ant-...
# CLAUDE_MODEL=claude-sonnet-4-20250514
```

### Demo mode (no config)

Just run it. SmartClient returns deterministic mock responses for each task type.

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Interactive lead scoring demo |
| `/api/ai/score/` | POST | Score a lead (1-10) |
| `/api/ai/summarize/` | POST | Summarize text |
| `/api/ai/classify/` | POST | Classify user intent |
| `/api/ai/draft-email/` | POST | Draft an email reply |

### Example: Score a Lead

```bash
curl -X POST http://localhost:8000/api/ai/score/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Jane", "industry": "SaaS", "message": "Need AI integration ASAP"}'
```

```json
{"score": 9, "label": "hot", "reason": "Urgent need with clear purchase intent"}
```

## Adding Your Own Tasks

```python
# ai_core/tasks.py

def my_custom_task(data: str) -> dict:
    client = get_client()
    resp = client.complete(
        prompt=f"Analyze this: {data}",
        system="You are an expert analyst.",
        temperature=0.3,
    )
    _log("my_custom_task", f"Analyze this: {data}", resp)
    return {"analysis": resp.text}
```

The `_log()` helper saves every call to the database — you get cost tracking, latency metrics, and fallback visibility for free.

## Project Structure

```
django-ai-starter/
├── ai_core/                 # The reusable AI integration layer
│   ├── client.py            # SmartClient — the dual-mode LLM client
│   ├── models.py            # AIRequest logging model
│   ├── tasks.py             # Pre-built AI tasks
│   ├── views.py             # REST API endpoints
│   └── admin.py             # Django admin config
├── example_app/             # Demo application
│   ├── models.py            # Lead model
│   ├── views.py             # Submit + score leads
│   └── templates/           # Interactive demo UI
├── config/                  # Django project settings
│   ├── settings.py          # AI_CONFIG from env vars
│   └── urls.py              # URL routing
├── .env.example             # Environment template
└── requirements.txt
```

## Configuration

All config lives in `AI_CONFIG` in `settings.py`, populated from environment variables:

| Variable | Default | Description |
|---|---|---|
| `OLLAMA_BASE_URL` | *(empty)* | Ollama server URL (e.g. `http://localhost:11434`) |
| `OLLAMA_MODEL` | `qwen3:8b` | Ollama model name |
| `OLLAMA_TIMEOUT` | `30` | Ollama request timeout (seconds) |
| `ANTHROPIC_API_KEY` | *(empty)* | Claude API key |
| `CLAUDE_MODEL` | `claude-sonnet-4-20250514` | Claude model ID |
| `CLAUDE_TIMEOUT` | `60` | Claude request timeout (seconds) |

## License

MIT — see [LICENSE](LICENSE).

---

Built by [Ruslan Danelian](https://ruslandanelian.com)
