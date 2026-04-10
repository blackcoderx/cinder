---
title: Field Types
description: Available field types for defining your data schema
---

Cinder provides various field types for defining your data schema.

## Available Field Types

| Type | SQLite Type | Parameters | Description |
|------|------------|------------|-------------|
| `TextField` | TEXT | `required`, `default`, `unique`, `min_length`, `max_length` | String values |
| `IntField` | INTEGER | `required`, `default`, `unique`, `min_value`, `max_value` | Integer values |
| `FloatField` | REAL | `required`, `default`, `unique`, `min_value`, `max_value` | Floating-point values |
| `BoolField` | INTEGER | `required`, `default`, `unique` | Boolean values (stored as 0/1) |
| `DateTimeField` | TEXT | `required`, `default`, `unique`, `auto_now` | ISO 8601 datetime strings |
| `URLField` | TEXT | `required`, `default`, `unique` | Validated URL strings |
| `JSONField` | TEXT | `required`, `default` | Arbitrary JSON data |
| `RelationField` | TEXT | `required`, `unique`, `collection` | Foreign key reference |
| `FileField` | TEXT | `max_size`, `allowed_types`, `multiple`, `public` | File uploads |

## Common Parameters

All field types accept:

- `required` (bool) — Field must be provided on create. Default: `False`
- `default` (any) — Default value when field is not provided. Default: `None`
- `unique` (bool) — Enforce uniqueness in the database. Default: `False`

## Examples

### TextField

```python
TextField("name", required=True, max_length=200)
TextField("slug", unique=True)
TextField("bio", default="No bio yet")
TextField("code", min_length=10, max_length=5000)
```

### IntField

```python
IntField("age", required=True, min_value=0, max_value=150)
IntField("views", default=0)
IntField("quantity", unique=True)
```

### FloatField

```python
FloatField("price", required=True, min_value=0)
FloatField("rating", min_value=0.0, max_value=5.0)
FloatField("latitude")
FloatField("longitude")
```

### BoolField

```python
BoolField("is_published", default=False)
BoolField("is_active", default=True)
BoolField("is_featured", required=True)
```

### DateTimeField

```python
# Auto-set to current time on create
DateTimeField("created_at", auto_now=True)

# Optional with default
DateTimeField("published_at", default=None)

# Required
DateTimeField("scheduled_at", required=True)
```

### URLField

```python
URLField("website")
URLField("github", required=True)
```

### JSONField

```python
JSONField("metadata", default={})
JSONField("config", default={"theme": "dark"})
JSONField("tags", default=[])
```

## Full Collection Example

```python
from cinder import Collection, TextField, IntField, FloatField, BoolField
from cinder import DateTimeField, URLField, JSONField, RelationField

articles = Collection("articles", fields=[
    TextField("title", required=True, min_length=1, max_length=200),
    TextField("slug", unique=True),
    TextField("content", required=True),
    IntField("views", default=0, min_value=0),
    FloatField("score", min_value=0.0, max_value=10.0),
    BoolField("is_published", default=False),
    DateTimeField("published_at", auto_now=True),
    URLField("source_url"),
    JSONField("metadata", default={}),
])

app.register(articles, auth=["read:public", "write:authenticated"])
```

## Next Steps

- [Relations](/fields/relations/) — Connect collections with foreign keys
- [File Storage](/file-storage/setup/) — Handle file uploads
- [Collections](/core-concepts/collections/) — Using fields in collections