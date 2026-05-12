from __future__ import annotations

import pytest

from zomato_phase1.transform import normalize_row, normalize_rows


def _good_row() -> dict:
    return {
        "name": "Jalsa",
        "rate": "4.1/5",
        "cuisines": "North Indian, Mughlai, Chinese",
        "approx_cost(for two people)": "800",
        "location": "Banashankari",
        "listed_in(city)": "Banashankari",
        "address": "942, 21st Main Road, Bangalore",
        "reviews_list": "[('Rated 4.0', 'ok')]",
    }


def test_normalize_row_keeps_valid_row() -> None:
    r = normalize_row("rev1", _good_row())
    assert r is not None
    assert r.name == "Jalsa"
    assert r.rating == pytest.approx(4.1)
    assert r.cost_band == "medium"
    assert "north indian" in r.cuisines


def test_normalize_row_drops_bad_rating() -> None:
    row = _good_row()
    row["rate"] = "NEW"
    assert normalize_row("rev1", row) is None


def test_normalize_rows_counts_drops() -> None:
    rows = [_good_row(), {**_good_row(), "name": "X", "rate": "NEW"}]
    kept, raw, dropped = normalize_rows("rev1", rows)
    assert raw == 2
    assert dropped == 1
    assert len(kept) == 1
