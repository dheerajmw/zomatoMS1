from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

import pytest

import zomato_phase1.pipeline as pipeline
from zomato_phase1.pipeline import load_restaurants


def _sample_rows() -> List[Dict[str, Any]]:
    return [
        {
            "name": "Jalsa",
            "rate": "4.1/5",
            "cuisines": "North Indian, Mughlai, Chinese",
            "approx_cost(for two people)": "800",
            "location": "Banashankari",
            "listed_in(city)": "Banashankari",
            "address": "942, 21st Main Road, Bangalore",
            "reviews_list": "[('Rated 4.0', 'ok')]",
        }
    ]


def test_load_restaurants_offline(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    def fake_hf(
        dataset_id: str,
        *,
        split: str = "train",
        max_rows: Optional[int] = None,
    ) -> Tuple[List[Dict[str, Any]], str]:
        rows = _sample_rows()
        if max_rows is not None:
            rows = rows[:max_rows]
        return rows, "test-rev"

    monkeypatch.setattr(pipeline, "load_rows_from_hf", fake_hf)

    restaurants, meta = load_restaurants(
        dataset_id="fixture/dataset",
        cache_path=str(tmp_path / "cache.parquet"),
        use_cache=False,
        write_cache_after_hf=False,
    )
    assert len(restaurants) == 1
    assert meta.normalized_row_count == 1
    assert meta.raw_row_count == 1
    assert meta.dropped_row_count == 0
    assert meta.source == "huggingface"


def test_load_restaurants_raises_on_empty(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    monkeypatch.setattr(pipeline, "load_rows_from_hf", lambda *a, **k: ([], "x"))
    with pytest.raises(ValueError):
        load_restaurants(
            dataset_id="fixture/dataset",
            cache_path=str(tmp_path / "cache.parquet"),
            use_cache=False,
            write_cache_after_hf=False,
        )
