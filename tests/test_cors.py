import pytest
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.testclient import TestClient

from zork.app import Zork, _CORSConfig
from zork.pipeline import build_middleware_stack


async def ok_endpoint(request: Request):
    return JSONResponse({"ok": True})


class TestCORSConfig:
    def test_default_disabled(self):
        config = _CORSConfig()
        assert config._is_configured() is False
        assert config._allow_origins == []
        assert config._allow_credentials is False

    def test_allow_origins(self):
        config = _CORSConfig()
        config.allow_origins(["https://example.com"])
        assert config._allow_origins == ["https://example.com"]
        assert config._is_configured() is True

    def test_allow_credentials(self):
        config = _CORSConfig()
        config.allow_credentials(True)
        assert config._allow_credentials is True

    def test_allow_methods(self):
        config = _CORSConfig()
        config.allow_methods(["GET", "POST"])
        assert config._allow_methods == ["GET", "POST"]

    def test_allow_headers(self):
        config = _CORSConfig()
        config.allow_headers(["X-Custom-Header"])
        assert config._allow_headers == ["X-Custom-Header"]

    def test_expose_headers(self):
        config = _CORSConfig()
        config.expose_headers(["X-Total-Count"])
        assert config._expose_headers == ["X-Total-Count"]

    def test_max_age(self):
        config = _CORSConfig()
        config.max_age(3600)
        assert config._max_age == 3600

    def test_build_config(self):
        config = _CORSConfig()
        config.allow_origins(["https://example.com"])
        config.allow_credentials(True)
        config.allow_methods(["GET"])
        config.allow_headers(["Content-Type"])

        cfg = config._build_config()
        assert cfg["allow_origins"] == ["https://example.com"]
        assert cfg["allow_credentials"] is True
        assert cfg["allow_methods"] == ["GET"]
        assert cfg["allow_headers"] == ["Content-Type"]


class TestCORSMiddlewareDisabled:
    def test_no_cors_headers_when_disabled(self):
        app = Starlette(routes=[Route("/ok", ok_endpoint)])
        app = build_middleware_stack(app, cors_config=None)
        client = TestClient(app)

        resp = client.options(
            "/ok",
            headers={
                "origin": "http://localhost:3000",
                "access-control-request-method": "GET",
            },
        )
        assert "access-control-allow-origin" not in resp.headers

    def test_simple_request_no_cors_headers(self):
        app = Starlette(routes=[Route("/ok", ok_endpoint)])
        app = build_middleware_stack(app, cors_config=None)
        client = TestClient(app)

        resp = client.get("/ok", headers={"origin": "http://localhost:3000"})
        assert "access-control-allow-origin" not in resp.headers


class TestCORSMiddlewareEnabled:
    def test_allow_origins_configured(self):
        app = Starlette(routes=[Route("/ok", ok_endpoint)])
        cors_config = {
            "allow_origins": ["https://example.com"],
            "allow_credentials": False,
            "allow_methods": ["GET", "POST"],
            "allow_headers": ["Content-Type"],
            "expose_headers": [],
            "max_age": None,
        }
        app = build_middleware_stack(app, cors_config=cors_config)
        client = TestClient(app)

        resp = client.options(
            "/ok",
            headers={
                "origin": "https://example.com",
                "access-control-request-method": "GET",
            },
        )
        assert resp.headers["access-control-allow-origin"] == "https://example.com"
        # Starlette adds space after comma
        assert "GET" in resp.headers["access-control-allow-methods"]
        assert "POST" in resp.headers["access-control-allow-methods"]

    def test_allow_credentials_false(self):
        app = Starlette(routes=[Route("/ok", ok_endpoint)])
        cors_config = {
            "allow_origins": ["*"],
            "allow_credentials": False,
            "allow_methods": ["GET"],
            "allow_headers": [],
            "expose_headers": [],
            "max_age": None,
        }
        app = build_middleware_stack(app, cors_config=cors_config)
        client = TestClient(app)

        resp = client.options(
            "/ok",
            headers={
                "origin": "http://localhost:3000",
                "access-control-request-method": "GET",
            },
        )
        assert resp.headers["access-control-allow-origin"] == "*"
        assert "access-control-allow-credentials" not in resp.headers

    def test_wildcard_with_credentials_allowed_by_starlette(self):
        # Starlette's CORSMiddleware allows this combo (browser rejects it)
        # We test the security warning in TestCORSInsecureWarning instead
        cors_config = {
            "allow_origins": ["*"],
            "allow_credentials": True,
            "allow_methods": ["GET"],
            "allow_headers": [],
            "expose_headers": [],
            "max_age": None,
        }
        app = Starlette(routes=[Route("/ok", ok_endpoint)])
        app = build_middleware_stack(app, cors_config=cors_config)
        client = TestClient(app)

        resp = client.options(
            "/ok",
            headers={
                "origin": "http://localhost:3000",
                "access-control-request-method": "GET",
            },
        )
        # Starlette allows "*" with credentials - browser will reject it
        assert "access-control-allow-origin" in resp.headers

    def test_custom_headers(self):
        app = Starlette(routes=[Route("/ok", ok_endpoint)])
        cors_config = {
            "allow_origins": ["https://example.com"],
            "allow_credentials": False,
            "allow_methods": ["GET"],
            "allow_headers": ["X-Custom-Header", " Authorization"],
            "expose_headers": ["X-Total-Count"],
            "max_age": None,
        }
        app = build_middleware_stack(app, cors_config=cors_config)
        client = TestClient(app)

        resp = client.options(
            "/ok",
            headers={
                "origin": "https://example.com",
                "access-control-request-method": "GET",
                "access-control-request-headers": "X-Custom-Header",
            },
        )
        assert "X-Custom-Header" in resp.headers.get("access-control-allow-headers", "")


class TestCORSAppConstruction:
    def test_default_no_cors(self):
        app = Zork(database=":memory:")
        assert app.cors._is_configured() is False

    def test_constructor_cors_origins(self):
        app = Zork(
            database=":memory:",
            cors_allow_origins=["https://example.com"],
        )
        assert app.cors._allow_origins == ["https://example.com"]
        assert app.cors._is_configured() is True

    def test_constructor_cors_credentials(self):
        app = Zork(
            database=":memory:",
            cors_allow_credentials=True,
        )
        assert app.cors._allow_credentials is True

    def test_constructor_cors_methods(self):
        app = Zork(
            database=":memory:",
            cors_allow_methods=["GET", "POST"],
        )
        assert app.cors._allow_methods == ["GET", "POST"]

    def test_constructor_cors_headers(self):
        app = Zork(
            database=":memory:",
            cors_allow_headers=["Content-Type"],
        )
        assert app.cors._allow_headers == ["Content-Type"]

    def test_constructor_full_cors(self):
        app = Zork(
            database=":memory:",
            cors_allow_origins=["https://example.com"],
            cors_allow_credentials=True,
            cors_allow_methods=["GET", "POST"],
            cors_allow_headers=["Content-Type"],
        )
        assert app.cors._allow_origins == ["https://example.com"]
        assert app.cors._allow_credentials is True
        assert app.cors._allow_methods == ["GET", "POST"]
        assert app.cors._allow_headers == ["Content-Type"]

    def test_fluent_api_allows_chaining(self):
        app = Zork(database=":memory:")
        app.cors.allow_origins(["https://example.com"])
        app.cors.allow_credentials(True)
        app.cors.allow_methods(["GET"])
        app.cors.allow_headers(["X-Custom"])

        assert app.cors._allow_origins == ["https://example.com"]
        assert app.cors._allow_credentials is True
        assert app.cors._allow_methods == ["GET"]
        assert app.cors._allow_headers == ["X-Custom"]

    def test_fluent_after_constructor(self):
        app = Zork(
            database=":memory:",
            cors_allow_origins=["https://example.com"],
        )
        app.cors.allow_methods(["GET", "POST"])

        assert app.cors._allow_origins == ["https://example.com"]
        assert app.cors._allow_methods == ["GET", "POST"]


class TestCORSInsecureWarning:
    def test_wildcard_with_credentials_logs_warning(self, caplog):
        app = Zork(
            database=":memory:",
            cors_allow_origins=["*"],
            cors_allow_credentials=True,
        )
        built = app.build()
        assert any(
            "allow_origins=['*'] and allow_credentials=True" in record.message
            for record in caplog.records
        )


class TestCORSEndToEnd:
    def test_build_app_with_cors(self):
        from zork import Collection, TextField

        app = Zork(database=":memory:")
        posts = Collection("posts", fields=[TextField("title", required=True)])
        app.register(posts)
        app.cors.allow_origins(["https://example.com"])

        built = app.build()

        client = TestClient(built, raise_server_exceptions=False)
        resp = client.options(
            "/api/posts",
            headers={
                "origin": "https://example.com",
                "access-control-request-method": "GET",
            },
        )
        assert "access-control-allow-origin" in resp.headers

    def test_build_app_without_cors_no_headers(self):
        from zork import Collection, TextField

        app = Zork(database=":memory:")
        posts = Collection("posts", fields=[TextField("title", required=True)])
        app.register(posts)

        built = app.build()

        client = TestClient(built, raise_server_exceptions=False)
        resp = client.options(
            "/api/posts",
            headers={
                "origin": "https://example.com",
                "access-control-request-method": "GET",
            },
        )
        assert "access-control-allow-origin" not in resp.headers
