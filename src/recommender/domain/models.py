from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, Field

Budget = Literal["low", "medium", "high"]


class RecommendationItem(BaseModel):
    """Single result row (facts + optional explanation)."""

    id: str
    rank: int = Field(..., ge=1)
    name: str
    city: str
    cuisines: List[str]
    rating: float
    cost_band: Budget
    explanation: str


class RecommendationResponse(BaseModel):
    """POST /v1/recommendations response envelope (architecture §6)."""

    request_id: str
    match_count: int = Field(..., ge=0)
    capped_to: Optional[int] = Field(
        default=None,
        description="If match_count exceeded internal cap before LLM, this is the cap applied.",
    )
    sent_to_llm: Optional[int] = Field(
        default=None,
        description="Rows included in the LLM payload for this request (Phase 4+).",
    )
    results: List[RecommendationItem]
    degraded: bool = False
    experience: Optional[Literal["ok", "empty", "degraded"]] = Field(
        default=None,
        description="Phase 5 coarse UI state: ok | empty | degraded (architecture §14.2).",
    )
    messages: List[str] = Field(default_factory=list)
