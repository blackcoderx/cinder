from __future__ import annotations

import logging
import os
import secrets
from contextlib import asynccontextmanager

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.types import ASGIApp, Receive, Scope, Send

from cinder.auth import Auth
from cinder.auth.models import create_auth_tables, cleanup_expired_blocklist
from cinder.auth.routes import build_auth_routes
from cinder.collections.router import build_collection_routes
from cinder.collections.schema import Collection, TextField
from cinder.collections.store import CollectionStore
from cinder.db.connection import Database
from cinder.pipeline import build_middleware_stack

logger = logging.getLogger("cinder")


class Cinder:
    def __init__(self, database: str = "app.db"):
        self.database = database
        self._collections: dict[str, tuple[Collection, dict[str, str]]] = {}
        self._auth: Auth | None = None
        self._secret: str | None = None

    def register(self, collection: Collection, auth: list[str] | None = None) -> None:
        auth_rules = {}
        if auth:
            for rule in auth:
                parts = rule.split(":")
                if len(parts) == 2:
                    auth_rules[parts[0]] = parts[1]

        # Auto-add created_by field if owner rule is used
        if "owner" in auth_rules.values():
            has_created_by = any(f.name == "created_by" for f in collection.fields)
            if not has_created_by:
                collection.fields.append(TextField("created_by"))

        self._collections[collection.name] = (collection, auth_rules)

    def use_auth(self, auth: Auth) -> None:
        self._auth = auth

    def _get_secret(self) -> str:
        if self._secret:
            return self._secret

        self._secret = os.getenv("CINDER_SECRET")
        if not self._secret:
            self._secret = secrets.token_urlsafe(32)
            logger.warning(
                "No CINDER_SECRET set — tokens will not survive restarts. "
                "Set CINDER_SECRET in your .env file."
            )
        return self._secret

    def build(self) -> Starlette:
        db = Database(self.database)
        store = CollectionStore(db)
        secret = self._get_secret()
        collections = self._collections
        auth = self._auth

        # Track whether the one-time startup initialisation has been performed.
        # Using a mutable container so the nested coroutine can update it.
        _init_done: list[bool] = [False]

        async def _init() -> None:
            if _init_done[0]:
                return
            await db.connect()
            logger.info(f"Connected to database: {self.database}")

            for name, (collection, _) in collections.items():
                await store.sync_schema(collection)
                logger.info(f"Synced collection: {name}")

            if auth:
                extend_cols = auth.get_extend_columns_sql()
                await create_auth_tables(db, extend_cols if extend_cols else None)
                await cleanup_expired_blocklist(db)
                logger.info("Auth tables ready")

            _init_done[0] = True

        @asynccontextmanager
        async def lifespan(app: Starlette):
            await _init()
            yield
            await db.disconnect()
            logger.info("Database disconnected")

        routes: list[Route] = []

        async def health(request: Request) -> JSONResponse:
            return JSONResponse({"status": "ok"})

        routes.append(Route("/api/health", health, methods=["GET"]))
        routes.extend(build_collection_routes(collections, store))

        if auth:
            routes.extend(build_auth_routes(auth, db, secret))

        starlette_app = Starlette(routes=routes, lifespan=lifespan)

        # LazyInitMiddleware ensures _init() is called before the first request
        # even when the lifespan is not triggered (e.g. Starlette TestClient
        # used without a context manager).
        class LazyInitMiddleware:
            def __init__(self, inner: ASGIApp) -> None:
                self._inner = inner

            async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
                if scope["type"] == "http" and not _init_done[0]:
                    await _init()
                await self._inner(scope, receive, send)

        wrapped = build_middleware_stack(
            starlette_app,
            db=db if auth else None,
            secret=secret if auth else None,
        )

        # Wrap *outside* the existing middleware stack so lazy init fires first.
        return LazyInitMiddleware(wrapped)  # type: ignore[return-value]

    def serve(self, host: str = "0.0.0.0", port: int = 8000, reload: bool = False) -> None:
        import uvicorn
        app = self.build()
        uvicorn.run(app, host=host, port=port)
