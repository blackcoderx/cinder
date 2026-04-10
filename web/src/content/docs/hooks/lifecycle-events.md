---
title: Lifecycle Events
description: Execute custom logic before and after CRUD operations
---

Cinder provides a flexible hook system that lets you run custom logic around every CRUD operation.

## Registering Hooks

Define your handler function, then pass it into `.on()`:

```python
async def add_slug(data, ctx):
    data["slug"] = data["title"].lower().replace(" ", "-")
    return data

posts.on("before_create", add_slug)
```

A decorator form is also available:

```python
@posts.on("before_create")
async def add_slug(data, ctx):
    data["slug"] = data["title"].lower().replace(" ", "-")
    return data
```

## Handler Signature

Every handler receives `(payload, ctx)`:

- `payload` — The data being operated on. Type depends on the event.
- `ctx` — A `CinderContext` with `user`, `request_id`, `collection`, `operation`, `request`, and `extra`.

Handlers may be **sync or async** — Cinder awaits both transparently.

## Mutation Rule

- `before_*` handlers mutate the payload by **returning it**. Returning `None` leaves the payload unchanged.
- `after_*` handlers can return `None` — their return value is ignored.

## Built-in Events

### CRUD Events

| Event | Payload | Mutable? |
|-------|---------|----------|
| `{collection}:before_create` | incoming data dict | yes (return mutated dict) |
| `{collection}:after_create` | saved record dict | no |
| `{collection}:before_read` | record id (string) | yes |
| `{collection}:after_read` | fetched record dict | yes |
| `{collection}:before_list` | `{filters, order_by, limit, offset}` dict | yes |
| `{collection}:after_list` | list of records | yes |
| `{collection}:before_update` | incoming update dict | yes |
| `{collection}:after_update` | `(new_record, previous_record)` tuple | no |
| `{collection}:before_delete` | record about to be deleted | no |
| `{collection}:after_delete` | deleted record | no |

### Auth Events

```
auth:before_register    auth:after_register
auth:before_login       auth:after_login
auth:before_logout      auth:after_logout
auth:before_password_reset    auth:after_password_reset
auth:after_verify_email
```

### App Events

```
app:startup     app:shutdown     app:error
```

## Examples

### Slugify on Create

```python
async def add_slug(data, ctx):
    data["slug"] = data["title"].lower().replace(" ", "-")
    return data

posts.on("before_create", add_slug)
```

### Aborting an Operation

Raise `CinderError` from any hook to stop the chain:

```python
from cinder.errors import CinderError

async def protect_pinned(record, ctx):
    if record.get("pinned"):
        raise CinderError(403, "Pinned posts cannot be deleted")

posts.on("before_delete", protect_pinned)
```

### Soft Delete

Use `CinderError.cancel_delete()` to skip the actual DB delete:

```python
async def soft_delete(record, ctx):
    await db.execute(
        "UPDATE messages SET is_deleted = 1 WHERE id = ?", (record["id"],)
    )
    raise CinderError.cancel_delete()

messages.on("before_delete", soft_delete)
```

`DELETE /api/messages/{id}` still returns `200 OK` and the record stays in the database.

## App Lifecycle

```python
async def seed(_, ctx):
    # Called once when the server starts
    await seed_database()

async def cleanup(_, ctx):
    # Called when the server shuts down
    await flush_queues()

async def log_error(exc, ctx):
    # Fired on any unhandled 500
    await sentry.capture(exc, request_id=ctx.request_id)

app.on("app:startup", seed)
app.on("app:shutdown", cleanup)
app.on("app:error", log_error)
```

## Next Steps

- [Custom Events](/hooks/custom-events/) — Define your own events
- [File Storage](/file-storage/setup/) — Hook into file operations
- [Email](/email/setup/) — Send emails from hooks