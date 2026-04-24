from __future__ import annotations

import asyncio
import json
import logging
import os
import re
from typing import TYPE_CHECKING, AsyncGenerator

from starlette.requests import Request
from starlette.responses import JSONResponse, StreamingResponse

from zork.errors import ZorkError
from zork.realtime.auth import authenticate_ws_token
from zork.realtime.auth_filter import filter_for_rule

if TYPE_CHECKING:
    from zork.realtime import RealtimeFacade

logger = logging.getLogger("zork.realtime.sse")

HEARTBEAT_INTERVAL: float = float(os.getenv("ZORK_SSE_HEARTBEAT", "15"))

CHANNEL_VALIDATION_REGEX = re.compile(r"^[a-zA-Z0-9:_\-.]+$")
CHANNEL_MAX_LENGTH = 256


def _validate_channel(channel: str) -> str | None:
    """Validate channel name format.

    Returns None if valid, or an error message if invalid.
    Channel names must be alphanumeric with colons, underscores, hyphens, and dots.
    """
    if not channel:
        return "Channel name cannot be empty"
    if len(channel) > CHANNEL_MAX_LENGTH:
        return f"Channel name exceeds maximum length of {CHANNEL_MAX_LENGTH}"
    if not CHANNEL_VALIDATION_REGEX.match(channel):
        return "Invalid channel name format"
    return None


def _match_origin(origin: str, pattern: str) -> bool:
    """Check if origin matches the given regex pattern."""
    try:
        return bool(re.match(pattern, origin))
    except re.error:
        return False


def sse_endpoint_factory(facade: "RealtimeFacade", db, secret: str, cors_config: dict | None = None):
    """Return the SSE HTTP handler bound to this app's realtime facade.

    Called once from ``Zork.build()``; the resulting coroutine is registered
    as a ``Route`` with ``methods=["GET"]``.

    Query parameters:
    - ``token``   — JWT bearer token (required unless collection is public)
    - ``channel`` — one or more channel names to subscribe to (repeatable)

    Example::

        GET /api/realtime/sse?token=<jwt>&channel=collection:posts&channel=collection:comments
    """
    if cors_config is None:
        cors_config = {"allow_origins": "*", "allow_origin_regex": None}

    async def sse_endpoint(request: Request) -> StreamingResponse:
        origin = request.headers.get("origin", "")

        if cors_config.get("allow_origins") != "*":
            allowed_origins = cors_config.get("allow_origins", [])
            origin_regex = cors_config.get("allow_origin_regex")
            if isinstance(allowed_origins, list) and origin not in allowed_origins:
                if not origin_regex or not _match_origin(origin, origin_regex):
                    return JSONResponse(
                        {"status": 403, "error": "Origin not allowed"},
                        status_code=403,
                    )

        # ------------------------------------------------------------------
        # 1. Authenticate
        # ------------------------------------------------------------------
        user = None
        token = request.query_params.get("token")
        if token:
            try:
                user = await authenticate_ws_token(token, db, secret)
            except ZorkError as e:
                from starlette.responses import JSONResponse

                return JSONResponse(
                    {"status": e.status_code, "error": e.message},
                    status_code=e.status_code,
                )

        # ------------------------------------------------------------------
        # 2. Collect and validate requested channels
        # ------------------------------------------------------------------
        channels = request.query_params.getlist("channel")
        if not channels:
            from starlette.responses import JSONResponse

            return JSONResponse(
                {"status": 400, "error": "At least one channel is required"},
                status_code=400,
            )

        # Validate channel names
        for channel in channels:
            validation_error = _validate_channel(channel)
            if validation_error:
                from starlette.responses import JSONResponse

                return JSONResponse(
                    {"status": 400, "error": validation_error},
                    status_code=400,
                )

        # ------------------------------------------------------------------
        # 3. Subscribe and build per-channel filters
        # ------------------------------------------------------------------
        # For built-in collection channels, attach the read-rule filter.
        # Custom channels get no default filter (public by default).
        combined_filter = _build_filter(channels, facade, user)
        subscription = await facade.broker.subscribe(
            channels, user=user, filter=combined_filter
        )

        # ------------------------------------------------------------------
        # 4. Stream
        # ------------------------------------------------------------------
        async def event_generator() -> AsyncGenerator[bytes, None]:
            # SSE preamble headers are set on the response; nothing to yield.
            try:
                while True:
                    try:
                        envelope = await asyncio.wait_for(
                            subscription.get(), timeout=HEARTBEAT_INTERVAL
                        )
                    except asyncio.TimeoutError:
                        # Heartbeat — SSE comment line; ignored by browsers
                        yield b": ping\n\n"
                        continue

                    if envelope is None:
                        # Broker closed (app:shutdown)
                        return

                    # Format as SSE frame
                    data = json.dumps(envelope)
                    event_type = envelope.get("event", "message")
                    record_id = envelope.get("id", "")
                    frame = f"event: {event_type}\ndata: {data}\nid: {record_id}\n\n"
                    yield frame.encode()

            except asyncio.CancelledError:
                # Client disconnected
                pass
            finally:
                await facade.broker.unsubscribe(subscription)

        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
            },
        )

    return sse_endpoint


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _build_filter(channels: list[str], facade: "RealtimeFacade", user: dict | None):
    """Build a combined filter that applies per-collection auth rules for
    built-in ``collection:{name}`` channels.  Custom channels pass through."""
    channel_filters: dict[str, object] = {}
    for channel in channels:
        if not channel.startswith("collection:"):
            continue
        name = channel.removeprefix("collection:")
        collections = facade._collections
        if name not in collections:
            continue
        collection, auth_rules = collections[name]
        read_rule = auth_rules.get("read", "public")
        channel_filters[channel] = filter_for_rule(read_rule, collection.owner_field)

    if not channel_filters:
        return None  # all custom channels — no filter

    def combined(envelope: dict, u: dict | None) -> bool:
        ch = envelope.get("channel", "")
        f = channel_filters.get(ch)
        if f is None:
            return True  # custom channel — allow
        return f(envelope, u)  # type: ignore[return-value]

    return combined
