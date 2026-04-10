---
title: WebSocket
description: Use WebSocket for bidirectional realtime communication
---

Connect to `/api/realtime/ws` and communicate via JSON messages.

## Connecting

```javascript
const ws = new WebSocket("ws://localhost:8000/api/realtime/ws");
```

No token is required on connection. You can authenticate mid-session.

## Subscribe to a Channel

Send a `subscribe` action to start receiving events:

```javascript
ws.send(JSON.stringify({ action: "subscribe", "channel": "collection:posts" }));
```

Cinder acknowledges with:

```json
{ "type": "ack", "action": "subscribe", "channel": "collection:posts" }
```

Subscribe to multiple channels by sending multiple `subscribe` messages.

## Receiving Events

Once subscribed, events arrive as JSON:

```json
{
  "channel": "collection:posts",
  "event": "create",
  "record": { "id": "abc", "title": "My Post" },
  "previous": null
}
```

## Unsubscribe

```javascript
ws.send(JSON.stringify({ action: "unsubscribe", "channel": "collection:posts" }));
```

## Authenticating Mid-Session

Send an `auth` message at any time:

```javascript
ws.send(JSON.stringify({ action: "auth", token: "eyJhbGciOi..." }));
```

Cinder responds with:

```json
{ "type": "ack", "action": "auth" }
```

On success, your user identity is attached to the connection.

If the token is invalid, the connection is closed with a `4401` close code.

## Full Browser Example

```javascript
const ws = new WebSocket("ws://localhost:8000/api/realtime/ws");

ws.onopen = () => {
  // Optionally authenticate first
  ws.send(JSON.stringify({ action: "auth", token: localStorage.getItem("token") }));

  // Subscribe to a collection channel
  ws.send(JSON.stringify({ action: "subscribe", channel: "collection:posts" }));
};

ws.onmessage = ({ data }) => {
  const msg = JSON.parse(data);

  if (msg.type === "ack") {
    console.log("Acknowledged:", msg.action);
    return;
  }

  if (msg.channel === "collection:posts") {
    console.log(`Post ${msg.event}d:`, msg.record);
  }
};

ws.onclose = (event) => {
  console.log("Disconnected:", event.code, event.reason);
};
```

## Auth-Aware Filtering

| Read rule | WebSocket behaviour |
|-----------|----------------------|
| `public` | All clients receive all events |
| `authenticated` | Only authenticated clients receive events |
| `admin` | Only clients with admin role receive events |
| `owner` | Each client only receives events for records they created |

## Next Steps

- [SSE](/realtime/sse/) — Server-to-client streaming
- [Custom Channels](/realtime/channels/) — Publish your own events
- [Overview](/realtime/overview/) — Full realtime docs