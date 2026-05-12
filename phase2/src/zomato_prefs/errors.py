from __future__ import annotations

from typing import List, Optional


class PreferenceValidationError(ValueError):
    """Raised when preference input fails Phase 2 validation (HTTP 400)."""

    def __init__(
        self,
        message: str,
        *,
        code: str = "VALIDATION_ERROR",
        allowed: Optional[List[str]] = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.allowed = allowed
