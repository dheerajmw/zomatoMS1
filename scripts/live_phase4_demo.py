#!/usr/bin/env python3
"""
Live Phase 4 smoke: load the real dataset (unless SKIP_DATASET_LOAD=1), POST preferences,
print top-N results (Groq explanations when GROQ_API_KEY is set).

Example (from repo root):
  export GROQ_API_KEY=...
  PYTHONPATH=src:phase1/src:phase2/src:phase3/src:phase4/src python3 scripts/live_phase4_demo.py
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for p in ("src", "phase1/src", "phase2/src", "phase3/src", "phase4/src"):
    sys.path.insert(0, str(ROOT / p))

from fastapi.testclient import TestClient  # noqa: E402

from recommender.api.main import create_app  # noqa: E402
from recommender.config import Settings, get_settings  # noqa: E402


def main() -> None:
    os.chdir(ROOT)
    get_settings.cache_clear()
    settings = Settings()
    app = create_app()
    app.state.settings_override = settings
    app.dependency_overrides[get_settings] = lambda: settings

    import argparse

    p = argparse.ArgumentParser(description="Live Phase 4 POST /v1/recommendations smoke test.")
    p.add_argument("--location", default="Bhanapura", help="User location (must match dataset catalog unless --fallback)")
    p.add_argument("--budget", default="1500")
    p.add_argument("--min-rating", type=float, default=4.0)
    p.add_argument("--limit", type=int, default=5)
    p.add_argument(
        "--fallback",
        default="Banashankari",
        help="If primary location returns 400 (unknown catalog), retry with this location and a note. "
        "Use empty string to disable.",
    )
    p.add_argument(
        "--output",
        "-o",
        default=None,
        help="Write full envelope (request + response metadata) as JSON to this path.",
    )
    args = p.parse_args()

    def post(loc: str, notes: str | None) -> tuple[int, dict]:
        body = {
            "location": loc,
            "budget": args.budget,
            "cuisines": ["North Indian", "Indian", "Chinese", "Fast Food", "Cafe"],
            "min_rating": args.min_rating,
            "limit": args.limit,
            "notes": notes,
        }
        with TestClient(app) as client:
            r = client.post("/v1/recommendations", json=body)
        payload = r.json() if r.headers.get("content-type", "").startswith("application/json") else {"raw": r.text}
        return r.status_code, payload

    notes = None
    used = args.location
    status, response = post(used, notes)
    fb = (args.fallback or "").strip()
    if status == 400 and fb:
        detail = response.get("detail") if isinstance(response, dict) else {}
        if isinstance(detail, dict) and "location" in (detail.get("message") or "").lower():
            used = fb
            notes = (
                f"Original location {args.location!r} is not in this dataset's city/area catalog "
                f"(Zomato metros only). Retried with catalog location {fb!r} for the same "
                "budget, min_rating, and limit."
            )
            status, response = post(used, notes)

    request_body = {
        "location": used,
        "budget": args.budget,
        "cuisines": ["North Indian", "Indian", "Chinese", "Fast Food", "Cafe"],
        "min_rating": args.min_rating,
        "limit": args.limit,
        "notes": notes,
    }

    out = {
        "request": request_body,
        "location_used": used,
        "status_code": status,
        "groq_configured": bool((settings.groq_api_key or "").strip()),
        "response": response,
    }
    text = json.dumps(out, indent=2, ensure_ascii=False)
    if args.output:
        outp = Path(args.output)
        outp.parent.mkdir(parents=True, exist_ok=True)
        outp.write_text(text + "\n", encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
