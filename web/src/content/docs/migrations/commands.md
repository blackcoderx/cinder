---
title: Migrations
description: Manage database schema changes with migration files
---

Migrations let you apply schema changes in a controlled, tracked way — essential for production deployments where you can't afford data loss or downtime from auto-sync.

## How migrations work

Each migration is a Python file in a `migrations/` directory. Zeno tracks which migrations have been applied in a `_schema_migrations` table. Running `zeno migrate` applies any pending migrations in order.

## Commands

### `zeno migrate`

Apply all pending migrations:

```bash
zeno migrate
zeno migrate --app main.py
zeno migrate --dir custom/migrations/path
```

Options:
- `--app` — path to your Zeno app file (used to read the database URL)
- `--dir` — migration directory (default: `migrations`)

### `zeno migrate run`

Same as `zeno migrate` (explicit sub-command form):

```bash
zeno migrate run --app main.py
```

### `zeno migrate status`

Show the status of all migrations:

```bash
zeno migrate status --app main.py
```

Output:

```
ID                                       Status     Applied At
---------------------------------------------------------------------------
20240101_add_slug_to_posts               applied    2024-01-01T10:00:00
20240102_add_author_index                pending    -
```

### `zeno migrate create`

Create a new blank migration file:

```bash
zeno migrate create add_slug_to_posts
# Creates: migrations/20240101_120000_add_slug_to_posts.py
```

### `zeno migrate create --auto`

Auto-generate a migration by diffing your current schema against the database:

```bash
zeno migrate create add_new_fields --auto --app main.py
```

Zeno compares each `Collection` definition to the live database and generates `up()` / `down()` functions for the detected changes.

### `zeno migrate rollback`

Roll back the last applied migration (runs its `down()` function):

```bash
zeno migrate rollback --app main.py
```

## Migration file format

```python
# migrations/20240101_120000_add_slug_to_posts.py

async def up(db):
    await db.execute("ALTER TABLE posts ADD COLUMN slug TEXT")
    await db.execute("CREATE INDEX IF NOT EXISTS idx_posts_slug ON posts (slug)")

async def down(db):
    await db.execute("DROP INDEX IF EXISTS idx_posts_slug")
    # SQLite doesn't support DROP COLUMN directly; use table rebuild if needed
```

`db` is a Zeno `Database` instance with `execute()`, `fetch_one()`, and `fetch_all()` methods.

## Typical workflow

1. Make a schema change in your `Collection` definition
2. Create a migration: `zeno migrate create describe_the_change --auto --app main.py`
3. Review the generated file in `migrations/`
4. Test locally: `zeno migrate --app main.py`
5. Deploy and run `zeno migrate --app main.py` in your CI/CD pipeline before starting the server

## Auto-sync vs migrations

| | Auto-sync | Migrations |
|---|-----------|------------|
| Adds new columns | Yes | Yes |
| Drops columns | No | Yes |
| Renames columns | No | Yes |
| Changes column types | No | Yes |
| Tracked / reversible | No | Yes |
| Recommended for | Dev only | Production |
