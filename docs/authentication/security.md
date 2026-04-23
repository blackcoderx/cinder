# Authentication Security

This guide covers security features and best practices for Zork authentication.

## Password Security

### Password Hashing

Zork uses bcrypt for password hashing:

- Passwords are never stored in plain text
- Each hash includes a salt
- Configurable work factor (default: 12 rounds)

### Password Requirements

Users must provide passwords with at least 8 characters. Additional validation can be added in hooks:

```python
@auth.on("before_register")
async def validate_password(data, ctx):
    password = data.get("password", "")
    
    if len(password) < 8:
        raise ZorkError(400, "Password must be at least 8 characters")
    
    if not any(c.isupper() for c in password):
        raise ZorkError(400, "Password must contain uppercase letter")
    
    if not any(c.isdigit() for c in password):
        raise ZorkError(400, "Password must contain a number")
    
    return data
```

## JWT Tokens

### Token Structure

Zork uses HS256 JWT tokens with these claims:

| Claim | Description |
|-------|-------------|
| `sub` | User ID |
| `role` | User role |
| `jti` | Unique token ID (for revocation) |
| `iat` | Issued at timestamp |
| `exp` | Expiration timestamp |
| `type` | Token type (access or refresh) |

### Token Expiry

Configure token lifetimes:

```python
auth = Auth(
    access_token_expiry=3600,       # 1 hour
    refresh_token_expiry=604800,    # 7 days
)
```

Shorter access token expiry means more frequent refreshes but less exposure if a token is compromised.

### Token Rotation

Refresh tokens are rotated on each use. Old refresh tokens are invalidated after use. This prevents replay attacks.

## Token Blocklist

When users log out, their tokens are added to a blocklist. Valid requests with blocked tokens are rejected.

### Database Blocklist

The default blocklist stores revoked tokens in the database:

- Tokens are checked against the blocklist on each request
- Expired tokens are cleaned up on application startup
- Suitable for single-server deployments

### Redis Blocklist

For production with multiple servers:

```python
auth = Auth(blocklist_backend="redis")
```

Benefits:

- Shared blocklist across all servers
- O(1) token lookups
- Automatic expiration via Redis TTL

## CSRF Protection

When using cookie-based authentication, Zork implements CSRF protection via the double-submit cookie pattern.

### How It Works

1. On login, Zork sets a CSRF token cookie (readable by JavaScript)
2. Client must send the token in the `X-CSRF-Token` header
3. Zork validates the header matches the cookie

### Configuration

```python
auth = Auth(
    token_delivery="cookie",
    csrf_enabled=True,        # Enable CSRF protection
    cookie_samesite="strict",  # Strict SameSite policy
    cookie_secure=True,       # HTTPS only
)
```

### Making Requests with CSRF

```javascript
// Get CSRF token from cookie
const csrfToken = document.cookie
  .split('; ')
  .find(row => row.startsWith('csrf_token='))
  .split('=')[1];

// Include in request header
fetch('/api/posts', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRF-Token': csrfToken
  },
  body: JSON.stringify({ title: 'My Post' })
});
```

## Cookie Security

When using cookie-based authentication:

```python
auth = Auth(
    token_delivery="cookie",
    cookie_secure=True,      # HTTPS only (default: True)
    cookie_samesite="lax",   # SameSite policy
    cookie_domain=".example.com",  # Cookie domain
)
```

### Cookie Flags

| Flag | Description |
|------|-------------|
| `HttpOnly` | Cannot be read by JavaScript (XSS protection) |
| `Secure` | Only sent over HTTPS |
| `SameSite` | Controls when cookies are sent cross-origin |

### SameSite Options

| Value | Behavior |
|-------|----------|
| `strict` | Cookies only sent in first-party context |
| `lax` | Cookies sent on top-level navigations and GET requests |
| `none` | Cookies sent in all contexts (requires Secure) |

## Secret Key Management

### Setting the Secret

Generate a secure secret:

```bash
zork generate-secret
```

Set it as an environment variable:

```bash
ZORK_SECRET=your-generated-secret-here
```

### Secret Requirements

- Use a cryptographically random string (at least 32 bytes)
- Never commit secrets to version control
- Rotate secrets periodically
- Use different secrets for different environments

### Production Best Practices

```bash
# Generate a new secret
zork generate-secret

# In production, set via environment
export ZORK_SECRET=$(zork generate-secret)
```

## Token Refresh Limits

Limit the number of active refresh tokens per user:

```python
auth = Auth(max_refresh_tokens=5)
```

When a user exceeds the limit, the oldest token is automatically revoked.

## Account Security

### Email Verification

Require email verification before allowing certain actions:

```python
@posts.on("before_create")
async def require_verified_email(data, ctx):
    if ctx.user and not ctx.user.get("is_verified"):
        raise ZorkError(403, "Please verify your email first")
    return data
```

### Account Lockout

Implement login attempt limiting:

```python
from datetime import datetime, timezone

MAX_ATTEMPTS = 5
LOCKOUT_DURATION = 300  # 5 minutes

@auth.on("before_login")
async def check_lockout(data, ctx):
    user = await get_user_by_email(data.get("email"))
    if user:
        attempts = user.get("login_attempts", 0)
        last_attempt = user.get("last_login_attempt")
        
        if attempts >= MAX_ATTEMPTS:
            lockout_end = datetime.fromisoformat(last_attempt).timestamp() + LOCKOUT_DURATION
            if datetime.now(timezone.utc).timestamp() < lockout_end:
                raise ZorkError(403, "Account temporarily locked")
    
    return data
```

### Password Change Security

When a user changes their password, all refresh tokens are revoked:

```python
# This is handled automatically by Zork
# Users must re-authenticate on all devices
```

## Security Checklist

Before deploying to production:

- Set `ZORK_SECRET` to a cryptographically secure value
- Enable `cookie_secure=True` for cookie authentication
- Configure appropriate token expiry times
- Enable CSRF protection for cookie delivery
- Use Redis blocklist for multi-server deployments
- Consider implementing rate limiting with `app.rate_limit.auth_limits()`
- Enable email verification for sensitive operations
- Monitor for unusual authentication patterns

## Optional Rate Limiting

Zork includes built-in rate limiting that you can enable for auth endpoints:

```python
app = Zork()
app.rate_limit.auth_limits()
```

This applies stricter limits to authentication endpoints:
- Login: 5 requests/minute per IP
- Register: 3 requests/minute per IP
- Forgot password: 3 requests/hour per IP

Disable rate limiting entirely if needed:

```python
app.rate_limit.enable(False)
# Or via environment: ZORK_RATE_LIMIT_ENABLED=false
```

Or customize specific endpoints:

```python
app = Zork()
app.rate_limit.default(limit=100, window=60)  # Default: 100 req/min
app.rate_limit.rule("/api/auth/login", limit=10, window=60, scope="ip")  # Custom
```

## Next Steps

- [Setup](/authentication/setup) — Configuring authentication
- [User Model](/authentication/user-model) — Managing user accounts
- [Rate Limiting](/rate-limiting/setup) — Protecting against brute force
