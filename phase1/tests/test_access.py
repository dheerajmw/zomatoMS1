from __future__ import annotations

from zomato_phase1.access import get_by_ids
from zomato_phase1.transform import normalize_row


def test_get_by_ids_preserves_order() -> None:
    a = normalize_row("r", {"name": "A", "rate": "4/5", "cuisines": "X", "approx_cost(for two people)": "600", "location": "L", "listed_in(city)": "L", "address": "addr"})
    b = normalize_row("r", {"name": "B", "rate": "3/5", "cuisines": "Y", "approx_cost(for two people)": "600", "location": "L", "listed_in(city)": "L", "address": "addr2"})
    assert a is not None and b is not None
    rows = [a, b]
    out = get_by_ids(rows, [b.id, a.id, "missing"])
    assert [x.id for x in out] == [b.id, a.id]
