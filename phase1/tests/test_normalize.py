from __future__ import annotations

import pytest

from zomato_phase1.normalize import (
    cost_to_band,
    parse_approx_cost,
    parse_rate,
    split_cuisines,
    stable_restaurant_id,
)


def test_parse_rate_slash_form() -> None:
    assert parse_rate("4.1/5") == pytest.approx(4.1)


def test_parse_rate_rejects_new() -> None:
    assert parse_rate("NEW") is None


def test_parse_approx_cost_digits() -> None:
    assert parse_approx_cost("800") == 800
    assert parse_approx_cost("₹1,200") == 1200


def test_cost_to_band() -> None:
    assert cost_to_band(400) == "low"
    assert cost_to_band(800) == "medium"
    assert cost_to_band(2000) == "high"


def test_split_cuisines() -> None:
    assert split_cuisines("Chinese, North Indian") == ["chinese", "north indian"]


def test_stable_restaurant_id_is_deterministic() -> None:
    row = {
        "name": "Jalsa",
        "address": "addr",
        "cuisines": "A, B",
        "rate": "4.1/5",
        "approx_cost(for two people)": "800",
        "location": "Banashankari",
        "listed_in(city)": "Banashankari",
    }
    a = stable_restaurant_id("rev1", row)
    b = stable_restaurant_id("rev1", row)
    assert a == b
    assert a.startswith("r_")
