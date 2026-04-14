from __future__ import annotations

import logging

from zeno.auth.models import USERS_TABLE, is_blocked
from zeno.auth.tokens import decode_token
from zeno.db.connection import Database
from zeno.errors import ZenoError

logger = logging.getLogger("zeno.realtime.auth")


async def authenticate_ws_token(
    token: str,
    db: Database,
    secret: str,
) -> dict | None:
    """Decode a JWT token and return the user dict or ``None``.

    Used by both the WebSocket and SSE handlers because
    ``AuthMiddleware`` in ``pipeline.py`` only processes HTTP scopes.
    Unlike the middleware, this function raises ``CinderError`` so
    transport handlers can send a proper close/error response:

    - ``CinderError(401, ...)`` — invalid/expired token or blocked JTI
    - ``CinderError(401, "User not found")`` — valid token, missing user row

    Returns the user dict (without the ``password`` field) on success.
    """
    try:
        payload = decode_token(token, secret)
    except ZenoError:
        raise

    jti = payload.get("jti")
    if jti and await is_blocked(db, jti):
        raise ZenoError(401, "Token has been revoked")

    user_id = payload.get("sub")
    if not user_id:
        raise ZenoError(401, "Invalid token payload")

    row = await db.fetch_one(f"SELECT * FROM {USERS_TABLE} WHERE id = ?", (user_id,))
    if row is None:
        raise ZenoError(401, "User not found")

    user = dict(row)
    user.pop("password", None)
    return user
