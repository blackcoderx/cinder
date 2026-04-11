---
title: Realtime
description: Live updates via WebSocket and Server-Sent Events
---

Cinder automatically broadcasts events for every CRUD operation. Clients connect over WebSocket or SSE and receive filtered updates in real time.

## How it works

When a record is created, updated, or deleted, Cinder fires an event through the realtime broker. Connected clients receive the event if they pass the access control check for that collection.

## Connecting

### WebSocket

```
ws://localhost:8000/api/realtime
```

Authenticate by sending the JWT token in the first message after connecting:

```json
{ "type": "auth", "token": "eyJ..." }
```

### Server-Sent Events

```
GET /api/realtime/sse
```

Pass the token as a query parameter:

```
GET /api/realtime/sse?token=eyJ...
```

## Event format

All events follow this envelope structure:

```json
{
  "channel": "collection:posts",
  "event": "create",
  "collection": "posts",
  "record": {
    "id": "...",
    "title": "New Post",
    "created_at": "..."
  },
  "id": "...",
  "ts": "2024-01-01T00:00:00+00:00"
}
```

For `update` events, a `previous` field contains the record's state before the change.

The `event` field is one of `create`, `update`, or `delete`. Channels follow the pattern `collection:{name}`.

## Access control filtering

Events are filtered per-client based on the same access control rules used for the REST endpoints. A client only receives events for records they are allowed to read:

- `read:public` — broadcast to all connected clients
- `read:authenticated` — only authenticated clients
- `read:owner` — only the client who owns the record
- `read:admin` — only admin clients

## Scaling with Redis

The default in-process broker works for a single server process. For multi-process deployments (multiple workers, horizontal scaling), switch to the Redis broker:

```python
app.configure_redis(url="redis://localhost:6379")
```

Or set the environment variable:

```
CINDER_REDIS_URL=redis://localhost:6379
```

See [Realtime with Redis](/realtime/redis/) for details.

## Full documentation

- [WebSocket](/realtime/websocket/) — connection lifecycle, message protocol
- [Server-Sent Events](/realtime/sse/) — streaming events over HTTP
- [Redis Broker](/realtime/redis/) — scaling realtime to multiple workers
