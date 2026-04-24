from __future__ import annotations

from typing import Callable


def filter_for_rule(
    rule: str, owner_field: str = "created_by"
) -> Callable[[dict, dict | None], bool]:
    """Return a filter callable that mirrors the collection's ``read`` auth rule.

    The filter is called per-envelope per-subscriber when the broker fans out
    an event:  ``filter(envelope, user) -> bool``.  Returning ``True`` means
    the envelope is delivered; ``False`` means it is silently dropped for that
    subscriber.

    Rules mirror ``src/zork/collections/router.py::_check_auth`` /
    ``_check_owner`` exactly so that subscribers only receive events for
    records they are authorised to read via the REST API.

    Developers can always bypass this by passing their own ``filter`` callable
    when subscribing through ``broker.subscribe(...)`` directly.

    Args:
        rule: Auth rule ("public", "authenticated", "admin", "owner")
        owner_field: Field name to check for ownership (default: "created_by")
    """
    if rule == "public":
        return _public_filter

    if rule == "authenticated":
        return _authenticated_filter

    if rule == "admin":
        return _admin_filter

    if rule == "owner":
        return lambda env, u: _owner_filter(env, u, owner_field)

    return _authenticated_filter


# ---------------------------------------------------------------------------
# Filter implementations
# ---------------------------------------------------------------------------


def _public_filter(envelope: dict, user: dict | None) -> bool:  # noqa: ARG001
    return True


def _authenticated_filter(envelope: dict, user: dict | None) -> bool:  # noqa: ARG001
    return user is not None


def _admin_filter(envelope: dict, user: dict | None) -> bool:  # noqa: ARG001
    return user is not None and user.get("role") == "admin"


def _owner_filter(envelope: dict, user: dict | None, owner_field: str = "created_by") -> bool:
    if user is None:
        return False
    record = envelope.get("record") or {}
    return record.get(owner_field) == user.get("id")
