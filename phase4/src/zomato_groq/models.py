from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from zomato_phase1.models import Restaurant


@dataclass(frozen=True)
class LLMRankResult:
    """Ranked restaurants after Groq (or deterministic fallback)."""

    rows: List[Restaurant]
    explanations: Dict[str, str]
    degraded: bool
    llm_ms: float
    retry_count: int
