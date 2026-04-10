---
title: The Cinder App
description: The central registry that wires everything together
---

The `Cinder` class is the entry point for every Cinder application. It acts as a **central registry** that connects your data schemas, authentication, and other subsystems into a unified REST API.

## Creating an App

```python
from cinder import Cinder

app = Cinder(database="app.db")
```

### Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| `database` | `"app.db"` | Database connection. Accepts SQLite path, `postgresql://...`, or `mysql://...` |
| `title` | `"Cinder API"` | Title shown in OpenAPI docs and Swagger UI |
| `version` | `"1.0.0"` | API version shown in OpenAPI docs |

## The Build Pattern

Cinder uses a two-phase initialization pattern:

```python
app = Cinder(database="app.db")

# Phase 1: Configure your app
# - Register collections
# - Set up auth
# - Configure subsystems (optional)

app.register(my_collection, auth=["read:public"])
app.use_auth(Auth())

# Phase 2: Build and serve
app.serve()  # Development: starts uvicorn
```

### build() vs serve()

| Method | Use Case | Under the Hood |
|--------|----------|---------------|
| `app.serve(host, port, reload)` | Development | Calls `build()`, then runs with Uvicorn |
| `app.build()` | Production | Returns a Starlette ASGI app for gunicorn/hypercorn |

For production deployment:

```python
# main.py
app = Cinder(database="app.db")
app.register(posts)
app.use_auth(Auth())

# gunicorn main:app.build() --factory -w 4 -k uvicorn.workers.UvicornWorker
```

## Registering Collections

Collections connect your data schemas to the API:

```python
from cinder import Cinder, Collection, TextField

app = Cinder(database="app.db")

# Define a collection
posts = Collection("posts", fields=[
    TextField("title", required=True),
    TextField("content"),
])

# Register it - this creates the table and API endpoints
app.register(posts)
```

After `register()`, Cinder automatically:
1. Creates the database table if it doesn't exist
2. Generates CRUD endpoints at `/api/posts`

## Subsystem Configuration

Cinder exposes several subsystems through a fluent configuration API:

```python
# Database
app.configure_database(PostgreSQLBackend(url="postgresql://..."))
app.configure_redis(url="redis://localhost:6379")  # Configures all Redis subsystems at once

# Cache
app.cache.configure(default_ttl=300, per_user=True)

# Rate Limiting
app.rate_limit.rule("/api/write", limit=10, window=60)

# Email
app.email.use(SMTPBackend.sendgrid(api_key="..."))
app.email.configure(from_address="noreply@example.com", app_name="MyApp")
```

Each subsystem attribute returns a configuration object that you chain methods on.

## Authentication Setup

Authentication is configured separately from collections:

```python
from cinder import Cinder, Auth

app = Cinder(database="app.db")
auth = Auth(allow_registration=True, token_expiry=86400)

app.use_auth(auth)
```

This enables auth endpoints: `/api/auth/register`, `/api/auth/login`, `/api/auth/me`, etc.

## Typical Application Flow

```python
from cinder import Cinder, Collection, TextField, Auth

# 1. Create the app
app = Cinder(database="app.db", title="My Blog API")

# 2. Define and register collections
posts = Collection("posts", fields=[
    TextField("title", required=True),
    TextField("content"),
])

app.register(posts, auth=["read:public", "write:authenticated"])

# 3. Configure auth
app.use_auth(Auth(allow_registration=True))

# 4. Add hooks (optional)
@app.on("posts:before_create")
async def validate(data, ctx):
    if len(data.get("title", "")) < 3:
        raise CinderError(400, "Title too short")
    return data

# 5. Serve
app.serve()
```

## App Lifecycle

When you call `app.build()`, Cinder:

1. **Resolves backends** — Connects to database, Redis (if configured), etc.
2. **Syncs schemas** — Creates/updates database tables for all collections
3. **Creates auth tables** — Sets up user storage if auth is enabled
4. **Builds routes** — Generates all HTTP endpoints
5. **Wires middleware** — Attaches auth, cache, rate-limiting middleware
6. **Returns ASGI app** — Ready to serve requests

## Next Steps

- [Collections](/core-concepts/collections/) — Define your data schemas
- [Access Control](/core-concepts/access-control/) — Control who can do what
- [Authentication](/authentication/setup/) — User registration and login
