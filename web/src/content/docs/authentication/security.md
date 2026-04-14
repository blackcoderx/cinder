---
title: Security
description: How Zeno handles passwords, tokens, and email verification
---

## Passwords

Passwords are hashed using **bcrypt** via `passlib`. The hash is stored in the `_users` table and never returned in any API response.

- Work factor is the `passlib` default (12 rounds)
- Plaintext passwords are never logged or stored
- The `password` column is excluded from all user responses

## JWT tokens

Zeno uses **python-jose** with HS256 signing.

**Token payload:**
- `sub` — user ID
- `role` — user role
- `jti` — unique token identifier (used for revocation)
- `exp` — expiry timestamp

**Revocation:**
When a user logs out, the token's `jti` is stored in `_token_blocklist` with its expiry time. Expired blocklist entries are cleaned up on startup. Any request using a revoked token receives a `401 Token has been revoked` error.

**Secret key:**
Set `ZENO_SECRET` to a long random string. Generate one with:

```bash
zeno generate-secret
```

Without a secret, Zeno auto-generates one at startup — this means all tokens are invalidated on every restart.

## Email verification

After registration, Zeno generates a time-limited verification token and stores it in `_email_verifications`. If an email backend is configured, it sends the link to the user.

- Verification tokens expire (checked at use time)
- The `GET /api/auth/verify-email?token=...` endpoint sets `is_verified = 1`
- Expired tokens are cleaned up on startup

**Requiring verified email:**
Zeno does not block unverified users by default. To enforce this, add a hook:

```python
@auth.on("before_login")
async def require_verified(body, ctx):
    # This runs before the password check; use after_login if you need the user object
    return body

@auth.on("after_login")
async def check_verified(user, ctx):
    from zeno.errors import ZenoError
    if not user.get("is_verified"):
        raise ZenoError(403, "Please verify your email before logging in")
```

## Password reset

Password reset tokens are UUIDs stored in `_password_resets` with a 1-hour expiry. The token is consumed (deleted) after a successful reset. If the email doesn't exist, the endpoint returns 200 without revealing that fact (to prevent user enumeration).

## HTTPS

Zeno does not enforce HTTPS internally. In production, always deploy behind a reverse proxy (nginx, Caddy, Cloudflare) that terminates TLS.

## Token storage (client side)

Store JWT tokens in memory or `localStorage` on the client. If you use `localStorage`, be aware of XSS risks. `HttpOnly` cookies are a more secure alternative — implement this with a custom middleware if needed.
