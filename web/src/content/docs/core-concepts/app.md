---
title: The Zeno App
description: The central application object that wires everything together
---

The `Zeno` class is the entry point for every application. It owns the database connection, registered collections, authentication config, and all optional subsystems.

## Creating an app

```python
from zork import Zeno

app = Zeno(database="app.db")
```

### Constructor options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `database` | `str` | `"app.db"` | Database URL or SQLite filename |
| `title` | `str` | `"Zeno API"` | API title shown in OpenAPI docs |
| `version` | `str` | `"1.0.0"` | API version shown in OpenAPI docs |

For PostgreSQL or MySQL, pass a full connection URL:

```python
app = Zeno(database="postgresql://user:pass@localhost/mydb")
```

Or use an environment variable — Zeno reads `ZENO_DATABASE_URL` then `DATABASE_URL` automatically.

## Registering collections

```python
app.register(posts, auth=["read:public", "write:authenticated"])
```

`register()` takes a `Collection` and an optional list of [access control rules](/core-concepts/access-control/). Each call creates the database table (if it doesn't exist) and wires up CRUD routes.

## Enabling authentication

```python
from zork import Auth

auth = Auth(token_expiry=86400, allow_registration=True)
app.use_auth(auth)
```

`use_auth()` mounts all `/api/auth/*` endpoints and enables JWT middleware. See [Authentication](/authentication/) for full details.

## Configuring optional subsystems

Each subsystem has a fluent configuration facade on the `app` object:

```python
# File storage
from zork.storage import LocalFileBackend
app.configure_storage(LocalFileBackend("./uploads"))

# Email
from zork.email import SMTPBackend
app.email.use(SMTPBackend.sendgrid(api_key="..."))
app.email.configure(from_address="no-reply@myapp.com", app_name="MyApp")

# Caching
app.cache.use(RedisCacheBackend())
app.cache.configure(default_ttl=300)

# Rate limiting
app.rate_limit.rule("/api/posts", limit=50, window=60)

# Redis (all subsystems at once)
app.configure_redis(url="redis://localhost:6379")

# Custom database backend
from zork.db.backends.postgresql import PostgreSQLBackend
app.configure_database(PostgreSQLBackend(url="...", min_size=2, max_size=20, ssl="require"))
```

## Registering hooks

Use `app.on()` to respond to any lifecycle event across all collections:

```python
@app.on("posts:after_create")
async def notify(post, ctx):
    print(f"New post: {post['title']}")

# Or pass the handler directly
app.on("orders:after_create", send_confirmation_email)
```

## Starting the server

### Via the CLI (recommended)

```bash
zork serve main.py
zork serve main.py --reload  # development auto-reload
zork serve main.py --host 0.0.0.0 --port 8080
```

### Programmatically

```python
app.serve()                          # default host/port
app.serve(host="0.0.0.0", port=8080)
```

### As an ASGI app

`app.build()` returns a plain ASGI app you can deploy with any ASGI server:

```python
# main.py
from zork import Zeno, ...
app = Zeno(...)
# ... configure ...
asgi_app = app.build()
```

```bash
uvicorn main:asgi_app
gunicorn main:asgi_app -k uvicorn.workers.UvicornWorker
```

## Lifecycle events

Zeno fires `app:startup` and `app:shutdown` during the ASGI lifespan:

```python
@app.on("app:startup")
async def on_start(_, ctx):
    print("Server started")

@app.on("app:shutdown")
async def on_stop(_, ctx):
    print("Server stopping")
```
