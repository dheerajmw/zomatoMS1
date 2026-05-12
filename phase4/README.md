# Phase 4 — LLM ranking via Groq (standalone package)

Implements [doc/phase-wise-architecture.md](../doc/phase-wise-architecture.md) §13: **Groq** OpenAI-compatible chat completions, **structured JSON** (`ordered_ids` + `explanations`), **retries**, and a **grounding guard** so only candidate ids are returned.

## Environment

| Variable | Default | Purpose |
|----------|---------|---------|
| `GROQ_API_KEY` | (empty) | If unset, API uses deterministic order + template explanations (`degraded=false`, no network). |
| `GROQ_MODEL` | `llama-3.1-8b-instant` | Groq model id |
| `GROQ_BASE_URL` | `https://api.groq.com/openai/v1` | Chat Completions base |

Timeouts / temperature / retries reuse app `LLM_*` settings in `recommender.config`.

## Public API

```python
from zomato_groq import groq_rank_candidates, LLMRankResult

result = groq_rank_candidates(
    prefs,
    candidates,
    api_key=settings.groq_api_key,
    base_url=settings.groq_base_url,
    model=settings.groq_model,
    timeout_s=settings.llm_timeout_ms / 1000,
    max_retries=settings.llm_max_retries,
    temperature=settings.llm_temperature,
    prompt_template_version=settings.prompt_template_version,
    response_limit=5,
)
# result.rows, result.explanations, result.degraded, result.llm_ms
```
