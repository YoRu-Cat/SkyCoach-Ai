"""Security helpers for the FastAPI backend.

This module bundles the cross-cutting concerns that protect the API
endpoints:

* :func:`safe_http_error` returns sanitised error responses that never
  echo raw exception text, which prevents accidental leakage of
  caller-supplied API keys.
* :func:`rate_limit_dependency` is a dependency factory that enforces a
  sliding-window per-IP request limit on the routes it decorates.
* :class:`BodySizeLimitMiddleware` rejects requests whose body exceeds a
  configurable maximum.
* :func:`require_admin_token` is an optional dependency that gates write
  or compute-heavy endpoints behind a shared secret header.
* :func:`assert_valid_coords` validates geographic coordinates before
  they are forwarded to upstream services.
"""
from __future__ import annotations

import logging
import os
import time
from collections import deque
from threading import Lock
from typing import Callable, Iterable

from fastapi import HTTPException, Request, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response


logger = logging.getLogger("skycoach.security")


# ---------------------------------------------------------------------------
# Error responses without secret leakage
# ---------------------------------------------------------------------------

def safe_http_error(
    status_code: int,
    public_message: str,
    *,
    log_exception: BaseException | None = None,
    extra: dict | None = None,
) -> HTTPException:
    """Build an HTTPException whose detail is safe to return to the client.

    The original exception, if provided, is logged server-side with full
    detail. Only ``public_message`` is included in the HTTP response, which
    keeps internal stack traces and any caller-supplied secrets out of the
    response body.
    """
    if log_exception is not None:
        logger.warning(
            "request failed: %s | extra=%s",
            log_exception,
            extra or {},
            exc_info=True,
        )
    return HTTPException(status_code=status_code, detail=public_message)


# ---------------------------------------------------------------------------
# In-process per-IP rate limiter
# ---------------------------------------------------------------------------

class _RateLimiter:
    """Sliding-window rate limiter keyed by (route, ip)."""

    def __init__(self) -> None:
        self._buckets: dict[tuple[str, str], deque[float]] = {}
        self._lock = Lock()

    def hit(self, key: tuple[str, str], window_s: float, limit: int) -> bool:
        now = time.monotonic()
        with self._lock:
            bucket = self._buckets.setdefault(key, deque())
            cutoff = now - window_s
            while bucket and bucket[0] < cutoff:
                bucket.popleft()
            if len(bucket) >= limit:
                return False
            bucket.append(now)
            return True


_rate_limiter = _RateLimiter()


def _client_key(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for", "")
    if forwarded:
        # x-forwarded-for is a CSV; first entry is the original client.
        return forwarded.split(",", 1)[0].strip()
    if request.client and request.client.host:
        return request.client.host
    return "unknown"


def rate_limit_dependency(*, requests: int, window_seconds: float):
    """FastAPI dependency factory that enforces a sliding-window per-IP
    rate limit on the route that depends on it.

    Example::

        @router.post(
            "/foo",
            dependencies=[
                Depends(rate_limit_dependency(requests=10, window_seconds=60)),
            ],
        )
    """
    def _dep(request: Request) -> None:
        route = request.url.path
        key = (route, _client_key(request))
        if not _rate_limiter.hit(key, window_seconds, requests):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Try again in {int(window_seconds)}s.",
            )

    return _dep


# ---------------------------------------------------------------------------
# Body size limit middleware
# ---------------------------------------------------------------------------

class BodySizeLimitMiddleware(BaseHTTPMiddleware):
    """Reject requests whose ``Content-Length`` header exceeds ``max_bytes``.

    The check is performed before the request body is consumed, so large
    payloads are short-circuited cheaply. Chunked-encoded uploads that omit
    ``Content-Length`` should be additionally bounded by a reverse-proxy
    limit upstream of the application server.
    """

    def __init__(self, app, max_bytes: int = 1_000_000) -> None:
        super().__init__(app)
        self.max_bytes = max_bytes

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        content_length = request.headers.get("content-length")
        if content_length and content_length.isdigit() and int(content_length) > self.max_bytes:
            return JSONResponse(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                content={"detail": "Request body too large."},
            )
        return await call_next(request)


# ---------------------------------------------------------------------------
# Optional admin token (for write endpoints / refresh hooks)
# ---------------------------------------------------------------------------

def require_admin_token(request: Request) -> None:
    """Reject the request unless its ``X-Admin-Token`` header matches the
    configured ``ADMIN_API_TOKEN`` environment variable.

    If ``ADMIN_API_TOKEN`` is not set, the check is skipped. This makes
    local development unaffected while still allowing production
    deployments to opt into a shared-secret gate on sensitive endpoints.
    """
    expected = os.getenv("ADMIN_API_TOKEN")
    if not expected:
        return
    presented = request.headers.get("x-admin-token", "")
    if presented != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid admin token.",
        )


# ---------------------------------------------------------------------------
# Coordinate validation
# ---------------------------------------------------------------------------

def assert_valid_coords(lat: float | None, lon: float | None) -> None:
    """Validate that ``(lat, lon)`` describe a point on Earth.

    Raises a 400 ``HTTPException`` if either value is out of range or only
    one of the two is supplied.
    """
    if lat is None and lon is None:
        return
    if lat is None or lon is None:
        raise HTTPException(status_code=400, detail="Both latitude and longitude are required.")
    try:
        lat_f = float(lat)
        lon_f = float(lon)
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail="Coordinates must be numeric.")
    if not (-90.0 <= lat_f <= 90.0) or not (-180.0 <= lon_f <= 180.0):
        raise HTTPException(status_code=400, detail="Coordinates out of range.")
