from __future__ import annotations

from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Environment-backed configuration (see `.env.example` and architecture §9.2)."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    hf_dataset: str = Field(
        default="ManikaSaini/zomato-restaurant-recommendation",
        validation_alias="HF_DATASET",
    )
    groq_api_key: Optional[str] = Field(default=None, validation_alias="GROQ_API_KEY")
    groq_model: str = Field(default="llama-3.1-8b-instant", validation_alias="GROQ_MODEL")
    groq_base_url: str = Field(
        default="https://api.groq.com/openai/v1",
        validation_alias="GROQ_BASE_URL",
    )
    data_cache_path: str = Field(default="./data/zomato.parquet", validation_alias="DATA_CACHE_PATH")

    max_candidates_k: int = Field(default=25, ge=1, validation_alias="MAX_CANDIDATES_K")
    max_response_limit: int = Field(default=10, ge=1, validation_alias="MAX_RESPONSE_LIMIT")

    llm_api_key: Optional[str] = Field(default=None, validation_alias="LLM_API_KEY")
    llm_model: str = Field(default="gpt-4o-mini", validation_alias="LLM_MODEL")
    llm_timeout_ms: int = Field(default=20_000, ge=1000, validation_alias="LLM_TIMEOUT_MS")
    llm_max_retries: int = Field(default=2, ge=0, le=10, validation_alias="LLM_MAX_RETRIES")
    llm_temperature: float = Field(default=0.3, ge=0, le=2, validation_alias="LLM_TEMPERATURE")
    prompt_template_version: str = Field(default="v0", validation_alias="PROMPT_TEMPLATE_VERSION")
    skip_dataset_load: bool = Field(default=False, validation_alias="SKIP_DATASET_LOAD")
    max_notes_length: int = Field(default=2000, ge=100, le=20_000, validation_alias="MAX_NOTES_LENGTH")

    cors_origins: Optional[str] = Field(
        default=None,
        validation_alias="CORS_ORIGINS",
        description="Comma-separated origins for browser clients (e.g. Next.js dev server).",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
