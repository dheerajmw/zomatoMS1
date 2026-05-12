from __future__ import annotations

from typing import Dict, List, Mapping, Sequence

from recommender.domain.models import RecommendationItem
from zomato_phase1.models import Restaurant

from zomato_output.contradictions import explanation_contradicts_facts
from zomato_output.sanitize import escape_for_html

DEFAULT_EXPLANATION_TEMPLATE = "Ranked by rating and match to your preferences."


def merge_canonical_rows(
    rows: Sequence[Restaurant],
    store_by_id: Mapping[str, Restaurant],
) -> List[Restaurant]:
    """
    §14.1: For each ``id`` in order, prefer the canonical row from the same snapshot dict.

    Deduplicates by ``id`` while preserving first-seen order.
    """
    seen: set[str] = set()
    out: List[Restaurant] = []
    for r in rows:
        rid = r.id
        if rid in seen:
            continue
        seen.add(rid)
        canonical = store_by_id.get(rid, r)
        out.append(canonical)
    return out


def _pick_explanation(
    restaurant: Restaurant,
    explanations: Mapping[str, str],
    *,
    apply_l7: bool,
) -> str:
    raw = (explanations.get(restaurant.id) or "").strip()
    if not raw:
        return DEFAULT_EXPLANATION_TEMPLATE
    if apply_l7 and explanation_contradicts_facts(raw, restaurant):
        return DEFAULT_EXPLANATION_TEMPLATE
    return raw


def finalize_recommendation_items(
    rows: Sequence[Restaurant],
    explanations: Mapping[str, str],
    *,
    limit: int,
    escape_for_html_output: bool = False,
    strip_contradictory_llm: bool = True,
) -> List[RecommendationItem]:
    """
    Build API rows: L6 default text, optional L7 replacement, optional M4 escaping.

    ``explanations`` is read-only; contradictions are replaced with the neutral template.
    """
    expl_map: Dict[str, str] = dict(explanations)
    out: List[RecommendationItem] = []
    cap = max(0, int(limit))
    for i, r in enumerate(rows[:cap], start=1):
        expl = _pick_explanation(r, expl_map, apply_l7=strip_contradictory_llm)
        if escape_for_html_output:
            expl = escape_for_html(expl)
        out.append(
            RecommendationItem(
                id=r.id,
                rank=i,
                name=r.name,
                city=r.city,
                cuisines=list(r.cuisines),
                rating=float(r.rating),
                cost_band=r.cost_band,
                explanation=expl,
            )
        )
    return out
