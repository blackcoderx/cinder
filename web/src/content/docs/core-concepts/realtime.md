---
title: Realtime
description: Push updates to connected clients in real-time
---

Realtime in Cinder enables you to push updates to connected clients whenever data changes. Instead of clients polling for updates, the server notifies them instantly.

## How It Works

Cinder uses a **channel-based pub/sub system**:

```
┌─────────────────┐                      ┌─────────────────┐
│   Your App      │                      │   Client         │
│                 │  ┌────────────────┐  │                 │
│  Record created │→ │   Broker       │→ │  Receives       │
│  Record updated │  │  (in-memory or │  │  notification   │
│  Record deleted │  │   Redis)       │  │                 │
└─────────────────┘  └────────────────┘  └─────────────────┘
                              ↑
                    ┌─────────────────┐
                    │  Other clients  │
                    │  (also subs.)   │
                    └─────────────────┘
```

## Channels

Everything in Cinder's realtime system revolves around **channels** — named event streams.

| Channel | Description | Auto-Emitted? |
|---------|-------------|---------------|
| `collection:{name}` | CRUD events for a collection | Yes — on every create/update/delete |
| Any custom string | Your own events | No — you fire them manually |

### Collection Channels

When you register a collection, Cinder automatically emits events to a channel named `collection:{name}`:

```python
app.register(posts)
```

This enables automatic events on `collection:posts`:

| Event | Trigger |
|-------|---------|
| `create` | A new record is created |
| `update` | A record is modified |
| `delete` | A record is deleted |

### Custom Channels

You can also publish to any channel name:

```python
await app.realtime.publish("notifications:user-123", {"message": "Hello!"})
await app.realtime.publish("system:alerts", {"level": "warning", "msg": "..."})
```

## Event Envelope

Every message follows this structure:

```json
{
  "channel": "collection:posts",
  "event": "create",
  "record": {
    "id": "abc123",
    "title": "New Post",
    "created_at": "2026-04-10T12:00:00Z"
  },
  "previous": null
}
```

| Field | Description |
|-------|-------------|
| `channel` | The channel this event was published to |
| `event` | `create`, `update`, or `delete` |
| `record` | The current state of the record |
| `previous` | Previous state (only on `update`) |

## Transport Options

Cinder supports two transport protocols:

| Transport | Best For | Browser Support |
|----------|----------|---------------|
| **WebSocket** | Bidirectional communication, low latency | All modern browsers |
| **Server-Sent Events (SSE)** | One-way streaming, simplicity | All modern browsers |

### Choosing a Transport

**Use WebSocket when you need:**
- Bidirectional communication (client can also send messages)
- The lowest possible latency
- Complex messaging patterns

**Use SSE when you need:**
- Simple one-way streaming
- Automatic reconnection (built into EventSource)
- Works through proxies that block WebSocket

## Connecting with WebSocket

```javascript
const ws = new WebSocket("ws://localhost:8000/api/realtime/ws");

ws.onopen = () => {
  // Authenticate (optional)
  ws.send(JSON.stringify({ 
    action: "auth", 
    token: localStorage.getItem("token") 
  }));
  
  // Subscribe to a channel
  ws.send(JSON.stringify({ 
    action: "subscribe", 
    channel: "collection:posts" 
  }));
};

ws.onmessage = ({ data }) => {
  const msg = JSON.parse(data);
  
  if (msg.channel === "collection:posts") {
    console.log(`Post ${msg.event}d:`, msg.record);
  }
};
```

### WebSocket Messages

**Subscribe:**
```json
{ "action": "subscribe", "channel": "collection:posts" }
```

**Unsubscribe:**
```json
{ "action": "unsubscribe", "channel": "collection:posts" }
```

**Authenticate:**
```json
{ "action": "auth", "token": "eyJhbGci..." }
```

## Connecting with SSE

```javascript
const token = localStorage.getItem("token");
const url = `/api/realtime/sse?channel=collection:posts&token=${token}`;
const source = new EventSource(url);

source.addEventListener("create", (e) => {
  const data = JSON.parse(e.data);
  console.log("New post:", data.record);
});

source.addEventListener("update", (e) => {
  const data = JSON.parse(e.data);
  console.log("Post updated:", data.record);
});
```

Subscribe to multiple channels:

```
/api/realtime/sse?channel=collection:posts&channel=collection:comments
```

## Auth Filtering

Realtime respects access control rules:

- **Public collections**: No auth required to subscribe
- **Protected collections**: Authenticate with a token to receive events
- **Owner rules**: Users only receive events for records they own

```javascript
// Authenticate mid-session
ws.send(JSON.stringify({ action: "auth", token: "..." }));
```

## Pubishing Custom Events

Emit events from your application code:

```python
# Publish to a custom channel
await app.realtime.publish("notifications:user-123", {"message": "Hello!"})

# Fire from a hook
@orders.on("after_update")
async def notify_status_change(payload, ctx):
    new_record, old_record = payload
    await app.realtime.publish(
        f"orders:{new_record['customer_id']}",
        {
            "event": "status_update",
            "record": new_record
        }
    )
```

## Next Steps

- [Realtime Reference](/realtime/overview/) — Detailed API documentation
- [Hooks](/core-concepts/lifecycle-hooks/) — Trigger realtime events from hooks
- [Authentication](/authentication/setup/) — Secure your realtime connections
