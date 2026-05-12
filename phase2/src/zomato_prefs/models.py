from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

CostBand = Literal["low", "medium", "high"]


class RawRecommendationRequest(BaseModel):
    """Wire format for ``POST /v1/recommendations`` (flexible ``budget`` string)."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="ignore")

    location: str = Field(..., min_length=1, max_length=160)
    budget: str = Field(..., min_length=1, max_length=40)
    cuisines: List[str] = Field(..., min_length=1, max_length=30)
    min_rating: float = Field(..., ge=0, le=5)
    notes: Optional[str] = Field(default=None, max_length=8000)
    limit: int = Field(default=5, ge=1, le=500)


class ValidatedPreferences(BaseModel):
    """Canonical, Phase-2–validated preferences for filtering (Phase 3+)."""

    model_config = ConfigDict(frozen=True)

    location_display: str
    location_normalized: str
    budget_band: CostBand
    cuisines: List[str]
    min_rating: float
    notes: Optional[str]
    limit: int
