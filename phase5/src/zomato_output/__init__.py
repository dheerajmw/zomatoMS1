"""Phase 5: merge, sanitization, and experience hints for recommendation output."""

from zomato_output.contradictions import explanation_contradicts_facts
from zomato_output.experience import experience_for_response
from zomato_output.merge import (
    DEFAULT_EXPLANATION_TEMPLATE,
    finalize_recommendation_items,
    merge_canonical_rows,
)
from zomato_output.sanitize import escape_for_html

__all__ = [
    "DEFAULT_EXPLANATION_TEMPLATE",
    "escape_for_html",
    "experience_for_response",
    "explanation_contradicts_facts",
    "finalize_recommendation_items",
    "merge_canonical_rows",
]
