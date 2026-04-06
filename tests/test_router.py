import pytest
from starlette.applications import Starlette
from starlette.testclient import TestClient

from cinder.collections.schema import (
    Collection, TextField, IntField, RelationField,
)
from cinder.collections.store import CollectionStore
from cinder.collections.router import build_collection_routes
from cinder.db.connection import Database
from cinder.pipeline import build_middleware_stack


@pytest.fixture
async def app_with_collection(db_path):
    db = Database(db_path)
    await db.connect()
    store = CollectionStore(db)

    posts = Collection("posts", fields=[
        TextField("title", required=True),
        TextField("body"),
        IntField("views", default=0),
    ])
    await store.sync_schema(posts)

    collections = {"posts": (posts, {"read": "public", "write": "public"})}
    routes = build_collection_routes(collections, store)
    app = Starlette(routes=routes)
    app = build_middleware_stack(app)

    yield TestClient(app), db
    await db.disconnect()


class TestCollectionCRUD:
    @pytest.mark.asyncio
    async def test_create(self, app_with_collection):
        client, _ = app_with_collection
        resp = client.post("/api/posts", json={"title": "Hello", "body": "World"})
        assert resp.status_code == 201
        data = resp.json()
        assert data["title"] == "Hello"
        assert data["views"] == 0
        assert "id" in data

    @pytest.mark.asyncio
    async def test_create_validation_error(self, app_with_collection):
        client, _ = app_with_collection
        resp = client.post("/api/posts", json={"body": "no title"})
        assert resp.status_code == 400

    @pytest.mark.asyncio
    async def test_get_single(self, app_with_collection):
        client, _ = app_with_collection
        created = client.post("/api/posts", json={"title": "Test"}).json()
        resp = client.get(f"/api/posts/{created['id']}")
        assert resp.status_code == 200
        assert resp.json()["title"] == "Test"

    @pytest.mark.asyncio
    async def test_get_not_found(self, app_with_collection):
        client, _ = app_with_collection
        resp = client.get("/api/posts/nonexistent-uuid")
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_list(self, app_with_collection):
        client, _ = app_with_collection
        client.post("/api/posts", json={"title": "A"})
        client.post("/api/posts", json={"title": "B"})
        resp = client.get("/api/posts")
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] == 2
        assert len(data["items"]) == 2

    @pytest.mark.asyncio
    async def test_list_pagination(self, app_with_collection):
        client, _ = app_with_collection
        for i in range(5):
            client.post("/api/posts", json={"title": f"Post {i}"})
        resp = client.get("/api/posts?limit=2&offset=0")
        data = resp.json()
        assert data["total"] == 5
        assert len(data["items"]) == 2
        assert data["limit"] == 2
        assert data["offset"] == 0

    @pytest.mark.asyncio
    async def test_list_filter(self, app_with_collection):
        client, _ = app_with_collection
        client.post("/api/posts", json={"title": "Draft", "views": 0})
        client.post("/api/posts", json={"title": "Popular", "views": 100})
        resp = client.get("/api/posts?views=100")
        data = resp.json()
        assert data["total"] == 1
        assert data["items"][0]["title"] == "Popular"

    @pytest.mark.asyncio
    async def test_update(self, app_with_collection):
        client, _ = app_with_collection
        created = client.post("/api/posts", json={"title": "Old"}).json()
        resp = client.patch(f"/api/posts/{created['id']}", json={"title": "New"})
        assert resp.status_code == 200
        assert resp.json()["title"] == "New"

    @pytest.mark.asyncio
    async def test_update_not_found(self, app_with_collection):
        client, _ = app_with_collection
        resp = client.patch("/api/posts/nonexistent", json={"title": "X"})
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_delete(self, app_with_collection):
        client, _ = app_with_collection
        created = client.post("/api/posts", json={"title": "Delete me"}).json()
        resp = client.delete(f"/api/posts/{created['id']}")
        assert resp.status_code == 200
        resp2 = client.get(f"/api/posts/{created['id']}")
        assert resp2.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_not_found(self, app_with_collection):
        client, _ = app_with_collection
        resp = client.delete("/api/posts/nonexistent")
        assert resp.status_code == 404


class TestExpand:
    @pytest.mark.asyncio
    async def test_expand_relation(self, db_path):
        db = Database(db_path)
        await db.connect()
        store = CollectionStore(db)

        categories = Collection("categories", fields=[
            TextField("name", required=True),
        ])
        products = Collection("products", fields=[
            TextField("name", required=True),
            RelationField("category", collection="categories"),
        ])
        await store.sync_schema(categories)
        await store.sync_schema(products)

        collections = {
            "categories": (categories, {"read": "public", "write": "public"}),
            "products": (products, {"read": "public", "write": "public"}),
        }
        routes = build_collection_routes(collections, store)
        app = Starlette(routes=routes)
        app = build_middleware_stack(app)
        client = TestClient(app)

        cat = client.post("/api/categories", json={"name": "Electronics"}).json()
        prod = client.post("/api/products", json={
            "name": "Phone", "category": cat["id"]
        }).json()

        resp = client.get(f"/api/products/{prod['id']}?expand=category")
        data = resp.json()
        assert "expand" in data
        assert data["expand"]["category"]["name"] == "Electronics"

        await db.disconnect()
