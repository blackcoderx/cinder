# Response Models

Control how your API responses are serialized, hide sensitive fields, and add computed properties.

## Overview

Response models let you transform API responses before they're sent to clients. This is essential for:
- Hiding sensitive data (passwords, tokens)
- Adding computed fields
- Controlling serialization options
- Field aliasing (snake_case → camelCase)

## Two APIs

Zork provides two ways to configure response models:

1. **Collection-level** - For auto-generated CRUD routes
2. **Decorator-based** - For custom routes

---

## Collection-Level Configuration

Configure response transformation on your `Collection`:

```python
from pydantic import BaseModel
from zork import Zork, Collection, TextField, IntField

class UserResponse(BaseModel):
    id: str
    name: str
    email: str

users = Collection("users", fields=[
    TextField("name", required=True),
    TextField("email", required=True),
    TextField("password_hash"),
])

# Exclude password from all responses
users.response(
    model=UserResponse,
    exclude={"password_hash"}
)

app = Zork(collections={"users": users})
```

### Field-Level Options

Add `hidden=True` to any field to automatically exclude it:

```python
users = Collection("users", fields=[
    TextField("name", required=True),
    TextField("email"),
    TextField("password", hidden=True),  # Always hidden
])
```

Available field options:
- `hidden: bool` - Always exclude from responses
- `read_only: bool` - Only in responses, not input
- `alias: str` - Rename field in output

### Response Options

```python
collection.response(
    model=UserResponse,
    include={"id", "name", "email"},  # Only these fields
    exclude={"password", "token"},      # Exclude these
    exclude_none=True,                  # Don't include None values
    exclude_unset=True,                 # Don't include unset fields
    exclude_defaults=True,              # Don't include defaults
    by_alias=True,                      # Use field aliases
)
```

---

## Decorator API

For custom routes, use `@app.response()`:

```python
from pydantic import BaseModel
from zork import Zork

app = Zork()

class PostDetail(BaseModel):
    id: str
    title: str
    slug: str          # computed
    view_count: int

    @model_validator(mode="before")
    def compute_slug(cls, data):
        if isinstance(data, dict) and "title" in data:
            data["slug"] = data["title"].lower().replace(" ", "-")
        return data

@app.response(PostDetail, include={"id", "title", "slug"})
@app.route("/posts/{id}")
async def get_post(request):
    return await fetch_post(request.path_params["id"])
```

### Decorator Options

```python
@app.response(
    model=MyModel,
    include={"id", "name"},
    exclude={"password"},
    exclude_none=True,
    exclude_unset=False,
    exclude_defaults=False,
    by_alias=False
)
@app.route("/path")
async def handler(request):
    return data
```

---

## Query Parameter Override

Clients can override response configuration via URL parameters:

```
GET /api/users?fields=id,name&exclude=email
GET /api/posts?exclude_none=true
```

Query params take precedence over server config.

---

## Computed Fields

Use Pydantic's `model_validator` to add computed fields:

```python
from pydantic import BaseModel, model_validator

class ArticleResponse(BaseModel):
    id: str
    title: str
    slug: str | None = None
    reading_time: int | None = None

    @model_validator(mode="before")
    @classmethod
    def compute_fields(cls, data):
        if isinstance(data, dict):
            # Compute slug from title
            if "title" in data:
                data["slug"] = data["title"].lower().replace(" ", "-")
            # Compute reading time from content
            if "content" in data:
                words = len(data["content"].split())
                data["reading_time"] = max(1, words // 200)
        return data
```

---

## Field Aliases

Use `alias` parameter or Pydantic's config:

```python
from pydantic import BaseModel, ConfigDict

class UserResponse(BaseModel):
    model_config = ConfigDict(alias_generator=lambda x: x.upper())
    
    id: str
    full_name: str  # outputs as FULL_NAME
```

Or use field-level aliases:

```python
from zork import Collection, TextField

users = Collection("users", fields=[
    TextField("full_name", alias="fullName"),
])
```

---

## Examples

### Basic Field Exclusion

```python
posts = Collection("posts", fields=[
    TextField("title", required=True),
    TextField("content"),
    TextField("internal_notes"),
])

posts.response(exclude={"internal_notes"})
```

### Multiple Response Models

For the same collection, use query params or create separate endpoints:

```python
# Public response - minimal fields
@app.response(include={"id", "title"})
@app.route("/posts/public")
async def get_public_post(request):
    return await fetch_post(request.path_params["id"])

# Admin response - all fields  
@app.response()
@app.route("/posts/admin/{id}")
async def get_admin_post(request):
    return await fetch_post(request.path_params["id"])
```

### Response Factory

```python
from zork.response import create_response_model
from pydantic import BaseModel

class User(BaseModel):
    id: str
    name: str
    email: str
    password: str

# Create reusable response model
PublicUserResponse = create_response_model(
    model=User,
    exclude={"password"},
    exclude_none=True
)
```