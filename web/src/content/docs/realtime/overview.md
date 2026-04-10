---
title: Overview
description: Introduction to Cinder's realtime capabilities
---

Cinder has built-in realtime support via **WebSockets** and **Server-Sent Events (SSE)**.

## Transports

| Endpoint | Transport | Description |
|----------|-----------|-------------|
| `GET /api/realtime/ws` | WebSocket | Persistent bidirectional connection |
| `GET /api/realtime/sse` | Server-Sent Events | HTTP streaming, browser-native |

## Channels

Everything in Cinder's realtime system is organized around **channels**:

| Channel format | Example | Description |
|----------------|---------|-------------|
| `collection:{name}` | `collection:posts` | Auto-emitted CRUD events |
| Custom string | `chat:room-42` | Your own events |

## Auto-Emit Bridge

When you register a collection, Cinder automatically emits events on every `create`, `update`, and `delete`.

**Envelope format:**

```json
{
  "channel": "collection:posts",
  "event": "create",
  "record": { "id": "...", "title": "Hello" },
  "previous": null
}
```

| Field | Values | Description |
|-------|--------|-------------|
| `channel` | `collection:{name}` | The channel |
| `event` | `create`, `update`, `delete` | Operation |
| `record` | object | Current state |
| `previous` | object or `null` | Previous state (only on `update`) |

## Enabling Realtime

Realtime is enabled automatically when you call `app.build()`. No extra install needed.

## Next Steps

- [WebSocket](/realtime/websocket/) — Bidirectional communication
- [SSE](/realtime/sse/) — Server-to-client streaming
- [Custom Channels](/realtime/channels/) — Publish your own events