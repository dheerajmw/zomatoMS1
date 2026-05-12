from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field

CostBand = Literal["low", "medium", "high"]


class Restaurant(BaseModel):
    """Canonical restaurant row (architecture §5.1, adapted to this dataset)."""

    id: str
    name: str
    city: str
    area: str = Field(description="Neighborhood / locality from Zomato `location`.")
    cuisines: List[str]
    rating: float = Field(..., ge=0, le=5)
    cost_band: CostBand
    approx_cost_for_two: Optional[int] = Field(
        default=None,
        description="Parsed rupee amount from `approx_cost(for two people)` when available.",
    )
    address: str = ""
    description: str = Field(
        default="",
        description="Truncated text for LLM context (e.g. reviews snippet).",
    )
    raw: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional raw row subset for debugging; omit in production APIs.",
    )


class LoadMetadata(BaseModel):
    """Diagnostics for a load run (architecture §10.1)."""

    dataset_id: str
    dataset_revision: Optional[str] = None
    source: Literal["huggingface", "parquet_cache", "disabled"] = "huggingface"
    raw_row_count: int = 0
    normalized_row_count: int = 0
    dropped_row_count: int = 0
    cache_path: Optional[str] = None
