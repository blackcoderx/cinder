---
title: Migrations
description: Manage database schema changes with migration files
---

Migrations let you apply schema changes in a controlled, tracked way — essential for production deployments where you can't afford data loss or downtime from auto-sync.

## How migrations work

Each migration is a Python file in a `migrations/` directory. Cinder tracks which migrations have been applied in a `_schema_migrations` table. Running `cinder migrate` applies any pending migrations in order.

## Commands

### `cinder migrate`

Apply all pending migrations:

```bash
cinder migrate
cinder migrate --app main.py
cinder migrate --dir custom/migrations/path
```

Options:
- `--app` — path to your Cinder app file (used to read the database URL)
- `--dir` — migration directory (default: `migrations`)

### `cinder migrate run`

Same as `cinder migrate` (explicit sub-command form):

```bash
cinder migrate run --app main.py
```

### `cinder migrate status`

Show the status of all migrations:

```bash
cinder migrate status --app main.py
```

Output:

```
ID                                       Status     Applied At
---------------------------------------------------------------------------
20240101_add_slug_to_posts               applied    2024-01-01T10:00:00
20240102_add_author_index                pending    -
```

### `cinder migrate create`

Create a new blank migration file:

```bash
cinder migrate create add_slug_to_posts
# Creates: migrations/20240101_120000_add_slug_to_posts.py
```

### `cinder migrate create --auto`

Auto-generate a migration by diffing your current schema against the database:

```bash
cinder migrate create add_new_fields --auto --app main.py
```

Cinder compares each `Collection` definition to the live database and generates `up()` / `down()` functions for the detected changes.

### `cinder migrate rollback`

Roll back the last applied migration (runs its `down()` function):

```bash
cinder migrate rollback --app main.py
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

`db` is a Cinder `Database` instance with `execute()`, `fetch_one()`, and `fetch_all()` methods.

## Typical workflow

1. Make a schema change in your `Collection` definition
2. Create a migration: `cinder migrate create describe_the_change --auto --app main.py`
3. Review the generated file in `migrations/`
4. Test locally: `cinder migrate --app main.py`
5. Deploy and run `cinder migrate --app main.py` in your CI/CD pipeline before starting the server

## Auto-sync vs migrations

| | Auto-sync | Migrations |
|---|-----------|------------|
| Adds new columns | Yes | Yes |
| Drops columns | No | Yes |
| Renames columns | No | Yes |
| Changes column types | No | Yes |
| Tracked / reversible | No | Yes |
| Recommended for | Dev only | Production |
