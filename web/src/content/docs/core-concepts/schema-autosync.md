---
title: Schema Auto-Sync
description: Cinder automatically syncs your schema changes to the database
---

On every startup, Cinder compares your collection definitions to the database and automatically applies safe schema changes.

## How Auto-Sync Works

When your app starts, Cinder:

1. Reads the existing database schema
2. Compares it against your Collection definitions
3. Applies only **additive changes** (never destructive)

```
┌─────────────────────────────────────────────────────────────────┐
│                     App Startup                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Your Code                    Database                            │
│  ┌──────────────┐           ┌──────────────┐                    │
│  │ Collection:  │           │ Table exists │ No ─────────┐      │
│  │ products    │───────────→│ with 5 cols  │────────────→│ CREATE│
│  └──────────────┘           └──────────────┘              │ TABLE│
│        │                         │                        │      │
│        │                     Yes │                        │      │
│        │                         ↓                        │      │
│        │                   Check cols ◄─────────────────┘      │
│        │                         │                              │
│        │          ┌──────────────┼──────────────┐              │
│        │          ↓              ↓              ↓              │
│        │      Missing       All match      Extra cols          │
│        │      cols?           ?              in DB?           │
│        │          ↓              ↓              ↓              │
│        └──────────┴──────────────┴──────────────┴──────────────┘
│              │                                                   │
│              ↓                                                   │
│     ALTER TABLE ──── ADD COLUMN                                  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## What Auto-Sync Handles

| Change | Auto-Sync Action |
|--------|-----------------|
| New collection | Creates the table |
| New field added | Adds the column via `ALTER TABLE` |
| Field removed from code | Logs a warning, **does not drop** the column |

## What Auto-Sync Does NOT Handle

| Change | Action Required |
|--------|-----------------|
| Removing columns | Use [Migrations](/migrations/overview/) |
| Renaming columns | Use Migrations (rename + data transform) |
| Adding indexes | Use Migrations or `indexed=True` on field |
| Dropping indexes | Use Migrations |
| Changing field constraints | Use Migrations |

## Examples

### Adding a New Field

```python
# Before restart - no tags field
posts = Collection("posts", fields=[
    TextField("title", required=True),
])

# After restart - tags field is added automatically
posts = Collection("posts", fields=[
    TextField("title", required=True),
    JSONField("tags", default=[]),  # New field!
])
```

On startup, Cinder detects the new `tags` field and runs:

```sql
ALTER TABLE posts ADD COLUMN tags TEXT
```

### Removing a Field

```python
# Remove deprecated field from code
posts = Collection("posts", fields=[
    TextField("title", required=True),
    # old_field removed
])
```

Cinder logs a warning:

```
WARNING: Column 'old_field' exists in database but not in Collection schema
```

The column and its data remain in the database. This prevents accidental data loss during development.

## Indexes

Indexes are **not** auto-synced. Use the `indexed=True` parameter on fields:

```python
products = Collection("products", fields=[
    TextField("name", required=True),
    TextField("category", indexed=True),  # Creates index
    IntField("views", indexed=True),     # Creates index
])
```

This generates on startup:

```sql
CREATE INDEX IF NOT EXISTS idx_products_category ON products (category);
CREATE INDEX IF NOT EXISTS idx_products_views ON products (views);
```

## Decision Matrix: Auto-Sync vs Migrations

| Task | Auto-Sync | Migrations |
|------|-----------|------------|
| Add new table | ✅ Yes | ✅ Yes |
| Add new column | ✅ Yes | ✅ Yes |
| Remove column | ❌ No (logs warning) | ✅ Yes |
| Rename column | ❌ No | ✅ Yes |
| Add index | ✅ Yes (`indexed=True`) | ✅ Yes |
| Remove index | ❌ No | ✅ Yes |
| Transform existing data | ❌ No | ✅ Yes |
| Change column type | ❌ No | ✅ Yes |

Both systems work together:
- **Auto-sync** handles additive changes automatically on every startup
- **Migrations** handle complex changes that need version control

## Safe Development Workflow

```python
# Step 1: Add field to code
posts = Collection("posts", fields=[
    TextField("title", required=True),
    TextField("summary"),  # Just added
])

# Step 2: Restart server
# Cinder auto-adds the column

# Step 3: Verify in database
# SELECT * FROM posts; -- now includes summary column

# Step 4: (Later) Remove field from code
# Data is preserved in DB, just not accessible via API
```

## Migrations for Complex Changes

When auto-sync isn't enough:

```bash
# Generate a migration for a complex change
cinder migrate create rename_author_to_writer
```

See [Migrations](/migrations/overview/) for detailed documentation.

## Next Steps

- [Migrations](/migrations/overview/) — Version-controlled schema changes
- [Database Indexes](/database/indexes/) — Optimize query performance
