---
title: Custom Events
description: Define and fire your own custom events
---

Any string is a valid event name. You don't register event names upfront — just fire them.

## Defining Custom Events

```python
async def trigger_shipping(record, ctx):
    await create_shipment(record)

async def send_receipt(record, ctx):
    await email_receipt(record)

orders.on("payment_confirmed", trigger_shipping)
orders.on("payment_confirmed", send_receipt)
```

## Firing Custom Events

Fire custom events from within built-in hooks:

```python
async def on_payment_updated(payload, ctx):
    record, prev = payload
    if record["status"] == "paid" and prev["status"] == "pending":
        await orders.fire("payment_confirmed", record, ctx)

orders.on("after_update", on_payment_updated)
```

## Cross-Collection Events

Publish events across collections using the app-level bus:

```python
async def suspend_account(data, ctx): ...
async def notify_security(data, ctx): ...

app.on("fraud:detected", suspend_account)
app.on("fraud:detected", notify_security)

# Fire from anywhere
await app.hooks.fire("fraud:detected", {"user_id": "..."}, ctx)
```

## Firing from Hooks

The `fire()` method is available on collections:

```python
posts.on("after_create", async def notify_followers(post, ctx):
    await posts.fire("new_post", post, ctx)
)
```

## Firing from App

Fire events at the app level:

```python
await app.hooks.fire("custom_event", payload, ctx)
```

## No-Op Behavior

Firing an event with zero registered handlers is a no-op — no error raised:

```python
# No handlers registered for "my_event" - this does nothing
await app.hooks.fire("my_event", {"data": "test"}, ctx)
```

## Event Naming Convention

Use namespaced events for organization:

```python
# Payment events
payments.on("payment:pending", handler)
payments.on("payment:completed", handler)
payments.on("payment:failed", handler)

# Webhook events
webhooks.on("webhook:triggered", handler)
```

## Example: Order Processing Pipeline

```python
# Define handlers for order lifecycle
@orders.on("order:created")
async def on_order_created(order, ctx):
    await send_order_confirmation(order)

@orders.on("order:paid")
async def on_order_paid(order, ctx):
    await initiate_shipping(order)
    await orders.fire("order:fulfilling", order, ctx)

@orders.on("order:shipped")
async def on_order_shipped(order, ctx):
    await notify_customer(order, "Your order has shipped!")

# Fire events at appropriate moments
@orders.on("after_create")
async def trigger_order_created(order, ctx):
    await orders.fire("order:created", order, ctx)

@orders.on("after_update")
async def check_payment_status(payload, ctx):
    order, prev = payload
    if order["status"] == "paid" and prev["status"] != "paid":
        await orders.fire("order:paid", order, ctx)
```

## Next Steps

- [Lifecycle Events](/hooks/lifecycle-events/) — Built-in events
- [Realtime](/realtime/overview/) — Emit events to connected clients
- [Email](/email/setup/) — Send notifications via email