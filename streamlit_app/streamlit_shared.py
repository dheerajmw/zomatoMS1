"""Shared helpers for Streamlit apps: repo path bootstrap + POST /v1/recommendations (HTTP or embedded ASGI)."""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path
from typing import Any

from urllib.parse import urlparse

import httpx

SESSION_API_OVERRIDE = "api_base_url_override"
SESSION_USE_EMBEDDED = "use_embedded_fastapi"


def ensure_repo_src_on_path() -> None:
    root = Path(__file__).resolve().parent.parent
    for rel in (
        "src",
        "phase1/src",
        "phase2/src",
        "phase3/src",
        "phase4/src",
        "phase5/src",
        "phase6/src",
    ):
        p = root / rel
        if p.is_dir():
            s = str(p)
            if s not in sys.path:
                sys.path.insert(0, s)


ensure_repo_src_on_path()


def normalize_api_base(raw: str) -> str:
    u = (raw or "").strip().rstrip("/")
    if not u:
        return "http://127.0.0.1:8000"
    if u.startswith(("http://", "https://")):
        return u
    low = u.lower()
    if low.startswith("localhost") or low.startswith("127.") or low.startswith("0.0.0.0") or low.startswith("[::1]"):
        return "http://" + u
    return "https://" + u


def resolve_api_base_url(
    *,
    sidebar_override: str,
    secrets_api_base: str | None,
    env_api_base: str | None,
) -> str:
    o = (sidebar_override or "").strip()
    if o:
        return normalize_api_base(o)
    if secrets_api_base:
        return normalize_api_base(str(secrets_api_base).strip())
    e = (env_api_base or "").strip()
    if e:
        return normalize_api_base(e)
    return "http://127.0.0.1:8000"


def host_is_loopback(url: str) -> bool:
    try:
        host = (urlparse(url).hostname or "").lower()
    except Exception:
        return False
    return host in ("localhost", "127.0.0.1", "0.0.0.0", "::1")


def connect_error_help(base: str) -> str:
    if host_is_loopback(base):
        return (
            f"**Could not connect to `{base}`.**\n\n"
            "**Quick fix:** Turn **ON** *Run API inside Streamlit (embedded)* — "
            "FastAPI runs in-process (no Uvicorn). Repo root must contain `pyproject.toml`.\n\n"
            "**Or** run `uvicorn recommender.api.main:app --host 127.0.0.1 --port 8000` and turn embedded **OFF**."
        )
    return f"**Could not connect to `{base}`.** Check the URL or use embedded mode."


async def post_via_asgi_async(payload: dict[str, Any]) -> tuple[int, Any]:
    ensure_repo_src_on_path()
    from recommender.api.main import app as asgi_app

    transport = httpx.ASGITransport(app=asgi_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://streamlit.embedded", timeout=180.0) as client:
        r = await client.post(
            "/v1/recommendations",
            json=payload,
            headers={"Accept": "application/json"},
        )
    try:
        body = r.json()
    except Exception:
        body = {"raw": r.text[:2000]}
    return r.status_code, body


def post_via_asgi(payload: dict[str, Any]) -> tuple[int, Any]:
    try:
        return asyncio.run(post_via_asgi_async(payload))
    except ImportError as e:
        return -1, {"_error": "import", "detail": str(e)}
    except RuntimeError as e:
        if "asyncio.run()" in str(e) or "cannot be called from a running event loop" in str(e).lower():
            return -1, {"_error": "async_loop", "detail": str(e)}
        raise
    except Exception as e:
        return -1, {"_error": "asgi", "detail": str(e)}


def post_recommendations_http(payload: dict[str, Any], api_base: str) -> tuple[int, Any]:
    url = f"{api_base.rstrip('/')}/v1/recommendations"
    try:
        with httpx.Client(timeout=120.0, follow_redirects=True) as client:
            r = client.post(url, json=payload, headers={"Accept": "application/json"})
    except httpx.ConnectError:
        return -1, {"_error": "connect"}
    except httpx.TimeoutException:
        return -1, {"_error": "timeout"}
    except httpx.RequestError:
        return -1, {"_error": "request"}
    try:
        body = r.json()
    except Exception:
        body = {"raw": r.text[:2000]}
    return r.status_code, body


def post_recommendations(payload: dict[str, Any], *, embedded: bool, api_base: str) -> tuple[int, Any]:
    if embedded:
        return post_via_asgi(payload)
    return post_recommendations_http(payload, api_base)


def initial_embedded_from_secrets(secrets_obj) -> bool:
    try:
        v = secrets_obj["USE_EMBEDDED_FASTAPI"]
    except Exception:
        return True
    if isinstance(v, str):
        return v.strip().lower() not in ("false", "0", "no", "")
    return bool(v)


def resolve_frontend_url(secrets_obj) -> str:
    try:
        v = secrets_obj["FRONTEND_URL"]
        if v:
            return str(v).strip().rstrip("/")
    except Exception:
        pass
    return os.environ.get("FRONTEND_URL", "").strip().rstrip("/")
