---
title: Server-Sent Events
description: Use SSE for unidirectional server-to-client streaming
---

Connect to `/api/realtime/sse` with query parameters. The browser's native `EventSource` API works out of the box.

## Subscribe

```
GET /api/realtime/sse?channel=collection:posts
GET /api/realtime/sse?channel=collection:posts&channel=collection:comments
GET /api/realtime/sse?token=eyJhbGciOi...&channel=collection:notes
```

| Query param | Required | Description |
|-------------|----------|-------------|
| `channel` | Yes | One or more channel names (repeatable) |
| `token` | Only for protected collections | JWT bearer token |

## SSE Frame Format

Each event is sent as a standard SSE frame:

```
event: create
data: {"channel":"collection:posts","event":"create","record":{...},"previous":null}
id: <record-id>
```

A `: ping` comment is sent every 15 seconds to keep the connection alive.

## Browser Example

```javascript
const token = localStorage.getItem("token");
const url = `/api/realtime/sse?token=${token}&channel=collection:posts`;
const source = new EventSource(url);

source.addEventListener("create", (e) => {
  const data = JSON.parse(e.data);
  console.log("New post:", data.record);
});

source.addEventListener("update", (e) => {
  const data = JSON.parse(e.data);
  console.log("Post updated:", data.record);
});

source.addEventListener("delete", (e) => {
  const data = JSON.parse(e.data);
  console.log("Post deleted:", data.record.id);
});

source.onerror = () => {
  console.error("SSE connection lost, browser will retry automatically");
};
```

## Auth-Aware Filtering

| Read rule | SSE behaviour |
|-----------|----------------|
| `public` | All clients receive events |
| `authenticated` | Only authenticated clients receive events |
| `admin` | Only admin clients receive events |
| `owner` | Each client only receives events for their records |

Pass `?token=` in the query string to authenticate.

## Configuration

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `CINDER_SSE_HEARTBEAT` | `15` | Seconds between ping comments |

```sh
CINDER_SSE_HEARTBEAT=30
```

## Why Use SSE?

- **Simpler than WebSocket** — No connection management
- **Works everywhere** — Native browser support
- **One-way** — Server to client only
- **Automatic reconnection** — Built into EventSource

## Next Steps

- [WebSocket](/realtime/websocket/) — Bidirectional communication
- [Custom Channels](/realtime/channels/) — Publish your own events
- [Overview](/realtime/overview/) — Full realtime docs