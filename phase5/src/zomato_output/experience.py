from __future__ import annotations

from typing import Literal

ExperienceState = Literal["ok", "empty", "degraded"]


def experience_for_response(*, match_count: int, degraded: bool) -> ExperienceState:
    """Coarse UI state for clients (§14.2); validation errors remain HTTP-only."""
    if match_count <= 0:
        return "empty"
    if degraded:
        return "degraded"
    return "ok"
