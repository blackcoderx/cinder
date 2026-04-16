# Authentication Setup

Zork includes a complete authentication system with user registration, JWT tokens, and access control. This guide explains how to configure authentication for your application.

## Quick Setup

Enable authentication with minimal configuration:

```python
from zork import Zork, Auth

app = Zork(database="app.db")

auth = Auth(allow_registration=True)
app.use_auth(auth)
```

This enables all authentication endpoints and JWT token handling.

## Auth Constructor Options

The Auth class accepts several configuration options:

```python
auth = Auth(
    allow_registration=True,           # Enable user registration
    token_expiry=86400,               # Access token lifetime (default: 1 day)
    access_token_expiry=3600,        # Short-lived access token (default: 1 hour)
    refresh_token_expiry=604800,      # Long-lived refresh token (default: 7 days)
    max_refresh_tokens=5,             # Max refresh tokens per user
)
```

### Token Expiry Options

| Option | Default | Description |
|--------|---------|-------------|
| `token_expiry` | 86400 | Legacy option, use `access_token_expiry` |
| `access_token_expiry` | 3600 | Short-lived access token in seconds |
| `refresh_token_expiry` | 604800 | Long-lived refresh token in seconds |

Recommended values:

```python
# Standard setup
auth = Auth(
    access_token_expiry=3600,        # 1 hour
    refresh_token_expiry=604800,     # 7 days
)

# High security
auth = Auth(
    access_token_expiry=900,         # 15 minutes
    refresh_token_expiry=86400,      # 1 day
)

# Extended sessions
auth = Auth(
    access_token_expiry=86400,       # 1 day
    refresh_token_expiry=2592000,    # 30 days
)
```

## Token Delivery Modes

Zork supports two ways to deliver tokens to clients.

### Bearer Tokens (Default)

Tokens are returned in the response body and must be sent in the Authorization header:

```python
auth = Auth(token_delivery="bearer")  # Default
```

Response from login:

```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {...}
}
```

Client sends token:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

Best for: Mobile apps, SPAs storing tokens in localStorage, API clients.

### Cookie Delivery

Tokens are stored in HTTP-only cookies for enhanced security:

```python
auth = Auth(
    token_delivery="cookie",
    cookie_secure=True,              # Require HTTPS
    cookie_samesite="lax",           # SameSite policy: lax, strict, or none
    csrf_enabled=True,               # Enable CSRF protection
)
```

Best for: Traditional web applications, SSR applications.

Cookie delivery includes:

- HTTP-only cookies (protected from XSS)
- CSRF protection via double-submit cookie pattern
- Automatic token refresh

## Blocklist Backends

When users log out, their tokens are added to a blocklist. Zork supports different backends:

### Database Blocklist (Default)

Stores revoked tokens in the database:

```python
auth = Auth(blocklist_backend="database")  # Default
```

No additional configuration needed.

### Redis Blocklist

Stores revoked tokens in Redis for faster lookups:

```python
auth = Auth(blocklist_backend="redis")
```

Requires Redis configuration. See [Redis Setup](/caching/setup).

Benefits of Redis blocklist:

- O(1) token validation lookups
- Automatic token expiration
- Shared state across multiple servers

## Protecting Collections

Use the auth parameter on app.register to protect your collections:

```python
# Public read, authenticated write
app.register(posts, auth=["read:public", "write:authenticated"])

# Authenticated for everything
app.register(notes, auth=["read:authenticated", "write:authenticated"])

# Owner only
app.register(drafts, auth=["read:owner", "write:owner"])

# Admin only
app.register(settings, auth=["read:admin", "write:admin"])
```

See the [Access Control](/core-concepts/access-control) guide for all rules.

## Disabling Registration

Prevent new user registration while keeping other auth features:

```python
auth = Auth(allow_registration=False)
```

Users can still log in if accounts are created through other means (admin creation, seeding, etc.).

## Custom User Fields

Extend the user model with additional fields:

```python
from zork import Auth, TextField

auth = Auth(
    allow_registration=True,
    extend_user=[
        TextField("first_name"),
        TextField("last_name"),
        TextField("display_name"),
    ],
)
```

Users can then include these fields during registration:

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@example.com",
    "password": "secret123",
    "first_name": "Alice",
    "last_name": "Smith"
  }'
```

## Environment Variables

Configure authentication via environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `ZORK_ACCESS_TOKEN_EXPIRY` | Access token lifetime | 3600 |
| `ZORK_REFRESH_TOKEN_EXPIRY` | Refresh token lifetime | 604800 |
| `ZORK_AUTH_DELIVERY` | Token delivery mode | bearer |
| `ZORK_BLOCKLIST_BACKEND` | Blocklist backend | database |
| `ZORK_COOKIE_SECURE` | Require HTTPS for cookies | true |
| `ZORK_COOKIE_SAMESITE` | SameSite policy | lax |
| `ZORK_CSRF_ENABLE` | Enable CSRF protection | true |
| `ZORK_MAX_REFRESH_TOKENS` | Max tokens per user | 5 |

## Authentication Endpoints

Once enabled, these endpoints are available:

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/auth/register` | Create a new user |
| POST | `/api/auth/login` | Authenticate and get tokens |
| POST | `/api/auth/logout` | Revoke current token |
| GET | `/api/auth/me` | Get current user |
| POST | `/api/auth/refresh` | Get new access token |
| POST | `/api/auth/forgot-password` | Request password reset |
| POST | `/api/auth/reset-password` | Reset password with token |
| GET | `/api/auth/verify-email` | Verify email address |

See the [Auth Endpoints](/authentication/endpoints) guide for detailed request/response formats.

## Next Steps

- [User Model](/authentication/user-model) — Understanding the user table
- [Auth Endpoints](/authentication/endpoints) — Request and response formats
- [Security](/authentication/security) — Security best practices
