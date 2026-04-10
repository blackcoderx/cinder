---
title: Indexes
description: Optimize database queries with indexes
---

Cinder supports database indexes for query optimization.

## Field-Level Indexing

Add `indexed=True` to any field to create an index automatically:

```python
from cinder import Collection, TextField, IntField

class Posts(Collection):
    name = TextField(required=True)
    category = TextField(indexed=True)  # Creates index on category
    views = IntField(indexed=True)      # Creates index on views
```

The index is created automatically when you call `store.sync_schema()` or run migrations with `--auto`.

## Composite Indexes

Define composite indexes for multi-column queries:

```python
class Posts(Collection):
    name = TextField(required=True)
    category = TextField()
    created_at = TextField()

    indexes = [
        ("category", "created_at"),  # Composite index on (category, created_at)
    ]
```

Index naming follows the pattern `idx_{table}_{column1}_{column2}`.

## Unique Fields

Fields with `unique=True` already have a database-enforced unique constraint, which implicitly creates an index. You don't need to add `indexed=True` for unique fields.

## Index Behavior

- **Auto-sync** — Indexes are created automatically when running `sync_schema()`
- **Migrations** — Use `cinder migrate --auto` to generate migration files
- **Non-destructive** — Cinder never drops indexes that exist in the database but are not in your schema

## When to Use Indexes

### Good Candidates for Indexing

- Columns used in `WHERE` clauses frequently
- Columns used for sorting (`ORDER BY`)
- Columns used in joins (`RelationField`)

### Avoid Indexing

- Columns with low cardinality (few unique values)
- Columns rarely queried
- Large text fields (consider full-text search instead)

## Example: Blog Posts

```python
class Post(Collection):
    title = TextField(required=True)
    slug = TextField(unique=True)  # Unique constraint = index
    category = TextField(indexed=True)  # Filter by category
    author = TextField(indexed=True)  # Filter by author
    created_at = TextField(indexed=True)  # Sort by date
    status = TextField()  # No index needed

    indexes = [
        ("category", "created_at"),  # Common query pattern
    ]
```

## Next Steps

- [SQLite](/database/sqlite/) — Default database
- [PostgreSQL](/database/postgresql/) — Production database
- [Migrations](/migrations/overview/) — Version-controlled schema changes