---
title: Commands
description: Migration CLI commands reference
---

## create

Create a new migration file:

### Blank Template

```bash
cinder migrate create add_index_posts --app main.py
# Created migration: migrations/20260409_143022_add_index_posts.py
```

### Auto-Generate from Schema

```bash
cinder migrate create sync_schema --app main.py --auto
```

The `--auto` flag generates SQL for:
- New collections not yet in the database → `CREATE TABLE`
- New fields not yet in existing tables → `ALTER TABLE ADD COLUMN`
- Columns in DB not in any collection → commented-out `DROP COLUMN`

## run / apply

Apply all pending migrations:

```bash
cinder migrate --app main.py
# Or explicitly
cinder migrate run --app main.py
```

Cinder applies each pending file in filename order.

## status

Show migration history:

```bash
cinder migrate status --app main.py
```

Output:
```
ID                                           STATUS    APPLIED AT
20260409_143022_add_index_posts_category     applied   2026-04-09T14:30:22+00:00
20260410_090000_add_audit_table              pending   -
```

Orphaned entries (applied but file deleted) appear with status `orphaned`.

## rollback

Undo the most recently applied migration:

```bash
cinder migrate rollback --app main.py
```

Rolls back by calling the migration's `down()` function and removing the tracking record.

## Custom Directory

All migrate commands accept `--dir` to override the default `migrations/` path:

```bash
cinder migrate --app main.py --dir db/migrations
cinder migrate create add_index --app main.py --dir db/migrations
```

## Full Example

```bash
# Create a new migration
cinder migrate create add_index_posts --app main.py --auto

# Apply pending migrations
cinder migrate --app main.py

# Check status
cinder migrate status --app main.py

# If something goes wrong, rollback
cinder migrate rollback --app main.py

# Apply again after fixing
cinder migrate --app main.py
```

## Next Steps

- [Overview](/migrations/overview/) — Migration system
- [Configuration](/configuration/env-variables/) — Environment variables