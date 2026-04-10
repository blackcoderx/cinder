---
title: Custom Channels
description: Publish and subscribe to custom event channels
---

You are not limited to collection channels. Publish to any string channel and subscribe to it.

## Server-Side: Publish from Hooks

```python
async def on_payment_updated(payload, ctx):
    record, prev = payload
    if record["status"] == "paid":
        await app.realtime.publish(
            "payments:completed",
            {"order_id": record["id"], "amount": record["total"]},
            event="payment_completed",
        )

orders.on("after_update", on_payment_updated)
```

## Client-Side: WebSocket

```javascript
ws.send(JSON.stringify({ action: "subscribe", channel: "payments:completed" }));
```

## Client-Side: SSE

```
GET /api/realtime/sse?channel=payments:completed
```

## Custom Envelope Builder

Override the default envelope format:

```python
import time

def my_envelope(collection_name, event, record, previous):
    return {
        "type": "data",
        "collection": collection_name,
        "action": event,
        "payload": record,
        "diff": previous,
        "ts": time.time(),
    }

app.realtime.envelope_builder = my_envelope
```

The builder is called every time the bridge emits to the broker.

## Controlling Auto-Emit

By default, every CRUD operation publishes to `collection:{name}`. Disable globally:

```python
app.realtime.disable_auto_emit()

# Later, re-enable
app.realtime.enable_auto_emit()
```

When auto-emit is disabled, you can still publish manually:

```python
async def manual_emit(record, ctx):
    await app.realtime.publish("collection:posts", record, event="create")

posts.on("after_create", manual_emit)
```

## Example: Chat Application

**Server:**

```python
# When a message is created, publish to room channel
messages.on("after_create", async def on_message(msg, ctx):
    room_id = msg["room_id"]
    await app.realtime.publish(
        f"chat:{room_id}",
        msg,
        event="message",
    )
)
```

**Client:**

```javascript
const ws = new WebSocket("ws://localhost:8000/api/realtime/ws");

ws.onopen = () => {
  ws.send(JSON.stringify({ action: "subscribe", channel: "chat:room-42" }));
};

ws.onmessage = (e) => {
  const msg = JSON.parse(e.data);
  if (msg.channel === "chat:room-42") {
    appendMessage(msg.record);
  }
};
```

Custom channels carry no default auth filter — events are delivered to all subscribers.

## Next Steps

- [WebSocket](/realtime/websocket/) — Full WebSocket guide
- [SSE](/realtime/sse/) — Full SSE guide
- [Overview](/realtime/overview/) — Realtime system overview