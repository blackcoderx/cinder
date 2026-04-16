# Realtime Overview

Zork includes realtime capabilities through WebSocket and Server-Sent Events (SSE). This lets clients receive instant updates when data changes.

## Overview

Realtime in Zork works through a publish-subscribe system:

1. When data changes (create, update, delete), Zork publishes an event
2. Connected clients receive the event in real-time
3. Clients can subscribe to specific collections or channels

## Enabling Realtime

Realtime is enabled by default. It becomes active once you register at least one collection:

```python
from zork import Zork, Collection, TextField

app = Zork()

posts = Collection("posts", fields=[
    TextField("title"),
])

app.register(posts)

# Realtime is now available at /api/realtime
```

## Connection Endpoints

| Protocol | Endpoint | Description |
|----------|----------|-------------|
| WebSocket | `ws://localhost:8000/api/realtime` | Bidirectional communication |
| SSE | `http://localhost:8000/api/realtime/sse` | Server-to-client only |

## WebSocket Connection

Connect using a WebSocket client:

```javascript
const ws = new WebSocket("ws://localhost:8000/api/realtime");

ws.onopen = () => {
  console.log("Connected to realtime");
  
  // Subscribe to collection events
  ws.send(JSON.stringify({
    action: "subscribe",
    channels: ["posts"]
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log("Event:", data);
  
  // data.event = "create" | "update" | "delete"
  // data.collection = "posts"
  // data.record = { ... }
};

ws.onerror = (error) => {
  console.error("WebSocket error:", error);
};

ws.onclose = () => {
  console.log("Disconnected");
};
```

## SSE Connection

For simpler use cases, use Server-Sent Events:

```javascript
const eventSource = new EventSource("http://localhost:8000/api/realtime/sse");

eventSource.addEventListener("posts:create", (event) => {
  const data = JSON.parse(event.data);
  console.log("New post:", data);
});

eventSource.addEventListener("posts:update", (event) => {
  const data = JSON.parse(event.data);
  console.log("Updated post:", data);
});

eventSource.addEventListener("posts:delete", (event) => {
  const data = JSON.parse(event.data);
  console.log("Deleted post:", data);
});
```

## Subscribing to Channels

Clients subscribe to specific channels to receive updates:

```javascript
// Subscribe to specific collections
ws.send(JSON.stringify({
  action: "subscribe",
  channels: ["posts", "comments"]
}));

// Subscribe to specific records
ws.send(JSON.stringify({
  action: "subscribe",
  channels: ["posts:abc-123"]  // posts with ID abc-123
}));

// Subscribe to all posts events
ws.send(JSON.stringify({
  action: "subscribe",
  channels: ["posts:*"]
}));
```

## Event Format

Realtime events have this structure:

```json
{
  "channel": "posts",
  "event": "create",
  "data": {
    "id": "new-post-id",
    "title": "New Post",
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

## Disabling Auto-Emit

By default, Zork automatically emits events for all CRUD operations. Disable this per collection:

```python
app.realtime.disable_auto_emit("audit_logs")  # Don't emit for audit logs
```

Or disable entirely:

```python
app.realtime.enabled = False
```

## Publishing Custom Events

Publish your own events from hooks:

```python
@posts.on("after_create")
async def notify_followers(post, ctx):
    await app.realtime.publish("posts:new", {
        "event": "create",
        "data": post
    })
```

## Authentication

Realtime connections can be authenticated:

```javascript
// WebSocket with auth
const ws = new WebSocket(
  "ws://localhost:8000/api/realtime",
  [],  // protocols
  {
    headers: {
      "Authorization": "Bearer YOUR_TOKEN"
    }
  }
);
```

Authenticated connections have access to the same access control rules as REST endpoints.

## Redis Broker

For multi-process deployments, use the Redis broker:

```python
app.configure_redis(url="redis://localhost:6379/0")
```

This enables Redis pub/sub for realtime events across multiple server processes.

## Event Filtering

Access control rules apply to realtime events. Clients only receive events for records they have permission to see:

```python
# Only authenticated users can receive updates
app.register(posts, auth=["read:authenticated"])
```

Unauthenticated SSE/WebSocket connections receive events only for public collections.

## Presence (Advanced)

For presence features (online users, typing indicators), implement custom logic using the broker:

```python
# Track user presence
@app.on("app:startup")
async def setup_presence(ctx):
    async def track_user_presence(user_id):
        await app.realtime.publish("presence", {
            "user_id": user_id,
            "online": True
        })
```

## Next Steps

- [WebSocket](/realtime/websocket) — Detailed WebSocket usage
- [SSE](/realtime/sse) — Detailed SSE usage
- [Redis Broker](/realtime/redis-broker) — Multi-process scaling
