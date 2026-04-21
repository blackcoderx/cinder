"""Tests for static file serving feature."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest
from starlette.testclient import TestClient

from zork import Zork
from zork.staticfiles import StaticFilesConfig, mount_static_files


class TestStaticFilesConfig:
    """Tests for StaticFilesConfig class."""

    def test_basic_config(self):
        config = StaticFilesConfig("/static", "./static")
        assert config.path == "/static"
        assert config.directory == "./static"
        assert config.html is False
        assert config.cache_ttl is None

    def test_name_derived_from_path(self):
        config = StaticFilesConfig("/static", "./static")
        assert config.name == "static"

    def test_name_from_path_with_slashes(self):
        config = StaticFilesConfig("/static/css", "./css")
        assert config.name == "static_css"

    def test_custom_name(self):
        config = StaticFilesConfig("/static", "./static", name="assets")
        assert config.name == "assets"

    def test_html_mode(self):
        config = StaticFilesConfig("/static", "./static", html=True)
        assert config.html is True

    def test_cache_ttl(self):
        config = StaticFilesConfig("/static", "./static", cache_ttl=3600)
        assert config.cache_ttl == 3600

    def test_cache_headers_when_ttl_set(self):
        config = StaticFilesConfig("/static", "./static", cache_ttl=3600)
        headers = config.get_cache_headers()
        assert headers == {"Cache-Control": "public, max-age=3600"}

    def test_cache_headers_when_ttl_none(self):
        config = StaticFilesConfig("/static", "./static")
        headers = config.get_cache_headers()
        assert headers is None


class TestStaticFilesConfigValidation:
    """Tests for StaticFilesConfig validation."""

    def test_validate_directory_exists(self, tmp_path):
        static_dir = tmp_path / "static"
        static_dir.mkdir()
        config = StaticFilesConfig("/static", str(static_dir))
        config.validate()

    def test_validate_directory_not_exists(self):
        config = StaticFilesConfig("/static", "./nonexistent")
        with pytest.raises(ValueError, match="Static files directory does not exist"):
            config.validate()


class TestMountStaticFiles:
    """Tests for mount_static_files function."""

    def test_single_mount(self, tmp_path):
        static_dir = tmp_path / "static"
        static_dir.mkdir()
        config = StaticFilesConfig("/static", str(static_dir))
        routes = mount_static_files([config])
        assert len(routes) == 1

    def test_multiple_mounts(self, tmp_path):
        static_dir1 = tmp_path / "static"
        static_dir2 = tmp_path / "assets"
        static_dir1.mkdir()
        static_dir2.mkdir()

        configs = [
            StaticFilesConfig("/static", str(static_dir1)),
            StaticFilesConfig("/assets", str(static_dir2)),
        ]
        routes = mount_static_files(configs)
        assert len(routes) == 2

    def test_validates_all_configs(self, tmp_path):
        static_dir = tmp_path / "static"
        static_dir.mkdir()

        configs = [
            StaticFilesConfig("/static", str(static_dir)),
            StaticFilesConfig("/assets", "./nonexistent"),
        ]
        with pytest.raises(ValueError, match="Static files directory does not exist"):
            mount_static_files(configs)


class TestZorkStaticFilesIntegration:
    """Integration tests for static files with Zork app."""

    def test_single_static_mount(self, tmp_path):
        static_dir = tmp_path / "static"
        static_dir.mkdir()
        (static_dir / "test.css").write_text("body { margin: 0; }")

        app = Zork(database=":memory:")
        app.static("/static", str(static_dir))
        built = app.build()

        client = TestClient(built, raise_server_exceptions=False)
        resp = client.get("/static/test.css")
        assert resp.status_code == 200
        assert resp.text == "body { margin: 0; }"

    def test_multiple_static_mounts(self, tmp_path):
        static_dir = tmp_path / "static"
        assets_dir = tmp_path / "assets"
        static_dir.mkdir()
        assets_dir.mkdir()

        (static_dir / "test.css").write_text("body { margin: 0; }")
        (assets_dir / "logo.svg").write_text("<svg></svg>")

        app = Zork(database=":memory:")
        app.static("/static", str(static_dir))
        app.static("/assets", str(assets_dir))
        built = app.build()

        client = TestClient(built, raise_server_exceptions=False)
        resp = client.get("/static/test.css")
        assert resp.status_code == 200

        resp = client.get("/assets/logo.svg")
        assert resp.status_code == 200

    def test_static_file_not_found(self, tmp_path):
        static_dir = tmp_path / "static"
        static_dir.mkdir()

        app = Zork(database=":memory:")
        app.static("/static", str(static_dir))
        built = app.build()

        client = TestClient(built, raise_server_exceptions=False)
        resp = client.get("/static/nonexistent.css")
        assert resp.status_code == 404

    def test_static_files_not_in_api_routes(self, tmp_path):
        static_dir = tmp_path / "static"
        static_dir.mkdir()
        (static_dir / "test.css").write_text("body { margin: 0; }")

        app = Zork(database=":memory:")
        app.static("/static", str(static_dir))
        built = app.build()

        client = TestClient(built, raise_server_exceptions=False)
        resp = client.get("/api/health")
        assert resp.status_code == 200


class TestSPAMode:
    """Tests for SPA fallback mode."""

    def test_spa_fallback_serves_index_html(self, tmp_path):
        dist_dir = tmp_path / "dist"
        dist_dir.mkdir()
        (dist_dir / "index.html").write_text("<html>SPA</html>")
        (dist_dir / "app.js").write_text("console.log('app')")

        app = Zork(database=":memory:")
        app.static("/", str(dist_dir), html=True)
        built = app.build()

        client = TestClient(built, raise_server_exceptions=False)
        resp = client.get("/index.html")
        assert resp.status_code == 200
        assert "SPA" in resp.text

        resp = client.get("/app.js")
        assert resp.status_code == 200


class TestSecurity:
    """Security tests for static file serving."""

    def test_path_traversal_blocked(self, tmp_path):
        static_dir = tmp_path / "static"
        static_dir.mkdir()
        (static_dir / "test.css").write_text("body { margin: 0; }")

        app = Zork(database=":memory:")
        app.static("/static", str(static_dir))
        built = app.build()

        client = TestClient(built, raise_server_exceptions=False)
        resp = client.get("/static/../../../etc/passwd")
        assert resp.status_code == 404

        resp = client.get("/static/..%2F..%2F..%2Fetc/passwd")
        assert resp.status_code == 404

        resp = client.get("/static/../test.css")
        assert resp.status_code == 404


class TestContentTypes:
    """Tests for content type detection."""

    def test_css_content_type(self, tmp_path):
        static_dir = tmp_path / "static"
        static_dir.mkdir()
        (static_dir / "style.css").write_text("body { }")

        app = Zork(database=":memory:")
        app.static("/static", str(static_dir))
        built = app.build()

        client = TestClient(built, raise_server_exceptions=False)
        resp = client.get("/static/style.css")
        assert resp.status_code == 200
        assert "text/css" in resp.headers.get("content-type", "")

    def test_js_content_type(self, tmp_path):
        static_dir = tmp_path / "static"
        static_dir.mkdir()
        (static_dir / "app.js").write_text("console.log('test')")

        app = Zork(database=":memory:")
        app.static("/static", str(static_dir))
        built = app.build()

        client = TestClient(built, raise_server_exceptions=False)
        resp = client.get("/static/app.js")
        assert resp.status_code == 200
        assert "javascript" in resp.headers.get("content-type", "").lower()

    def test_svg_content_type(self, tmp_path):
        static_dir = tmp_path / "static"
        static_dir.mkdir()
        (static_dir / "icon.svg").write_text("<svg></svg>")

        app = Zork(database=":memory:")
        app.static("/static", str(static_dir))
        built = app.build()

        client = TestClient(built, raise_server_exceptions=False)
        resp = client.get("/static/icon.svg")
        assert resp.status_code == 200
        assert "svg" in resp.headers.get("content-type", "").lower()


class TestFluentAPI:
    """Tests for fluent API chaining."""

    def test_method_chaining(self, tmp_path):
        static_dir = tmp_path / "static"
        static_dir.mkdir()

        app = Zork(database=":memory:")
        app.static("/static", str(static_dir))
        app.static("/assets", str(static_dir))
        app.static("/images", str(static_dir))

        built = app.build()
        client = TestClient(built, raise_server_exceptions=False)

        assert client.get("/static/test.css").status_code == 404
        assert client.get("/assets/test.css").status_code == 404
        assert client.get("/images/test.css").status_code == 404

    def test_return_self(self, tmp_path):
        static_dir = tmp_path / "static"
        static_dir.mkdir()

        app = Zork(database=":memory:")
        result = app.static("/static", str(static_dir))
        assert result is app


class TestStaticFilesConfigAppConstruction:
    """Tests for StaticFilesConfig through app."""

    def test_configure_via_fluent_api(self, tmp_path):
        static_dir = tmp_path / "static"
        static_dir.mkdir()

        app = Zork(database=":memory:")
        app.static("/static", str(static_dir))

        assert app.staticfiles._is_configured() is True
        configs = app.staticfiles._get_configs()
        assert len(configs) == 1
        assert configs[0].path == "/static"
        assert configs[0].directory == str(static_dir)

    def test_no_mounts_when_not_configured(self):
        app = Zork(database=":memory:")
        assert app.staticfiles._is_configured() is False
        assert app.staticfiles._get_configs() == []

    def test_multiple_configurations(self, tmp_path):
        static_dir = tmp_path / "static"
        assets_dir = tmp_path / "assets"
        static_dir.mkdir()
        assets_dir.mkdir()

        app = Zork(database=":memory:")
        app.static("/static", str(static_dir))
        app.static("/assets", str(assets_dir))

        configs = app.staticfiles._get_configs()
        assert len(configs) == 2
        assert configs[0].path == "/static"
        assert configs[1].path == "/assets"


class TestCacheHeaders:
    """Tests for cache headers."""

    def test_cache_headers_present(self, tmp_path):
        static_dir = tmp_path / "static"
        static_dir.mkdir()
        (static_dir / "test.css").write_text("body { }")

        app = Zork(database=":memory:")
        app.static("/static", str(static_dir), cache_ttl=3600)
        built = app.build()

        client = TestClient(built, raise_server_exceptions=False)
        resp = client.get("/static/test.css")
        assert resp.status_code == 200
        assert "cache-control" in resp.headers or "etag" in resp.headers

    def test_no_cache_headers_by_default(self, tmp_path):
        static_dir = tmp_path / "static"
        static_dir.mkdir()
        (static_dir / "test.css").write_text("body { }")

        app = Zork(database=":memory:")
        app.static("/static", str(static_dir))
        built = app.build()

        client = TestClient(built, raise_server_exceptions=False)
        resp = client.get("/static/test.css")
        assert resp.status_code == 200


class TestWithCollections:
    """Tests for static files combined with collections."""

    def test_static_and_collections(self, tmp_path):
        from zork import Collection, IntField, TextField

        static_dir = tmp_path / "static"
        static_dir.mkdir()
        (static_dir / "test.css").write_text("body { margin: 0; }")

        app = Zork(database=":memory:")
        posts = Collection("posts", fields=[TextField("title"), IntField("views")])
        app.register(posts)
        app.static("/static", str(static_dir))
        built = app.build()

        client = TestClient(built, raise_server_exceptions=False)
        resp = client.get("/static/test.css")
        assert resp.status_code == 200

        resp = client.get("/api/posts")
        assert resp.status_code == 200