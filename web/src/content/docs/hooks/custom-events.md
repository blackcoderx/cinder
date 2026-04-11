---
title: Custom Events
description: Fire and listen to your own events
---

The hook system is not limited to built-in lifecycle events. You can fire any event string and register handlers for it — useful for cross-collection observers, background workflows, and custom event buses.

## Firing a custom event

```python
await app.hooks.fire("order:shipped", order_data, ctx)
```

Or from within a hook:

```python
@orders.on("after_update")
async def check_shipped(order, ctx):
    if order["status"] == "shipped":
        await app.hooks.fire("order:shipped", order, ctx)
```

## Listening to a custom event

```python
@app.on("order:shipped")
async def send_tracking_email(order, ctx):
    await app.email.send(EmailMessage(
        to=order["customer_email"],
        subject="Your order has shipped!",
        html_body=f"<p>Track your order: {order['tracking_number']}</p>",
        text_body=f"Track your order: {order['tracking_number']}",
    ))
```

## Event naming

Any string is a valid event name. By convention:

- Built-in events use `{collection}:{verb}` — e.g. `"posts:before_create"`
- Custom events should follow the same pattern for clarity — e.g. `"order:shipped"`, `"payment:failed"`, `"fraud:detected"`

## Passing data between hooks

The `ctx.extra` dict is a free-form scratchpad you can use to pass data between handlers in the same request:

```python
@posts.on("before_create")
async def compute_score(data, ctx):
    ctx.extra["quality_score"] = expensive_computation(data)
    return data

@posts.on("after_create")
async def log_score(record, ctx):
    score = ctx.extra.get("quality_score")
    print(f"Post created with score: {score}")
```

## App-level vs collection-level

`app.on(event)` and `collection.on(event)` share the same underlying registry after `app.register(collection)` is called. The only difference is namespacing:

```python
# These are equivalent:
posts.on("before_create", handler)
app.on("posts:before_create", handler)
```

## Firing events from outside hooks

You can fire events from anywhere — not just inside hooks:

```python
# In a scheduled job, a background task, etc.
ctx = CinderContext.system(extra={"source": "scheduler"})
await app.hooks.fire("daily:digest", None, ctx)
```

`CinderContext.system()` creates a context with no user or request — suitable for system-initiated events.
