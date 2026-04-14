import pytest
from starlette.testclient import TestClient

from zork.app import Zork
from zork.auth import Auth
from zork.collections.schema import Collection, IntField, TextField


@pytest.fixture
def app(db_path):
    zork = Zork(database=db_path)

    posts = Collection(
        "posts",
        fields=[
            TextField("title", required=True),
            TextField("body"),
            IntField("views", default=0),
        ],
    )
    zork.register(posts, auth=["read:public", "write:public"])
    return zork


@pytest.fixture
def app_with_auth(db_path):
    zork = Zork(database=db_path)

    posts = Collection(
        "posts",
        fields=[
            TextField("title", required=True),
        ],
    )
    auth = Auth(token_expiry=3600, allow_registration=True)

    zork.register(posts, auth=["read:public", "write:authenticated"])
    zork.use_auth(auth)
    return zork


class TestZorkApp:
    def test_build_creates_working_app(self, app):
        starlette_app = app.build()
        client = TestClient(starlette_app)

        resp = client.post("/api/posts", json={"title": "Hello"})
        assert resp.status_code == 201

        resp = client.get("/api/posts")
        assert resp.status_code == 200
        assert resp.json()["total"] == 1

    def test_collections_registered(self, app):
        assert "posts" in app._collections

    def test_health_check(self, app):
        starlette_app = app.build()
        client = TestClient(starlette_app)
        resp = client.get("/api/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}


class TestZorkWithAuth:
    def test_auth_routes_available(self, app_with_auth):
        starlette_app = app_with_auth.build()
        client = TestClient(starlette_app)

        resp = client.post(
            "/api/auth/register",
            json={
                "email": "test@test.com",
                "password": "password123",
            },
        )
        assert resp.status_code == 201
        token = resp.json()["token"]

        resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200

    def test_authenticated_write_requires_token(self, app_with_auth):
        starlette_app = app_with_auth.build()
        client = TestClient(starlette_app)

        resp = client.post("/api/posts", json={"title": "Unauthorized"})
        assert resp.status_code == 401

    def test_authenticated_write_with_token(self, app_with_auth):
        starlette_app = app_with_auth.build()
        client = TestClient(starlette_app)

        reg = client.post(
            "/api/auth/register",
            json={
                "email": "writer@test.com",
                "password": "password123",
            },
        ).json()
        token = reg["token"]

        resp = client.post(
            "/api/posts",
            json={"title": "Authorized"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 201

    def test_public_read_without_token(self, app_with_auth):
        starlette_app = app_with_auth.build()
        client = TestClient(starlette_app)

        resp = client.get("/api/posts")
        assert resp.status_code == 200
