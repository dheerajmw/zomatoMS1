# Restaurant recommender — Next.js UI (architecture §17.2)

First-party browser client for `POST /v1/recommendations`. Implements **§14.2** states: loading, empty (**F1**), degraded (**L1**), validation (**U1**). Explanations are rendered as **plain text** (React text nodes) for **M4** — no `dangerouslySetInnerHTML`.

## Prerequisites

1. **API** running (e.g. `uvicorn recommender.api.main:app --reload` or `zomato-serve`) on port **8000** by default.
2. **CORS** — in the API `.env` set:

   `CORS_ORIGINS=http://localhost:3000`

   (comma-separate multiple origins if needed.)

## Run

```bash
cd frontend
npm install
cp .env.local.example .env.local   # optional; defaults to http://127.0.0.1:8000
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Env

| Variable | Purpose |
|----------|---------|
| `NEXT_PUBLIC_API_BASE_URL` | Base URL of the FastAPI service (no trailing slash). Default in code: `http://127.0.0.1:8000`. |
