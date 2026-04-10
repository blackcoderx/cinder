---
title: Collections
description: Define your data schema and auto-generate REST APIs
---

A **Collection** is the core building block in Cinder. It defines a data schema that Cinder transforms into both a database table and a full REST API.

## The Mental Model

Think of a collection like a spreadsheet:

```
Collection "users"
┌──────────┬────────────────────┬──────────┬─────────────────────────┐
│    id    │        email        │   name   │       created_at        │
├──────────┼────────────────────┼──────────┼─────────────────────────┤
│  uuid-1  │  alice@example.com  │   Alice  │   2026-04-10T10:00:00Z  │
│  uuid-2  │    bob@example.com  │    Bob   │   2026-04-10T11:00:00Z  │
└──────────┴────────────────────┴──────────┴─────────────────────────┘
       ↑              ↑                 ↑                ↑
   SYSTEM         YOUR FIELDS         YOUR FIELDS       SYSTEM
   FIELD          (you define)         (you define)      FIELD
```

You define the columns (fields), Cinder handles everything else.

## Basic Syntax

```python
from cinder import Collection, TextField, IntField, FloatField, BoolField

products = Collection("products", fields=[
    TextField("name", required=True, max_length=200),
    TextField("description"),
    FloatField("price", required=True, min_value=0),
    IntField("stock", default=0),
    BoolField("is_published", default=False),
])
```

Then register it with your app:

```python
app = Cinder(database="app.db")
app.register(products, auth=["read:public", "write:authenticated"])
```

Cinder automatically creates:
- A database table with your fields
- CRUD API endpoints at `/api/products`
- Input validation based on field constraints

## System Fields

Every collection automatically includes three system fields:

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID v4 string | Unique identifier, auto-generated on create |
| `created_at` | ISO 8601 timestamp | Set automatically when the record is created |
| `updated_at` | ISO 8601 timestamp | Updated automatically on every PATCH request |

Example response:

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "My Post",
  "created_at": "2026-04-10T12:00:00Z",
  "updated_at": "2026-04-10T12:00:00Z"
}
```

## Alternative Syntax: Class-Based

For more complex collections, use the class-based syntax:

```python
from cinder import Collection, TextField, IntField, DateTimeField, BoolField

class Article(Collection):
    title = TextField(required=True, max_length=200)
    slug = TextField(unique=True)  # URL-friendly identifier
    content = TextField()
    published_at = DateTimeField()  # Nullable - set manually
    views = IntField(default=0)
    is_draft = BoolField(default=True)

app.register(Article, auth=["read:public", "write:authenticated"])
```

This syntax allows you to reference fields by name (`Article.title`) and add class-level configuration like indexes.

## Indexes

Indexes improve query performance on frequently filtered columns.

### Single-Column Index

Add `indexed=True` to any field:

```python
class Posts(Collection):
    title = TextField(required=True)
    category = TextField(indexed=True)  # Faster filtering by category
    status = TextField(indexed=True)    # Faster filtering by status
    created_at = TextField()            # No index
```

### Composite Index

For queries that filter on multiple columns together:

```python
class Posts(Collection):
    title = TextField(required=True)
    category = TextField()
    status = TextField()
    created_at = TextField()

    indexes = [
        ("category", "status"),           # Filter by category AND status
        ("category", "created_at"),       # Filter by category AND date
    ]
```

### When to Index

| Scenario | Index? | Reason |
|----------|--------|--------|
| Primary lookups (by ID) | Built-in | System field, always indexed |
| Frequently filtered columns | Yes | Faster WHERE clause queries |
| Unique constraints | Built-in | `unique=True` creates a constraint |
| Columns with low cardinality (e.g., boolean) | Usually no | Index overhead > scan cost |
| Sorted columns | Yes | Faster ORDER BY |

## Auth Rules

The `auth` parameter controls access to your collection's endpoints:

```python
app.register(posts, auth=["read:public", "write:authenticated"])
```

| Rule | Meaning |
|------|---------|
| `read:public` | Anyone can read (no auth required) |
| `read:authenticated` | Only logged-in users can read |
| `read:owner` | Users can only read records they created |
| `read:admin` | Only admins can read |
| `write:public` | Anyone can create/update/delete |
| `write:authenticated` | Only logged-in users can write |
| `write:owner` | Users can only modify their own records |
| `write:admin` | Only admins can write |

See [Access Control](/core-concepts/access-control/) for detailed examples.

## Multiple Auth Rules

Combine rules for flexible access:

```python
app.register(posts, auth=[
    "read:public",            # Everyone can read
    "write:authenticated",    # Logged-in users can write
    "read:admin",             # Admins can also see hidden data
])
```

Access is granted if **any** rule permits it (OR logic).

## Common Patterns

### Public Content with Protected Writes

```python
articles = Collection("articles", fields=[
    TextField("title", required=True),
    TextField("content"),
])
app.register(articles, auth=["read:public", "write:authenticated"])
```

### Private Content

```python
notes = Collection("notes", fields=[
    TextField("title", required=True),
    TextField("content"),
])
app.register(notes, auth=["read:owner", "write:owner"])
# Users can only see/edit their own notes
```

### Admin-Only Content

```python
config = Collection("config", fields=[
    TextField("key", required=True),
    TextField("value"),
])
app.register(config, auth=["read:admin", "write:admin"])
# Only users with role="admin" can access
```

## Next Steps

- [Field Types](/fields/field-types/) — All available field definitions
- [Relations](/core-concepts/relations/) — Link collections together
- [Access Control](/core-concepts/access-control/) — Fine-grained permissions
- [Schema Auto-Sync](/core-concepts/schema-autosync/) — How Cinder handles schema changes
