from __future__ import annotations

import os
from typing import Any, Callable

from zork.collections.schema import Field
from zork.hooks.registry import HookRegistry
from zork.hooks.runner import HookRunner

DEFAULT_ACCESS_TOKEN_EXPIRY = 3600
DEFAULT_REFRESH_TOKEN_EXPIRY = 604800
DEFAULT_MAX_REFRESH_TOKENS = 5

__all__ = [
    "Auth",
    "DEFAULT_ACCESS_TOKEN_EXPIRY",
    "DEFAULT_REFRESH_TOKEN_EXPIRY",
    "DEFAULT_MAX_REFRESH_TOKENS",
]


class Auth:
    def __init__(
        self,
        *,
        token_expiry: int = 86400,
        allow_registration: bool = True,
        extend_user: list[Field] | None = None,
        access_token_expiry: int | None = None,
        refresh_token_expiry: int | None = None,
        blocklist_backend: str | None = None,
        token_delivery: str | None = None,
        cookie_secure: bool | None = None,
        cookie_samesite: str | None = None,
        cookie_domain: str | None = None,
        csrf_enable: bool | None = None,
        max_refresh_tokens: int | None = None,
    ):
        self.token_expiry = token_expiry
        self.allow_registration = allow_registration
        self.extend_user = extend_user or []
        self._registry: HookRegistry = HookRegistry()
        self._runner: HookRunner = HookRunner(self._registry)

        self.access_token_expiry = int(
            os.getenv(
                "ZORK_ACCESS_TOKEN_EXPIRY",
                str(access_token_expiry or DEFAULT_ACCESS_TOKEN_EXPIRY),
            )
        )
        self.refresh_token_expiry = int(
            os.getenv(
                "ZORK_REFRESH_TOKEN_EXPIRY",
                str(refresh_token_expiry or DEFAULT_REFRESH_TOKEN_EXPIRY),
            )
        )

        self.blocklist_backend = blocklist_backend or os.getenv(
            "ZORK_BLOCKLIST_BACKEND", "database"
        )
        self.token_delivery = token_delivery or os.getenv(
            "ZORK_AUTH_DELIVERY", "bearer"
        )

        secure_env = os.getenv(
            "ZORK_COOKIE_SECURE",
            str(cookie_secure if cookie_secure is not None else True),
        )
        self.cookie_secure = secure_env.lower() in ("true", "1", "yes")
        self.cookie_samesite = os.getenv(
            "ZORK_COOKIE_SAMESITE", cookie_samesite or "lax"
        )
        self.cookie_domain = os.getenv("ZORK_COOKIE_DOMAIN", cookie_domain)

        csrf_env = os.getenv(
            "ZORK_CSRF_ENABLE", str(csrf_enable if csrf_enable is not None else True)
        )
        self.csrf_enable = csrf_env.lower() in ("true", "1", "yes")

        self.max_refresh_tokens = int(
            os.getenv(
                "ZORK_MAX_REFRESH_TOKENS",
                str(max_refresh_tokens or DEFAULT_MAX_REFRESH_TOKENS),
            )
        )

    def bind_registry(self, registry: HookRegistry, runner: HookRunner) -> None:
        """Swap in a shared registry, migrating any existing handlers."""
        if registry is self._registry:
            return
        for event, handlers in self._registry._hooks.items():
            for h in handlers:
                registry.on(event, h)
        self._registry = registry
        self._runner = runner

    def on(self, event: str, handler: Callable | None = None):
        """Register an auth hook. Namespaced as ``auth:{event}``.

        Supports both direct call and decorator forms.
        """
        full = f"auth:{event}"
        if handler is None:

            def decorator(fn: Callable) -> Callable:
                self._registry.on(full, fn)
                return fn

            return decorator
        self._registry.on(full, handler)
        return handler

    async def fire(self, event: str, payload: Any, ctx: Any) -> Any:
        return await self._runner.fire(f"auth:{event}", payload, ctx)

    def get_extend_columns_sql(self) -> list[str]:
        return [f.column_sql() for f in self.extend_user]
