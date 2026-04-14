---
title: Lifecycle Hooks
description: Run custom logic before or after any database operation
---

Hooks let you intercept every CRUD operation — validate data, enrich records, send notifications, or modify the payload before it hits the database.

## Hook events

For each collection named `{name}`, Zeno fires these events:

| Event | When | Can modify payload |
|-------|------|--------------------|
| `{name}:before_create` | Before INSERT | Yes |
| `{name}:after_create` | After INSERT | No |
| `{name}:before_update` | Before UPDATE | Yes |
| `{name}:after_update` | After UPDATE (receives tuple of updated, previous) | No |
| `{name}:before_delete` | Before DELETE | No |
| `{name}:after_delete` | After DELETE | No |
| `{name}:before_read` | Before single-record GET | Yes (receives record ID) |
| `{name}:after_read` | After single-record GET | Yes |
| `{name}:before_list` | Before list GET | Yes (receives query descriptor) |
| `{name}:after_list` | After list GET | Yes (receives list of records) |

## Registering a hook

Use the decorator form on the collection:

```python
@posts.on("before_create")
async def add_slug(data, ctx):
    data["slug"] = data["title"].lower().replace(" ", "-")
    return data
```

Or register directly:

```python
async def add_slug(data, ctx):
    data["slug"] = data["title"].lower().replace(" ", "-")
    return data

posts.on("before_create", add_slug)
```

Or register at the app level (useful when observing multiple collections):

```python
@app.on("posts:after_create")
async def notify_subscribers(post, ctx):
    await send_notification(post["id"])
```

## The `ZenoContext` object

Every hook receives a `ZenoContext` as its second argument:

```python
from zeno.hooks.context import ZenoContext

async def my_hook(data, ctx: ZenoContext):
    print(ctx.user)        # dict of the current user, or None if unauthenticated
    print(ctx.collection)  # "posts"
    print(ctx.operation)   # "create", "update", "delete"
    print(ctx.request_id)  # correlation ID for logging
    print(ctx.extra)       # arbitrary dict for passing data between hooks
```

## Modifying data in `before_` hooks

Return the modified `data` dict from a `before_create` or `before_update` hook to persist your changes:

```python
@posts.on("before_create")
async def set_author(data, ctx):
    if ctx.user:
        data["author_id"] = ctx.user["id"]
    return data
```

If you don't return anything (or return `None`), the original `data` is used unchanged.

## Raising errors from hooks

Raise a `ZenoError` to abort the operation and return an HTTP error response:

```python
from zeno.errors import ZenoError

@posts.on("before_create")
async def check_quota(data, ctx):
    count = await get_post_count(ctx.user["id"])
    if count >= 10:
        raise ZenoError(403, "Post limit reached")
    return data
```

## Multiple hooks on the same event

Multiple handlers on the same event run in registration order. Each handler receives the data returned by the previous one:

```python
@posts.on("before_create")
async def add_slug(data, ctx):
    data["slug"] = slugify(data["title"])
    return data

@posts.on("before_create")
async def add_author(data, ctx):
    data["author_id"] = ctx.user["id"]
    return data
```

## Async handlers

All hook handlers must be `async def`. Synchronous functions are not supported.

## Firing custom events

You can fire your own events anywhere in your hooks:

```python
@orders.on("after_create")
async def process_order(order, ctx):
    # do work ...
    await app.hooks.fire("order:processed", order, ctx)
```

See [Custom Events](/hooks/custom-events/) for more.
