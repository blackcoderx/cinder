---
title: Overview
description: Schema migrations for version-controlled database changes
---

Cinder's migration system provides explicit, version-tracked control over schema changes.

## When to Use Migrations vs Auto-Sync

| Change | Auto-Sync | Migration |
|--------|-----------|-----------|
| Add a new column | ✅ Handled on startup | Optional |
| Create a new collection | ✅ Handled on startup | Optional |
| Add a database index | ❌ | ✅ Write a migration |
| Rename a column | ❌ | ✅ Write a migration |
| Transform existing data | ❌ | ✅ Write a migration |
| Drop a column | ❌ | ✅ Uncomment generated SQL |

Both run together — auto-sync handles additive changes, migrations handle the rest.

## Migration Files

Migration files live in a `migrations/` directory:

```python
# migrations/20260409_143022_add_index_posts_category.py
"""Add index on posts.category for faster category filtering."""

async def up(db):
    await db.execute("CREATE INDEX idx_posts_category ON posts (category)")

async def down(db):
    await db.execute("DROP INDEX IF EXISTS idx_posts_category")
```

The `db` argument is Cinder's `Database` object.

## How It Works

1. **Apply** — Run `cinder migrate` to apply pending migrations
2. **Track** — Applied migrations are recorded in `_schema_migrations`
3. **Rollback** — Use `cinder migrate rollback` to undo

## Migration Tracking

Applied migrations are recorded in `_schema_migrations`:

```sql
CREATE TABLE _schema_migrations (
    id         TEXT PRIMARY KEY,   -- migration filename without .py
    applied_at TEXT NOT NULL       -- UTC ISO 8601 timestamp
)
```

## Example Workflow

1. Add `indexed=True` to a field
2. Generate migration: `cinder migrate create add_index --auto`
3. Apply: `cinder migrate`
4. Check status: `cinder migrate status`

## Next Steps

- [Commands](/migrations/commands/) — CLI reference
- [Database Indexes](/database/indexes/) — Query optimization