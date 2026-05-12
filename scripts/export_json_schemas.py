#!/usr/bin/env python3
"""Emit JSON Schema for API contracts into config/schemas/."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "phase1" / "src"))
sys.path.insert(0, str(ROOT / "phase2" / "src"))
sys.path.insert(0, str(ROOT / "phase3" / "src"))
sys.path.insert(0, str(ROOT / "phase4" / "src"))
sys.path.insert(0, str(ROOT / "phase5" / "src"))
sys.path.insert(0, str(ROOT / "phase6" / "src"))

from recommender.domain.models import (  # noqa: E402
    RecommendationItem,
    RecommendationResponse,
)
from zomato_prefs.models import (  # noqa: E402
    RawRecommendationRequest,
    ValidatedPreferences,
)


def main() -> None:
    out = ROOT / "config" / "schemas"
    out.mkdir(parents=True, exist_ok=True)
    (out / "raw-recommendation-request.json").write_text(
        json.dumps(RawRecommendationRequest.model_json_schema(), indent=2) + "\n",
        encoding="utf-8",
    )
    (out / "validated-preferences.json").write_text(
        json.dumps(ValidatedPreferences.model_json_schema(), indent=2) + "\n",
        encoding="utf-8",
    )
    (out / "recommendation-item.json").write_text(
        json.dumps(RecommendationItem.model_json_schema(), indent=2) + "\n",
        encoding="utf-8",
    )
    (out / "recommendation-response.json").write_text(
        json.dumps(RecommendationResponse.model_json_schema(), indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote schemas under {out}")


if __name__ == "__main__":
    main()
