from __future__ import annotations

from typing import Any, Dict, List, Optional

from recommender.config import Settings
from recommender.domain.models import RecommendationResponse
from recommender.infra.restaurant_store import RestaurantStore
from recommender.services.tracing import emit_recommendation_request_trace
from zomato_filter import filter_and_cap
from zomato_groq import groq_rank_candidates
from zomato_output import (
    experience_for_response,
    finalize_recommendation_items,
    merge_canonical_rows,
)
from zomato_prefs.models import ValidatedPreferences

__all__ = ["execute_recommendations"]


def _no_match_messages() -> List[str]:
    return [
        "No restaurants matched all filters (edge case F1).",
        "Try lowering min_rating, broadening location, or choosing different cuisines.",
    ]


def execute_recommendations(
    *,
    validated: ValidatedPreferences,
    settings: Settings,
    store: Optional[RestaurantStore],
    request_id: str,
    t0: float,
) -> RecommendationResponse:
    """
    Orchestrate filter → Groq → Phase 5 merge → Phase 6 trace (architecture §17.1 application layer).
    HTTP adapters validate preferences and map errors before calling this function.
    """
    restaurants = list(store.restaurants) if store is not None else []
    store_by_id: Dict[str, Any] = {r.id: r for r in restaurants}

    fr = filter_and_cap(
        validated,
        restaurants,
        max_candidates_k=settings.max_candidates_k,
    )

    if fr.match_count == 0:
        resp = RecommendationResponse(
            request_id=request_id,
            match_count=0,
            capped_to=None,
            sent_to_llm=0,
            results=[],
            degraded=False,
            experience=experience_for_response(match_count=0, degraded=False),
            messages=_no_match_messages()
            + [
                f"filter_ms={fr.filter_ms:.2f}",
                f"prefs: location={validated.location_display!r}, budget={validated.budget_band}, "
                f"cuisines={validated.cuisines}, min_rating>={validated.min_rating}",
            ],
        )
        emit_recommendation_request_trace(
            settings=settings,
            store=store,
            request_id=request_id,
            fr=fr,
            llm=None,
            resp=resp,
            sent_to_llm=0,
            t0=t0,
            store_by_id=store_by_id,
        )
        return resp

    candidates_unique = merge_canonical_rows(fr.candidates, store_by_id)

    llm = groq_rank_candidates(
        validated,
        candidates_unique,
        api_key=settings.groq_api_key,
        base_url=settings.groq_base_url,
        model=settings.groq_model,
        timeout_s=settings.llm_timeout_ms / 1000.0,
        max_retries=settings.llm_max_retries,
        temperature=settings.llm_temperature,
        prompt_template_version=settings.prompt_template_version,
        response_limit=validated.limit,
    )
    display_rows = merge_canonical_rows(llm.rows, store_by_id)
    results = finalize_recommendation_items(
        display_rows,
        llm.explanations,
        limit=validated.limit,
        escape_for_html_output=False,
        strip_contradictory_llm=True,
    )

    extra = (
        f"match_count={fr.match_count}, capped_to={fr.capped_to}, "
        f"returned={len(results)}, filter_ms={fr.filter_ms:.2f}, "
        f"llm_ms={llm.llm_ms:.2f}, llm_retry_count={llm.retry_count}, "
        f"prompt_template_version={settings.prompt_template_version!r}, "
        f"groq_model={settings.groq_model!r}."
    )

    resp = RecommendationResponse(
        request_id=request_id,
        match_count=fr.match_count,
        capped_to=fr.capped_to,
        sent_to_llm=len(candidates_unique),
        results=results,
        degraded=llm.degraded,
        experience=experience_for_response(match_count=fr.match_count, degraded=llm.degraded),
        messages=[extra],
    )
    emit_recommendation_request_trace(
        settings=settings,
        store=store,
        request_id=request_id,
        fr=fr,
        llm=llm,
        resp=resp,
        sent_to_llm=len(candidates_unique),
        t0=t0,
        store_by_id=store_by_id,
    )
    return resp
