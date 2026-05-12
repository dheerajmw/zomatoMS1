import uuid

from fastapi.testclient import TestClient

from recommender.runtime import IMPLEMENTATION_PHASE

_VALID_BODY = {
    "location": "Bangalore",
    "budget": "medium",
    "cuisines": ["Chinese"],
    "min_rating": 4.0,
    "notes": "family friendly",
    "limit": 5,
}


def test_health(client: TestClient) -> None:
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert data["phase"] == IMPLEMENTATION_PHASE
    assert data["restaurants_loaded"] == 0
    assert data["load_source"] == "disabled"


def test_recommendations_stub_shape(client: TestClient) -> None:
    r = client.post("/v1/recommendations", json=_VALID_BODY)
    assert r.status_code == 200
    data = r.json()
    uuid.UUID(data["request_id"])
    assert data["match_count"] == 0
    assert data["results"] == []
    assert data["degraded"] is False
    assert isinstance(data["messages"], list)
    assert data.get("experience") == "empty"


def test_recommendations_limit_enforced(client: TestClient) -> None:
    body = {**_VALID_BODY, "limit": 99}
    r = client.post("/v1/recommendations", json=body)
    assert r.status_code == 400
    err = r.json()["detail"]
    assert err["code"] == "VALIDATION_ERROR"
    assert "limit" in err["message"].lower()


def test_openapi_contains_schemas(client: TestClient) -> None:
    r = client.get("/openapi.json")
    assert r.status_code == 200
    spec = r.json()
    assert "/v1/recommendations" in spec["paths"]
    assert "RawRecommendationRequest" in spec["components"]["schemas"]
    assert "RecommendationResponse" in spec["components"]["schemas"]
