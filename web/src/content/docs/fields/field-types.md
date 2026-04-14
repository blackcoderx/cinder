---
title: Field Types
description: All available field types and their options
---

Fields define the shape of a collection's data. All fields share a common set of base options and then add type-specific constraints.

## Common options

Every field type accepts these parameters:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `required` | `bool` | `False` | Value must be present; field cannot be null |
| `default` | `Any` | `None` | Value used when the field is not provided on create |
| `unique` | `bool` | `False` | Enforce a database-level UNIQUE constraint |
| `indexed` | `bool` | `False` | Create a database index for faster queries |

---

## TextField

Stores a UTF-8 string of arbitrary length.

```python
from zeno import TextField

TextField("title", required=True)
TextField("slug", unique=True, indexed=True)
TextField("bio", default="")
TextField("username", min_length=3, max_length=32)
```

**Extra options:**

| Option | Type | Description |
|--------|------|-------------|
| `min_length` | `int` | Minimum character length (validated by Pydantic) |
| `max_length` | `int` | Maximum character length (validated by Pydantic) |

---

## IntField

Stores a 64-bit integer.

```python
from zeno import IntField

IntField("view_count", default=0)
IntField("score", min_value=0, max_value=100)
IntField("priority", required=True)
```

**Extra options:**

| Option | Type | Description |
|--------|------|-------------|
| `min_value` | `int` | Minimum value (validated by Pydantic) |
| `max_value` | `int` | Maximum value (validated by Pydantic) |

---

## FloatField

Stores a double-precision floating-point number.

```python
from zeno import FloatField

FloatField("price", required=True, min_value=0.0)
FloatField("rating", min_value=0.0, max_value=5.0)
```

**Extra options:**

| Option | Type | Description |
|--------|------|-------------|
| `min_value` | `float` | Minimum value |
| `max_value` | `float` | Maximum value |

---

## BoolField

Stores a boolean. SQLite stores this as `0` or `1`.

```python
from zeno import BoolField

BoolField("is_published", default=False)
BoolField("is_featured")
```

---

## DateTimeField

Stores a datetime as an ISO 8601 string.

```python
from zeno import DateTimeField

DateTimeField("published_at")
DateTimeField("expires_at", required=True)
DateTimeField("last_seen", auto_now=True)
```

**Extra options:**

| Option | Type | Description |
|--------|------|-------------|
| `auto_now` | `bool` | If `True`, automatically set to the current UTC time on every update |

---

## URLField

Stores a URL string, validated by Pydantic's `AnyUrl` validator.

```python
from zeno import URLField

URLField("website")
URLField("avatar_url", required=True)
```

---

## JSONField

Stores arbitrary JSON data as a serialised string.

```python
from zeno import JSONField

JSONField("metadata")
JSONField("config", default={})
JSONField("tags", default=[])
```

The value can be any JSON-serialisable Python type: `dict`, `list`, `str`, `int`, `float`, `bool`, or `None`.

---

## FileField

Stores file upload metadata. The actual file bytes are written to the configured [storage backend](/file-storage/setup/). This field holds only the metadata.

```python
from zeno import FileField

FileField("avatar", max_size=2_000_000, allowed_types=["image/*"], public=True)
FileField("attachments", multiple=True, allowed_types=["application/pdf"])
```

**Extra options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `max_size` | `int` | `10_000_000` | Maximum file size in bytes (10 MB default) |
| `allowed_types` | `list[str]` | `["*/*"]` | MIME type patterns to accept (`"image/*"`, `"application/pdf"`, etc.) |
| `multiple` | `bool` | `False` | If `True`, allows multiple files to be uploaded to this field |
| `public` | `bool` | `False` | If `True`, the download route requires no authentication |

Zeno automatically generates `POST /api/{collection}/{id}/files/{field}`, `GET`, and `DELETE` routes for every `FileField`. See [File Storage](/file-storage/setup/) for full details.

---

## RelationField

Stores a reference to a record in another collection.

```python
from zeno import RelationField

RelationField("author", collection="users")
RelationField("category", collection="categories", required=True)
```

See [Relations](/fields/relations/) for full documentation including expand usage.
