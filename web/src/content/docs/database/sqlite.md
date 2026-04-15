---
title: SQLite
description: The default development database
---

SQLite is the default database for Zork. No installation or configuration is required — just pass a filename.

## Configuration

```python
app = Zork(database="app.db")
```

Or use a full SQLite URL:

```python
app = Zork(database="sqlite:///app.db")
app = Zork(database="sqlite:////absolute/path/to/app.db")
```

The file is created automatically if it doesn't exist.

## Using an in-memory database (testing)

```python
app = Zork(database=":memory:")
```

The in-memory database is destroyed when the connection closes. Useful for isolated tests.

## When to use SQLite

SQLite is ideal for:

- Local development
- Prototyping
- Single-user or low-traffic applications
- Edge deployments where a file-based database is preferred

## Limitations

- No concurrent write support — SQLite uses file-level locking. Under high write concurrency, requests will queue.
- Not suitable for horizontal scaling (multiple server processes sharing the same SQLite file have race conditions).

For production with multiple workers, use [PostgreSQL](/database/postgresql/) or [MySQL](/database/mysql/).

## Driver

Zork uses [aiosqlite](https://github.com/omnilib/aiosqlite), which wraps SQLite's standard library driver with an async interface. No extra install is needed — `aiosqlite` is part of Zork's core dependencies.
