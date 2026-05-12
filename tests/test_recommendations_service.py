from __future__ import annotations

import time
import uuid

from recommender.config import Settings
from recommender.infra.restaurant_store import RestaurantStore
from recommender.services.recommendations import execute_recommendations
from zomato_phase1 import LoadMetadata
from zomato_prefs.models import ValidatedPreferences


def test_execute_recommendations_f1_empty_store() -> None:
    """Architecture §17.1 orchestration: empty store yields F1-style response + experience empty."""
    meta = LoadMetadata(
        dataset_id="fixture",
        dataset_revision=None,
        source="disabled",
        raw_row_count=0,
        normalized_row_count=0,
        dropped_row_count=0,
        cache_path=":memory:",
    )
    store = RestaurantStore(restaurants=[], meta=meta)
    settings = Settings(
        hf_dataset="fixture",
        data_cache_path=":memory:",
        groq_api_key=None,
        groq_model="stub",
        groq_base_url="https://example.invalid",
        max_candidates_k=25,
        max_response_limit=10,
        llm_api_key=None,
        llm_model="stub",
        llm_timeout_ms=5000,
        llm_max_retries=0,
        llm_temperature=0.0,
        prompt_template_version="v0",
        skip_dataset_load=True,
        max_notes_length=2000,
        cors_origins=None,
        _env_file=None,
    )
    prefs = ValidatedPreferences(
        location_display="Testville",
        location_normalized="testville",
        budget_band="low",
        cuisines=["indian"],
        min_rating=0.0,
        notes=None,
        limit=3,
    )
    rid = str(uuid.uuid4())
    out = execute_recommendations(
        validated=prefs,
        settings=settings,
        store=store,
        request_id=rid,
        t0=time.perf_counter(),
    )
    assert out.request_id == rid
    assert out.match_count == 0
    assert out.results == []
    assert out.experience == "empty"
    assert any("No restaurants matched" in m for m in out.messages)
