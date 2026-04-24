import pytest
from starlette.applications import Starlette
from starlette.testclient import TestClient

from zork.collections.router import build_collection_routes
from zork.collections.schema import Collection, IntField, TextField
from zork.collections.store import CollectionStore
from zork.db.connection import Database
from zork.pipeline import build_middleware_stack


@pytest.fixture
async def app_with_posts(db_path):
    db = Database(db_path)
    await db.connect()
    store = CollectionStore(db)

    posts = Collection(
        "posts",
        fields=[
            TextField("title", required=True),
            IntField("views", default=0),
        ],
    )
    await store.sync_schema(posts)

    collections = {"posts": (posts, {"read": "public", "write": "public"})}
    routes = build_collection_routes(collections, store)
    app = Starlette(routes=routes)
    app = build_middleware_stack(app)

    yield TestClient(app), db
    await db.disconnect()


@pytest.fixture
async def app_with_pagination_disabled(db_path):
    db = Database(db_path)
    await db.connect()
    store = CollectionStore(db)

    posts = Collection(
        "posts",
        fields=[
            TextField("title", required=True),
            IntField("views", default=0),
        ],
        pagination=False,
    )
    await store.sync_schema(posts)

    collections = {"posts": (posts, {"read": "public", "write": "public"})}
    routes = build_collection_routes(collections, store)
    app = Starlette(routes=routes)
    app = build_middleware_stack(app)

    yield TestClient(app), db
    await db.disconnect()


@pytest.fixture
async def app_with_pagination_auto(db_path):
    db = Database(db_path)
    await db.connect()
    store = CollectionStore(db)

    posts = Collection(
        "posts",
        fields=[
            TextField("title", required=True),
            IntField("views", default=0),
        ],
        pagination="auto",
    )
    await store.sync_schema(posts)

    collections = {"posts": (posts, {"read": "public", "write": "public"})}
    routes = build_collection_routes(collections, store)
    app = Starlette(routes=routes)
    app = build_middleware_stack(app)

    yield TestClient(app), db
    await db.disconnect()


class TestPaginationMetadata:
    """Tests for comprehensive pagination metadata feature."""

    @pytest.mark.asyncio
    async def test_pagination_has_more_true(self, app_with_posts):
        """Test has_more is True when more records exist."""
        client, _ = app_with_posts

        for i in range(5):
            client.post("/api/posts", json={"title": f"Post {i}"})

        resp = client.get("/api/posts?limit=2&offset=0")
        assert resp.status_code == 200
        data = resp.json()

        assert data["pagination"]["has_more"] is True
        assert data["pagination"]["total"] == 5

    @pytest.mark.asyncio
    async def test_pagination_has_more_false(self, app_with_posts):
        """Test has_more is False on last page."""
        client, _ = app_with_posts

        for i in range(3):
            client.post("/api/posts", json={"title": f"Post {i}"})

        resp = client.get("/api/posts?limit=10&offset=0")
        data = resp.json()

        assert data["pagination"]["has_more"] is False
        assert data["pagination"]["total"] == 3

    @pytest.mark.asyncio
    async def test_pagination_next_offset(self, app_with_posts):
        """Test next_offset points to next page."""
        client, _ = app_with_posts

        for i in range(5):
            client.post("/api/posts", json={"title": f"Post {i}"})

        resp = client.get("/api/posts?limit=2&offset=0")
        data = resp.json()

        assert data["pagination"]["next_offset"] == 2

    @pytest.mark.asyncio
    async def test_pagination_next_offset_none_on_last_page(self, app_with_posts):
        """Test next_offset is None on last page."""
        client, _ = app_with_posts

        for i in range(3):
            client.post("/api/posts", json={"title": f"Post {i}"})

        resp = client.get("/api/posts?limit=2&offset=2")
        data = resp.json()

        assert data["pagination"]["next_offset"] is None

    @pytest.mark.asyncio
    async def test_pagination_prev_offset(self, app_with_posts):
        """Test prev_offset points to previous page."""
        client, _ = app_with_posts

        for i in range(5):
            client.post("/api/posts", json={"title": f"Post {i}"})

        resp = client.get("/api/posts?limit=2&offset=2")
        data = resp.json()

        assert data["pagination"]["prev_offset"] == 0

    @pytest.mark.asyncio
    async def test_pagination_prev_offset_none_on_first_page(self, app_with_posts):
        """Test prev_offset is None on first page."""
        client, _ = app_with_posts

        for i in range(3):
            client.post("/api/posts", json={"title": f"Post {i}"})

        resp = client.get("/api/posts?limit=2&offset=0")
        data = resp.json()

        assert data["pagination"]["prev_offset"] is None

    @pytest.mark.asyncio
    async def test_pagination_page_number(self, app_with_posts):
        """Test page number calculation."""
        client, _ = app_with_posts

        for i in range(10):
            client.post("/api/posts", json={"title": f"Post {i}"})

        resp = client.get("/api/posts?limit=3&offset=3")
        data = resp.json()

        assert data["pagination"]["page"] == 2

    @pytest.mark.asyncio
    async def test_pagination_total_pages(self, app_with_posts):
        """Test total_pages calculation."""
        client, _ = app_with_posts

        for i in range(10):
            client.post("/api/posts", json={"title": f"Post {i}"})

        resp = client.get("/api/posts?limit=3&offset=0")
        data = resp.json()

        assert data["pagination"]["total_pages"] == 4

    @pytest.mark.asyncio
    async def test_pagination_links_self(self, app_with_posts):
        """Test self link in pagination links."""
        client, _ = app_with_posts

        client.post("/api/posts", json={"title": "Test Post"})

        resp = client.get("/api/posts?limit=10&offset=0")
        data = resp.json()

        assert "self" in data["links"]
        assert "offset=0" in data["links"]["self"]
        assert "limit=10" in data["links"]["self"]

    @pytest.mark.asyncio
    async def test_pagination_links_next(self, app_with_posts):
        """Test next link in pagination links."""
        client, _ = app_with_posts

        for i in range(5):
            client.post("/api/posts", json={"title": f"Post {i}"})

        resp = client.get("/api/posts?limit=2&offset=0")
        data = resp.json()

        assert "next" in data["links"]
        assert data["links"]["next"] is not None
        assert "offset=2" in data["links"]["next"]

    @pytest.mark.asyncio
    async def test_pagination_links_next_none_on_last_page(self, app_with_posts):
        """Test next link is None on last page."""
        client, _ = app_with_posts

        for i in range(3):
            client.post("/api/posts", json={"title": f"Post {i}"})

        resp = client.get("/api/posts?limit=10&offset=0")
        data = resp.json()

        assert data["links"]["next"] is None

    @pytest.mark.asyncio
    async def test_pagination_links_prev(self, app_with_posts):
        """Test prev link in pagination links."""
        client, _ = app_with_posts

        for i in range(5):
            client.post("/api/posts", json={"title": f"Post {i}"})

        resp = client.get("/api/posts?limit=2&offset=2")
        data = resp.json()

        assert "prev" in data["links"]
        assert data["links"]["prev"] is not None
        assert "offset=0" in data["links"]["prev"]

    @pytest.mark.asyncio
    async def test_pagination_links_first(self, app_with_posts):
        """Test first link in pagination links."""
        client, _ = app_with_posts

        for i in range(5):
            client.post("/api/posts", json={"title": f"Post {i}"})

        resp = client.get("/api/posts?limit=2&offset=4")
        data = resp.json()

        assert "first" in data["links"]
        assert "offset=0" in data["links"]["first"]

    @pytest.mark.asyncio
    async def test_pagination_links_last(self, app_with_posts):
        """Test last link in pagination links."""
        client, _ = app_with_posts

        for i in range(10):
            client.post("/api/posts", json={"title": f"Post {i}"})

        resp = client.get("/api/posts?limit=3&offset=0")
        data = resp.json()

        assert "last" in data["links"]
        assert data["pagination"]["total_pages"] == 4
        assert "offset=9" in data["links"]["last"]

    @pytest.mark.asyncio
    async def test_pagination_preserves_query_params_in_links(self, app_with_posts):
        """Test that other query params are preserved in pagination links."""
        client, _ = app_with_posts

        for i in range(5):
            client.post("/api/posts", json={"title": f"Post {i}", "views": 0})

        resp = client.get("/api/posts?limit=2&offset=0&views=0")
        data = resp.json()

        assert "views=0" in data["links"]["self"]
        assert data["pagination"]["has_more"] is True
        assert data["links"]["next"] is not None
        assert "views=0" in data["links"]["next"]

    @pytest.mark.asyncio
    async def test_pagination_with_empty_results(self, app_with_posts):
        """Test pagination metadata when no results."""
        client, _ = app_with_posts

        resp = client.get("/api/posts?limit=10&offset=0")
        data = resp.json()

        assert data["pagination"]["total"] == 0
        assert data["pagination"]["has_more"] is False
        assert data["pagination"]["next_offset"] is None
        assert data["pagination"]["prev_offset"] is None
        assert data["pagination"]["page"] == 1
        assert data["pagination"]["total_pages"] == 1

    @pytest.mark.asyncio
    async def test_pagination_exact_page(self, app_with_posts):
        """Test pagination when items fill exact number of pages."""
        client, _ = app_with_posts

        for i in range(6):
            client.post("/api/posts", json={"title": f"Post {i}"})

        resp = client.get("/api/posts?limit=3&offset=3")
        data = resp.json()

        assert data["pagination"]["total"] == 6
        assert data["pagination"]["total_pages"] == 2
        assert data["pagination"]["page"] == 2
        assert data["pagination"]["has_more"] is False
        assert data["pagination"]["next_offset"] is None


class TestPaginationFlexibility:
    """Tests for flexible pagination configuration."""

    @pytest.mark.asyncio
    async def test_pagination_disabled_at_collection_level(self, app_with_pagination_disabled):
        """Test pagination disabled at collection level."""
        client, _ = app_with_pagination_disabled

        for i in range(5):
            client.post("/api/posts", json={"title": f"Post {i}"})

        resp = client.get("/api/posts")
        data = resp.json()

        assert "pagination" not in data
        assert "links" not in data
        assert "items" in data

    @pytest.mark.asyncio
    async def test_pagination_auto_mode_first_page_no_next(self, app_with_pagination_auto):
        """Test auto mode doesn't include pagination on first page with no next."""
        client, _ = app_with_pagination_auto

        for i in range(3):
            client.post("/api/posts", json={"title": f"Post {i}"})

        resp = client.get("/api/posts?limit=10&offset=0")
        data = resp.json()

        assert "pagination" not in data
        assert "links" not in data

    @pytest.mark.asyncio
    async def test_pagination_auto_mode_has_more(self, app_with_pagination_auto):
        """Test auto mode includes pagination when has_more is true."""
        client, _ = app_with_pagination_auto

        for i in range(5):
            client.post("/api/posts", json={"title": f"Post {i}"})

        resp = client.get("/api/posts?limit=2&offset=0")
        data = resp.json()

        assert "pagination" in data
        assert "links" in data

    @pytest.mark.asyncio
    async def test_pagination_auto_mode_second_page(self, app_with_pagination_auto):
        """Test auto mode includes pagination on second page."""
        client, _ = app_with_pagination_auto

        for i in range(5):
            client.post("/api/posts", json={"title": f"Post {i}"})

        resp = client.get("/api/posts?limit=2&offset=2")
        data = resp.json()

        assert "pagination" in data
        assert "links" in data

    @pytest.mark.asyncio
    async def test_query_override_disable_pagination(self, app_with_posts):
        """Test query parameter can disable pagination."""
        client, _ = app_with_posts

        for i in range(5):
            client.post("/api/posts", json={"title": f"Post {i}"})

        resp = client.get("/api/posts?pagination=false")
        data = resp.json()

        assert "pagination" not in data
        assert "links" not in data

    @pytest.mark.asyncio
    async def test_query_override_enable_pagination(self, app_with_pagination_disabled):
        """Test query parameter can enable pagination when disabled."""
        client, _ = app_with_pagination_disabled

        for i in range(5):
            client.post("/api/posts", json={"title": f"Post {i}"})

        resp = client.get("/api/posts?pagination=true")
        data = resp.json()

        assert "pagination" in data
        assert "links" in data

    @pytest.mark.asyncio
    async def test_paginate_method_on_collection(self, db_path):
        """Test paginate() method on Collection."""
        db = Database(db_path)
        await db.connect()
        store = CollectionStore(db)

        posts = Collection(
            "posts",
            fields=[TextField("title", required=True)],
        ).paginate(False)

        await store.sync_schema(posts)

        collections = {"posts": (posts, {"read": "public", "write": "public"})}
        routes = build_collection_routes(collections, store)
        app = Starlette(routes=routes)
        app = build_middleware_stack(app)

        client = TestClient(app)

        for i in range(3):
            client.post("/api/posts", json={"title": f"Post {i}"})

        resp = client.get("/api/posts")
        data = resp.json()

        assert "pagination" not in data
        assert "links" not in data

        await db.disconnect()

    @pytest.mark.asyncio
    async def test_get_pagination_config(self, db_path):
        """Test get_pagination_config() method."""
        posts = Collection("posts", fields=[TextField("title")], pagination=False)
        assert posts.get_pagination_config() is False

        posts = Collection("posts", fields=[TextField("title")], pagination=True)
        assert posts.get_pagination_config() is True

        posts = Collection("posts", fields=[TextField("title")], pagination="auto")
        assert posts.get_pagination_config() == "auto"

        posts = Collection("posts", fields=[TextField("title")])
        assert posts.get_pagination_config() is True

        posts = Collection("posts", fields=[TextField("title")]).paginate("auto")
        assert posts.get_pagination_config() == "auto"
