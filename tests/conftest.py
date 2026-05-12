from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from recommender.api.main import create_app
from recommender.config import Settings, get_settings


@pytest.fixture(autouse=True)
def _force_test_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """BaseSettings reads process env; ensure tests never hit Hugging Face by default."""
    monkeypatch.setenv("SKIP_DATASET_LOAD", "true")


@pytest.fixture
def test_settings() -> Settings:
    return Settings(
        hf_dataset="fixture/dataset",
        data_cache_path=":memory:",
        groq_api_key=None,
        groq_model="llama-3.1-8b-instant",
        groq_base_url="https://api.groq.com/openai/v1",
        max_candidates_k=25,
        max_response_limit=10,
        llm_api_key=None,
        llm_model="stub-model",
        llm_timeout_ms=5000,
        llm_max_retries=0,
        llm_temperature=0.0,
        prompt_template_version="v0",
        skip_dataset_load=True,
        max_notes_length=2000,
        cors_origins=None,
        _env_file=None,
    )


@pytest.fixture
def client(test_settings: Settings) -> TestClient:
    app = create_app()
    app.state.settings_override = test_settings
    app.dependency_overrides[get_settings] = lambda: test_settings
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
    if hasattr(app.state, "settings_override"):
        del app.state.settings_override
    get_settings.cache_clear()
