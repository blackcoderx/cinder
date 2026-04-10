---
title: Security
description: How Cinder protects your users
---

Understanding the security mechanisms behind Cinder's authentication system.

## Password Hashing

Cinder uses [bcrypt](https://en.wikipedia.org/wiki/Bcrypt) for password storage.

### How It Works

```python
# Cinder never stores plain passwords
password_hash = bcrypt_hash(plain_password)
# Stored in database: "$2b$12$..."
```

### Security Features

| Feature | Benefit |
|---------|---------|
| Automatic salt | Same password produces different hashes |
| Cost factor | Configurable work factor (default: 12) |
| Constant-time comparison | Resistant to timing attacks |

### Why Bcrypt?

- **Purpose-built** for password hashing
- **Adaptive** — cost factor can increase over time
- **Battle-tested** — used by millions of applications
- **Easy to use** — handles salt generation automatically

## JWT Tokens

Cinder uses [JSON Web Tokens (JWT)](https://jwt.io/) with the HS256 algorithm.

### Token Structure

A JWT has three parts: header, payload, signature.

```javascript
// Header
{ "alg": "HS256", "typ": "JWT" }

// Payload (what you decode)
{
  "sub": "user-uuid",           // Subject (user ID)
  "role": "user",               // User's role
  "jti": "unique-token-id",     // JWT ID (for revocation)
  "iat": 1712736000,            // Issued at (Unix timestamp)
  "exp": 1712822400             // Expires at (default: 24h)
}

// Signature
HMACSHA256(header.payload, secret)
```

### What the Token Contains

| Claim | Description |
|-------|-------------|
| `sub` | User's UUID |
| `role` | User's role (`user`, `admin`, etc.) |
| `jti` | Unique identifier — used for blocklist |
| `iat` | When the token was created |
| `exp` | When the token expires |

### What the Token Does NOT Contain

- Password hash
- Sensitive user data
- Any data that changes frequently (roles are embedded at issue time)

## Token Blocklist

When a user logs out, their token is added to a blocklist. Every request checks this list.

```
┌─────────────────────────────────────────────────────────┐
│                    Token Validation                       │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  1. Decode JWT ──────────→ Invalid? ───→ Reject (401)  │
│         │                                                  │
│         ↓                                                  │
│  2. Check expiration ──→ Expired? ───→ Reject (401)    │
│         │                                                  │
│         ↓                                                  │
│  3. Check blocklist ───→ Blocked? ───→ Reject (401)    │
│         │                                                  │
│         ↓                                                  │
│  4. Valid token ────────────────→ Allow request          │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

The blocklist stores only:
- Token ID (`jti`)
- Expiration timestamp

Expired blocklist entries are automatically cleaned up on startup.

## Secret Key

The secret key signs all tokens. It's critical for security.

### Configuration Priority

| Priority | Source | Notes |
|----------|--------|-------|
| 1 (highest) | `CINDER_SECRET` env var | Recommended for production |
| 2 (fallback) | Auto-generated | Works but tokens won't survive restarts |

### Best Practice

```bash
# Generate a secret
cinder generate-secret

# Set as environment variable
export CINDER_SECRET="your-secret-here"
```

### Same Secret Required

All instances sharing a database must use the same `CINDER_SECRET`:
- Same secret = tokens are valid
- Different secret = tokens are rejected

## What Cinder Protects Against

| Threat | Protection |
|--------|------------|
| Password storage | Bcrypt hashing (not reversible) |
| Token replay | Token blocklist on logout |
| Expired token reuse | Expiration check in validation |
| Forged tokens | Signature verification with secret |
| Password enumeration | Same error message for wrong email/password |
| Email enumeration | Same response for existing/non-existent email |

## Security Best Practices

### DO

- Set `CINDER_SECRET` in production
- Use HTTPS in production
- Keep `token_expiry` reasonable (24h is default)
- Enable email verification for sensitive apps
- Use strong password policies (via hooks)

### DON'T

- Share `CINDER_SECRET` across different apps
- Set very long token expiry without risk assessment
- Skip HTTPS in production
- Disable email verification for untrusted registrations

## Related

- [Setup](/authentication/setup/) — Configure auth
- [Endpoints](/authentication/endpoints/) — Auth API reference
- [Troubleshooting](/authentication/troubleshooting/) — Debug auth issues
