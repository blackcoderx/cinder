# Field Types

Fields define the structure of your collection data. Each field type maps to a database column type and has validation options.

## Common Options

All field types share these base options:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `required` | bool | `False` | Field must be provided on create |
| `default` | Any | `None` | Value used when field is not provided |
| `unique` | bool | `False` | Enforce database-level uniqueness |
| `indexed` | bool | `False` | Create database index for faster queries |

## TextField

Stores a UTF-8 string of any length.

```python
from zork import TextField

TextField("title", required=True)
TextField("slug", unique=True, indexed=True)
TextField("bio", default="")
TextField("username", min_length=3, max_length=32)
```

**Extra options:**

| Option | Type | Description |
|--------|------|-------------|
| `min_length` | int | Minimum character count |
| `max_length` | int | Maximum character count |

## IntField

Stores a 64-bit integer.

```python
from zork import IntField

IntField("age")
IntField("priority", required=True)
IntField("score", default=0)
IntField("rating", min_value=1, max_value=5)
```

**Extra options:**

| Option | Type | Description |
|--------|------|-------------|
| `min_value` | int | Minimum allowed value |
| `max_value` | int | Maximum allowed value |

## FloatField

Stores a double-precision floating-point number.

```python
from zork import FloatField

FloatField("price", required=True, min_value=0.0)
FloatField("latitude")
FloatField("longitude")
FloatField("rating", min_value=0.0, max_value=5.0)
```

**Extra options:**

| Option | Type | Description |
|--------|------|-------------|
| `min_value` | float | Minimum allowed value |
| `max_value` | float | Maximum allowed value |

## BoolField

Stores a boolean value. SQLite stores booleans as integers (0 or 1).

```python
from zork import BoolField

BoolField("is_active", default=True)
BoolField("is_featured")
BoolField("is_published", default=False)
```

## DateTimeField

Stores a datetime as an ISO 8601 formatted string.

```python
from zork import DateTimeField

DateTimeField("published_at")
DateTimeField("expires_at", required=True)
DateTimeField("last_modified", auto_now=True)
```

**Extra options:**

| Option | Type | Description |
|--------|------|-------------|
| `auto_now` | bool | Automatically set to current time on every update |

When `auto_now=True`, the field value is automatically updated to the current timestamp whenever the record is modified.

## URLField

Stores a URL string, validated by Pydantic.

```python
from zork import URLField

URLField("website")
URLField("blog_url")
URLField("avatar_url", required=True)
```

The value must be a valid URL format.

## JSONField

Stores arbitrary JSON data as a serialized string.

```python
from zork import JSONField

JSONField("metadata")
JSONField("config", default={})
JSONField("tags", default=[])
JSONField("settings", default={"theme": "light"})
```

The value can be any JSON-serializable Python type: dict, list, str, int, float, bool, or None.

## FileField

Stores file upload metadata. The actual file bytes are stored in the configured storage backend.

```python
from zork import FileField

# Avatar upload (single image)
FileField("avatar", max_size=2_000_000, allowed_types=["image/*"], public=True)

# Document attachments (multiple PDFs)
FileField("documents", multiple=True, allowed_types=["application/pdf"])

# Generic file upload
FileField("attachment")
```

**Extra options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `max_size` | int | 10000000 | Maximum file size in bytes (10 MB) |
| `allowed_types` | list[str] | `["*/*"]` | MIME types to accept |
| `multiple` | bool | `False` | Allow multiple files |
| `public` | bool | `False` | No auth required for download |

### Allowed Types Examples

```python
# Any file type
FileField("file")

# Images only
FileField("image", allowed_types=["image/*"])

# Specific types
FileField("document", allowed_types=["application/pdf", "application/msword"])

# Videos
FileField("video", allowed_types=["video/*"])
```

### File Upload Endpoints

When you add a FileField, Zork automatically creates upload/download endpoints:

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/{collection}/{id}/files/{field}` | Upload file(s) |
| GET | `/api/{collection}/{id}/files/{field}` | Download file(s) |
| DELETE | `/api/{collection}/{id}/files/{field}` | Delete file(s) |

See the [File Storage](/file-storage/setup) guide for storage backend configuration.

## RelationField

Stores a reference to a record in another collection.

```python
from zork import RelationField

RelationField("author", collection="users")
RelationField("category", collection="categories", required=True)
RelationField("parent", collection="posts")  # Self-referential
```

See the [Relations](/core-concepts/relations) guide for details on using relations.

## Field Examples

### User Profile

```python
users = Collection("users", fields=[
    TextField("username", required=True, unique=True, min_length=3, max_length=20),
    TextField("email", required=True, unique=True),
    TextField("password_hash"),
    TextField("avatar_url"),
    URLField("website"),
    DateTimeField("joined_at", auto_now=True),
    BoolField("is_admin", default=False),
])
```

### Blog Post

```python
posts = Collection("posts", fields=[
    TextField("title", required=True),
    TextField("slug", required=True, unique=True, indexed=True),
    TextField("content"),
    TextField("excerpt"),
    URLField("cover_image"),
    RelationField("author", collection="users"),
    RelationField("category", collection="categories"),
    JSONField("tags", default=[]),
    IntField("view_count", default=0),
    BoolField("is_published", default=False),
    DateTimeField("published_at"),
])
```

### E-commerce Product

```python
products = Collection("products", fields=[
    TextField("name", required=True),
    TextField("description"),
    FloatField("price", required=True, min_value=0.0),
    FloatField("weight_kg"),
    IntField("stock", default=0, min_value=0),
    TextField("sku", required=True, unique=True),
    BoolField("is_active", default=True),
    JSONField("attributes", default={}),
])
```

## Next Steps

- [Relations](/core-concepts/relations) — Link collections together
- [File Storage](/file-storage/setup) — Configure file upload storage
- [Validation](/core-concepts/lifecycle-hooks) — Add custom validation in hooks
