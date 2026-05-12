"""Phase 1: ingest Hugging Face Zomato-style data into canonical Restaurant rows."""

from zomato_phase1.access import get_by_ids
from zomato_phase1.models import LoadMetadata, Restaurant
from zomato_phase1.pipeline import load_restaurants

__all__ = [
    "Restaurant",
    "LoadMetadata",
    "load_restaurants",
    "get_by_ids",
]
