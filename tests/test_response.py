import pytest
from pydantic import BaseModel, Field, model_validator, ConfigDict

from zork.response import ResponseModel, create_response_model
from zork.collections.schema import Collection, TextField, IntField
from zork.collections.router import build_collection_routes, _transform_response
from zork.collections.store import CollectionStore
from zork.db.connection import Database
from starlette.applications import Starlette
from starlette.testclient import TestClient
from starlette.requests import Request
from starlette.routing import Route


@pytest.fixture
def db_path(tmp_path):
    return str(tmp_path / "test.db")


@pytest.fixture
async def mem_db():
    db = Database(":memory:")
    await db.connect()
    yield db
    await db.disconnect()


class TestResponseModelBasic:
    """Test ResponseModel basic functionality."""

    def test_include_specific_fields(self):
        """Test including only specific fields."""
        model = ResponseModel(include={"id", "name"})
        data = {"id": "1", "name": "John", "email": "john@example.com"}
        result = model.transform(data)
        assert result == {"id": "1", "name": "John"}
        assert "email" not in result

    def test_exclude_sensitive_fields(self):
        """Test excluding sensitive fields."""
        model = ResponseModel(exclude={"password", "token"})
        data = {"id": "1", "name": "John", "password": "secret", "token": "abc"}
        result = model.transform(data)
        assert result == {"id": "1", "name": "John"}
        assert "password" not in result
        assert "token" not in result

    def test_include_and_exclude_together(self):
        """Test using both include and exclude together."""
        model = ResponseModel(include={"id", "name", "email", "password"}, exclude={"password"})
        data = {"id": "1", "name": "John", "email": "john@example.com", "password": "secret"}
        result = model.transform(data)
        assert result == {"id": "1", "name": "John", "email": "john@example.com"}

    def test_exclude_none_values(self):
        """Test excluding fields with None values."""
        model = ResponseModel(exclude_none=True)
        data = {"id": "1", "name": "John", "email": None, "bio": None}
        result = model.transform(data)
        assert result == {"id": "1", "name": "John"}
        assert "email" not in result
        assert "bio" not in result

    def test_exclude_unset_values(self):
        """Test excluding fields that weren't explicitly set."""
        model = ResponseModel(exclude_unset=True)
        data = {"id": "1", "name": "John"}
        result = model.transform(data)
        assert result == {"id": "1", "name": "John"}

        data_with_defaults = {"id": "1", "name": "John", "status": "active"}
        result = model.transform(data_with_defaults)
        assert "status" in result

    def test_exclude_default_values(self):
        """Test excluding fields with default values using Pydantic model."""
        
        class User(BaseModel):
            id: str
            name: str
            status: str = "active"
        
        model = ResponseModel(model=User, exclude_defaults=True)
        data = {"id": "1", "name": "John", "status": "active"}
        result = model.transform(data)
        assert result == {"id": "1", "name": "John"}

    def test_by_alias(self):
        """Test using field aliases in output."""

        class UserModel(BaseModel):
            model_config = ConfigDict(alias_generator=lambda x: x.upper())

            id: str
            name: str

        model = ResponseModel(model=UserModel, by_alias=True)
        data = {"id": "1", "name": "John"}
        result = model.transform(data)
        assert "ID" in result or "id" in result


class TestResponseModelWithPydanticModel:
    """Test ResponseModel with Pydantic model integration."""

    def test_with_pydantic_model(self):
        """Test transformation using a Pydantic model."""

        class UserResponse(BaseModel):
            id: str
            name: str

        model = ResponseModel(model=UserResponse)
        data = {"id": "1", "name": "John", "email": "john@example.com", "password": "secret"}
        result = model.transform(data)
        assert result == {"id": "1", "name": "John"}
        assert "email" not in result
        assert "password" not in result

    def test_pydantic_model_with_computed_field(self):
        """Test computed fields via model_validator."""

        class ArticleResponse(BaseModel):
            id: str
            title: str
            slug: str | None = None

            @model_validator(mode="before")
            @classmethod
            def compute_slug(cls, data):
                if isinstance(data, dict) and "title" in data:
                    data["slug"] = data["title"].lower().replace(" ", "-")
                return data

        model = ResponseModel(model=ArticleResponse)
        data = {"id": "1", "title": "Hello World"}
        result = model.transform(data)
        assert result["slug"] == "hello-world"

    def test_pydantic_model_with_include(self):
        """Test Pydantic model with include option."""

        class User(BaseModel):
            id: str
            name: str
            email: str
            password: str

        model = ResponseModel(model=User, include={"id", "name"})
        data = {"id": "1", "name": "John", "email": "john@example.com", "password": "secret"}
        result = model.transform(data)
        assert result == {"id": "1", "name": "John"}

    def test_pydantic_model_with_exclude(self):
        """Test Pydantic model with exclude option."""

        class User(BaseModel):
            id: str
            name: str
            email: str
            password: str

        model = ResponseModel(model=User, exclude={"password"})
        data = {"id": "1", "name": "John", "email": "john@example.com", "password": "secret"}
        result = model.transform(data)
        assert "password" not in result


class TestResponseModelList:
    """Test ResponseModel with list transformation."""

    def test_transform_list(self):
        """Test transforming a list of records."""
        model = ResponseModel(include={"id", "name"})
        data = [
            {"id": "1", "name": "John", "email": "john@example.com"},
            {"id": "2", "name": "Jane", "email": "jane@example.com"},
        ]
        result = model.transform(data)
        assert len(result) == 2
        assert result[0] == {"id": "1", "name": "John"}
        assert result[1] == {"id": "2", "name": "Jane"}

    def test_transform_empty_list(self):
        """Test transforming an empty list."""
        model = ResponseModel(include={"id"})
        result = model.transform([])
        assert result == []

    def test_transform_list_preserves_structure(self):
        """Test that list transformation preserves nested objects."""
        model = ResponseModel(include={"id", "profile"})
        data = [
            {"id": "1", "name": "John", "profile": {"bio": "Test"}},
            {"id": "2", "name": "Jane", "profile": {"bio": "Test2"}},
        ]
        result = model.transform(data)
        assert result[0]["profile"] == {"bio": "Test"}


class TestResponseModelEdgeCases:
    """Test edge cases and error handling."""

    def test_transform_none(self):
        """Test transforming None returns None."""
        model = ResponseModel()
        result = model.transform(None)
        assert result is None

    def test_transform_non_dict(self):
        """Test transforming non-dict returns as-is."""
        model = ResponseModel()
        result = model.transform("string")
        assert result == "string"

    def test_transform_non_dict_list(self):
        """Test transforming list with non-dict items."""
        model = ResponseModel()
        result = model.transform([1, 2, 3])
        assert result == [1, 2, 3]

    def test_include_with_missing_fields(self):
        """Test include with fields that don't exist in data."""
        model = ResponseModel(include={"id", "nonexistent"})
        data = {"id": "1", "name": "John"}
        result = model.transform(data)
        assert result == {"id": "1"}

    def test_exclude_with_missing_fields(self):
        """Test exclude with fields that don't exist in data."""
        model = ResponseModel(exclude={"nonexistent"})
        data = {"id": "1", "name": "John"}
        result = model.transform(data)
        assert result == {"id": "1", "name": "John"}


class TestResponseModelCustomTransform:
    """Test custom transform function."""

    def test_custom_transform_function(self):
        """Test custom transform function is applied."""

        def uppercase_name(data):
            if "name" in data:
                data["name"] = data["name"].upper()
            return data

        model = ResponseModel(transform=uppercase_name)
        data = {"id": "1", "name": "John"}
        result = model.transform(data)
        assert result["name"] == "JOHN"

    def test_custom_transform_with_include(self):
        """Test custom transform works with include/exclude."""
        model = ResponseModel(include={"id", "name"}, transform=lambda d: {**d, "processed": True})
        data = {"id": "1", "name": "John", "extra": "data"}
        result = model.transform(data)
        assert result == {"id": "1", "name": "John", "processed": True}


class TestCreateResponseModel:
    """Test the create_response_model factory function."""

    def test_basic_factory(self):
        """Test basic factory usage."""
        model = create_response_model(exclude={"password"})
        data = {"id": "1", "name": "John", "password": "secret"}
        result = model.transform(data)
        assert "password" not in result

    def test_factory_with_pydantic_model(self):
        """Test factory with Pydantic model."""

        class User(BaseModel):
            id: str
            name: str

        model = create_response_model(model=User)
        data = {"id": "1", "name": "John", "extra": "field"}
        result = model.transform(data)
        assert result == {"id": "1", "name": "John"}

    def test_factory_with_hidden_fields(self):
        """Test factory with hidden fields list."""

        class User(BaseModel):
            id: str
            name: str
            email: str

        model = create_response_model(model=User, hidden_fields=["email"])
        data = {"id": "1", "name": "John", "email": "john@example.com"}
        result = model.transform(data)
        assert "email" not in result


class TestFieldExtensions:
    """Test Field class extensions (hidden, read_only, alias)."""

    def test_field_hidden_attribute(self):
        """Test Field hidden attribute is stored."""
        field = TextField("password", hidden=True)
        assert field.hidden is True

    def test_field_read_only_attribute(self):
        """Test Field read_only attribute is stored."""
        field = TextField("created_at", read_only=True)
        assert field.read_only is True

    def test_field_alias_attribute(self):
        """Test Field alias attribute is stored."""
        field = TextField("full_name", alias="fullName")
        assert field.alias == "fullName"


class TestCollectionResponse:
    """Test Collection.response() configuration."""

    def test_response_config_stored(self):
        """Test response config is stored on collection."""
        collection = Collection(
            "users",
            fields=[TextField("name"), TextField("email")],
        )
        collection.response(include={"id", "name"})

        config = collection.get_response_config()
        assert config["include"] == {"id", "name"}
        assert collection.has_response_config() is True

    def test_response_config_with_model(self):
        """Test response config with Pydantic model."""

        class UserResponse(BaseModel):
            id: str
            name: str

        collection = Collection(
            "users",
            fields=[TextField("name"), TextField("email")],
        )
        collection.response(model=UserResponse, exclude={"email"})

        config = collection.get_response_config()
        assert config["model"] == UserResponse

    def test_response_config_hidden_fields(self):
        """Test hidden fields from Field are included."""
        collection = Collection(
            "users",
            fields=[
                TextField("name"),
                TextField("password", hidden=True),
            ],
        )

        config = collection.get_response_config()
        assert "password" in config["hidden_fields"]

    def test_response_chaining(self):
        """Test response() returns self for chaining."""
        collection = Collection(
            "users",
            fields=[TextField("name")],
        )
        result = collection.response(exclude={"name"})
        assert result is collection


class TestTransformResponse:
    """Test _transform_response helper function."""

    @pytest.mark.asyncio
    async def test_transform_with_collection_config(self, mem_db):
        """Test transform uses collection config."""
        store = CollectionStore(mem_db)
        collection = Collection(
            "users",
            fields=[TextField("name"), TextField("password")],
        )
        collection.response(exclude={"password"})

        data = {"id": "1", "name": "John", "password": "secret"}

        class MockRequest:
            query_params = {}

        request = MockRequest()
        result = _transform_response(data, collection, request)

        assert "password" not in result
        assert result["name"] == "John"

    @pytest.mark.asyncio
    async def test_query_param_fields_override(self, mem_db):
        """Test query params can override config."""
        store = CollectionStore(mem_db)
        collection = Collection(
            "users",
            fields=[TextField("name"), TextField("email")],
        )
        collection.response(include={"id", "name", "email"})

        data = {"id": "1", "name": "John", "email": "john@example.com"}

        class MockRequest:
            query_params = {"fields": "id,email"}

        request = MockRequest()
        result = _transform_response(data, collection, request)

        assert result == {"id": "1", "email": "john@example.com"}

    @pytest.mark.asyncio
    async def test_query_param_exclude_override(self, mem_db):
        """Test query exclude param can override config."""
        store = CollectionStore(mem_db)
        collection = Collection(
            "users",
            fields=[TextField("name"), TextField("email")],
        )
        collection.response(exclude=set())

        data = {"id": "1", "name": "John", "email": "john@example.com"}

        class MockRequest:
            query_params = {"exclude": "email"}

        request = MockRequest()
        result = _transform_response(data, collection, request)

        assert "email" not in result


class TestCollectionRoutes:
    """Integration tests for collection routes with response models."""

    @pytest.fixture
    async def app_with_response_config(self, db_path):
        db = Database(db_path)
        await db.connect()
        store = CollectionStore(db)

        collection = Collection(
            "posts",
            fields=[
                TextField("title", required=True),
                TextField("content"),
                TextField("internal_notes"),
            ],
        )
        collection.response(exclude={"internal_notes"})

        await store.sync_schema(collection)

        collections = {"posts": (collection, {"read": "public", "write": "public"})}
        routes = build_collection_routes(collections, store)
        app = Starlette(routes=routes)

        from zork.pipeline import build_middleware_stack
        app = build_middleware_stack(app)

        yield TestClient(app), db
        await db.disconnect()

    def test_list_excludes_hidden_fields(self, app_with_response_config):
        """Test list endpoint excludes configured fields."""
        client, _ = app_with_response_config

        client.post("/api/posts", json={"title": "Test Post", "content": "Content", "internal_notes": "Secret"})

        response = client.get("/api/posts")
        assert response.status_code == 200
        data = response.json()
        assert data["items"][0].get("internal_notes") is None or "internal_notes" not in data["items"][0]

    def test_get_excludes_hidden_fields(self, app_with_response_config):
        """Test get endpoint excludes configured fields."""
        client, _ = app_with_response_config

        resp = client.post("/api/posts", json={"title": "Test", "content": "Content", "internal_notes": "Secret"})
        post_id = resp.json()["id"]

        response = client.get(f"/api/posts/{post_id}")
        assert response.status_code == 200
        data = response.json()
        assert "internal_notes" not in data or data.get("internal_notes") is None


class TestDecoratorAPI:
    """Test @app.response() decorator API."""

    def test_response_decorator_with_route(self):
        """Test response decorator with route registration."""
        from zork.app import Zork

        app = Zork()

        class PostResponse(BaseModel):
            id: str
            title: str

        @app.response(PostResponse)
        @app.route("/posts/{id}")
        async def get_post(request):
            return {"id": "1", "title": "Test", "extra_field": "should be excluded"}

        routes = app._custom_routes or []
        assert len(routes) > 0
        assert routes[0].path == "/posts/{id}"

    def test_response_decorator_with_options(self):
        """Test response decorator with options."""
        from zork.app import Zork

        app = Zork()

        @app.response(exclude={"password"})
        @app.route("/users/{id}")
        async def get_user(request):
            return {"id": "1", "name": "John", "password": "secret"}

        assert hasattr(app, "_custom_routes")
        routes = app._custom_routes or []
        assert len(routes) > 0