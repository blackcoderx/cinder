---
title: Collections
description: Define schemas that Zeno turns into full CRUD APIs
---

A `Collection` maps a Python schema to a database table and a complete set of REST endpoints. You define the shape of your data; Zeno handles the rest.

## Defining a collection

```python
from zeno import Collection, TextField, IntField, BoolField

articles = Collection("articles", fields=[
    TextField("title", required=True),
    TextField("body"),
    IntField("view_count", default=0),
    BoolField("published", default=False),
])
```

## Naming rules

The collection name becomes both the table name and the URL segment:

- `Collection("articles")` → table `articles`, endpoints at `/api/articles`
- Use lowercase letters, numbers, and underscores
- Must be unique across all registered collections

## Auto-generated columns

Every collection automatically gets three extra columns you do not need to declare:

| Column | Type | Description |
|--------|------|-------------|
| `id` | `TEXT` (UUID) | Auto-generated UUID primary key |
| `created_at` | `TEXT` (ISO 8601) | Set on insert, never changed |
| `updated_at` | `TEXT` (ISO 8601) | Updated on every `PATCH` |

## Auto-generated endpoints

Registering a collection wires up five routes:

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/{name}` | List records with filtering, pagination, sorting |
| `POST` | `/api/{name}` | Create a new record |
| `GET` | `/api/{name}/{id}` | Get a single record by ID |
| `PATCH` | `/api/{name}/{id}` | Partial update (only provided fields change) |
| `DELETE` | `/api/{name}/{id}` | Delete a record |

## Registering a collection

```python
app.register(articles)

# With access control
app.register(articles, auth=["read:public", "write:authenticated"])
```

See [Access Control](/core-concepts/access-control/) for all available rules.

## Composite indexes

Declare multi-column indexes for queries that filter or sort on combinations of fields:

```python
posts = Collection(
    "posts",
    fields=[
        TextField("author_id"),
        TextField("status"),
        DateTimeField("published_at"),
    ],
    indexes=[
        ("author_id", "status"),         # index on (author_id, status)
        ("status", "published_at"),      # index on (status, published_at)
    ],
)
```

## Registering hooks on a collection

```python
@articles.on("before_create")
async def add_slug(data, ctx):
    data["slug"] = data["title"].lower().replace(" ", "-")
    return data
```

See [Lifecycle Hooks](/core-concepts/lifecycle-hooks/) for all available events.

## Schema auto-sync

When you start your app, Zeno compares the `Collection` definition against the live database schema and adds any missing columns. Removed columns are left in place (non-destructive). For larger structural changes, use [Migrations](/migrations/commands/).
