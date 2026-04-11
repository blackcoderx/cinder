---
title: Rate Limiting
description: Protect your API from abuse with token-bucket rate limiting
sidebar:
  order: 1
---

Cinder includes a rate limiting middleware that uses the **token-bucket algorithm** to limit how many requests a client can make in a given time window. It is enabled by default.

## How it works

Each client gets a "bucket" of tokens. Every request consumes one token. Tokens refill at a steady rate. When the bucket is empty, the request receives `429 Too Many Requests`.

Clients are identified by:
- **Unauthenticated requests** — IP address
- **Authenticated requests** — user ID (from the JWT token)

## Default limits

| Client type | Default | Environment variable |
|-------------|---------|----------------------|
| Unauthenticated | 100 requests / 60 seconds | `CINDER_RATE_LIMIT_ANON` |
| Authenticated | 1000 requests / 60 seconds | `CINDER_RATE_LIMIT_USER` |

Override via environment variables:

```dotenv
CINDER_RATE_LIMIT_ANON=50/60     # 50 requests per minute for anonymous
CINDER_RATE_LIMIT_USER=500/60    # 500 per minute for authenticated users
```

## Per-route rules

Override limits for specific path prefixes:

```python
app.rate_limit.rule("/api/posts", limit=50, window=60)
app.rate_limit.rule("/api/auth/register", limit=5, window=60)
```

Per-route rules take precedence over the global defaults.

## Disabling rate limiting

```dotenv
CINDER_RATE_LIMIT_ENABLED=false
```

Or in code:

```python
app.rate_limit.enable(False)
```

## In this section

- [Configuration](/rate-limiting/configuration/) — backend setup, global defaults, and per-route rules
