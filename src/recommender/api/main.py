from __future__ import annotations

import time
import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any, Dict

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from recommender.config import Settings, get_settings
from recommender.domain.models import RecommendationResponse
from recommender.runtime import IMPLEMENTATION_PHASE
from recommender.services.recommendations import execute_recommendations
from zomato_prefs import PreferenceValidationError, RawRecommendationRequest, validate_preferences


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Phase 1 store through Phase 6 trace logging in recommendations handler."""
    settings = getattr(app.state, "settings_override", None) or get_settings()
    from recommender.infra.restaurant_store import build_restaurant_store
    from zomato_prefs.catalog import city_area_tokens_from_pairs, merge_metro_tokens, rating_bounds_from_ratings

    store = build_restaurant_store(settings)
    app.state.restaurant_store = store

    if store.restaurants:
        app.state.rating_bounds = rating_bounds_from_ratings(r.rating for r in store.restaurants)
        pairs = ((r.city, r.area) for r in store.restaurants)
        app.state.catalog_tokens = merge_metro_tokens(city_area_tokens_from_pairs(pairs))
    else:
        app.state.rating_bounds = (0.0, 5.0)
        app.state.catalog_tokens = merge_metro_tokens(frozenset())

    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="Restaurant Recommender",
        version="0.1.0",
        description=(
            "Zomato-inspired restaurant recommendations. "
            "Phases 0–6 per doc/phase-wise-architecture.md (through trace logging & runbook)."
        ),
        lifespan=lifespan,
    )

    _cors = Settings()
    _origins = [o.strip() for o in (_cors.cors_origins or "").split(",") if o.strip()]
    if _origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=_origins,
            allow_credentials=False,
            allow_methods=["GET", "POST", "OPTIONS"],
            allow_headers=["*"],
        )

    @app.get("/health", tags=["ops"])
    def health(request: Request) -> Dict[str, Any]:
        store = getattr(request.app.state, "restaurant_store", None)
        if store is None:
            return {
                "status": "ok",
                "phase": IMPLEMENTATION_PHASE,
                "restaurants_loaded": 0,
                "dataset_load": "pending",
            }
        meta = store.meta
        return {
            "status": "ok",
            "phase": IMPLEMENTATION_PHASE,
            "restaurants_loaded": len(store.restaurants),
            "dataset_id": meta.dataset_id,
            "dataset_revision": meta.dataset_revision,
            "load_source": meta.source,
            "raw_row_count": meta.raw_row_count,
            "normalized_row_count": meta.normalized_row_count,
            "dropped_row_count": meta.dropped_row_count,
        }

    @app.post(
        "/v1/recommendations",
        response_model=RecommendationResponse,
        tags=["recommendations"],
        summary="Recommend restaurants (through Phase 6 structured trace logging)",
    )
    def create_recommendations(
        raw: RawRecommendationRequest,
        request: Request,
        settings: Settings = Depends(get_settings),
    ) -> RecommendationResponse:
        rating_bounds = getattr(request.app.state, "rating_bounds", (0.0, 5.0))
        catalog_tokens = getattr(request.app.state, "catalog_tokens", None)

        try:
            validated = validate_preferences(
                raw,
                rating_bounds=rating_bounds,
                max_response_limit=settings.max_response_limit,
                max_notes_length=settings.max_notes_length,
                catalog_tokens=catalog_tokens,
            )
        except PreferenceValidationError as exc:
            raise HTTPException(
                status_code=400,
                detail={
                    "code": exc.code,
                    "message": exc.message,
                    "allowed": exc.allowed,
                },
            ) from exc

        request_id = str(uuid.uuid4())
        t0 = time.perf_counter()
        store = getattr(request.app.state, "restaurant_store", None)
        return execute_recommendations(
            validated=validated,
            settings=settings,
            store=store,
            request_id=request_id,
            t0=t0,
        )

    return app


app = create_app()


def run() -> None:
    """Entry point for `python -m recommender.api.main` (dev)."""
    import uvicorn

    uvicorn.run("recommender.api.main:app", host="0.0.0.0", port=8000, reload=False)


if __name__ == "__main__":
    run()
