---
title: Indexes
description: Speed up queries with field and composite indexes
---

Indexes speed up filtering, sorting, and lookups on large collections. Zeno creates indexes automatically when you declare them on fields or on the collection.

## Single-field indexes

Add `indexed=True` to any field:

```python
from zork import Collection, TextField, IntField

posts = Collection("posts", fields=[
    TextField("title", required=True),
    TextField("author_id", indexed=True),    # single-field index
    TextField("status", indexed=True),
    IntField("view_count"),
])
```

Zeno generates:

```sql
CREATE INDEX IF NOT EXISTS idx_posts_author_id ON posts (author_id);
CREATE INDEX IF NOT EXISTS idx_posts_status ON posts (status);
```

## Unique indexes

Adding `unique=True` creates a `UNIQUE` constraint, which implies an index:

```python
TextField("slug", unique=True)
TextField("email", unique=True)
```

## Composite indexes

Define multi-column indexes at the collection level for queries that filter on combinations of fields:

```python
posts = Collection(
    "posts",
    fields=[
        TextField("author_id"),
        TextField("status"),
        DateTimeField("published_at"),
    ],
    indexes=[
        ("author_id", "status"),          # queries filtering both author_id AND status
        ("status", "published_at"),       # queries filtering status and sorting by date
    ],
)
```

## When to add indexes

Add an index when you regularly:

- Filter on that field (`?filter[field]=value`)
- Sort on that field (`?sort=field`)
- Use it as a foreign key in a `RelationField`

Indexes improve read performance but have a small cost on write operations. For small collections (under ~10 000 rows), indexes rarely matter.

## Index naming

Zeno names indexes automatically:

- Single field: `idx_{collection}_{field}`
- Composite: `idx_{collection}_{field1}_{field2}`

These names are stable — if an index already exists with the same name, `CREATE INDEX IF NOT EXISTS` is a no-op.

## Indexes and migrations

Indexes are created by auto-sync on startup (same as columns). If you add an `indexed=True` to an existing field, the index will be created the next time the app starts — no migration needed.
