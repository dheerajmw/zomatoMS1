from __future__ import annotations

from dataclasses import dataclass
from typing import List

from recommender.config import Settings
from zomato_phase1 import LoadMetadata, Restaurant, load_restaurants


@dataclass(frozen=True)
class RestaurantStore:
    """In-memory snapshot of restaurants (Phase 1)."""

    restaurants: List[Restaurant]
    meta: LoadMetadata


def build_restaurant_store(settings: Settings) -> RestaurantStore:
    """Load canonical restaurants using Phase 1 pipeline."""
    if settings.skip_dataset_load:
        meta = LoadMetadata(
            dataset_id=settings.hf_dataset,
            dataset_revision=None,
            source="disabled",
            raw_row_count=0,
            normalized_row_count=0,
            dropped_row_count=0,
            cache_path=settings.data_cache_path,
        )
        return RestaurantStore(restaurants=[], meta=meta)

    restaurants, meta = load_restaurants(
        dataset_id=settings.hf_dataset,
        cache_path=settings.data_cache_path,
        use_cache=True,
        write_cache_after_hf=True,
    )
    return RestaurantStore(restaurants=restaurants, meta=meta)
