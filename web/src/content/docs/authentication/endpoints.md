---
title: Endpoints
description: Authentication API reference
---

All auth endpoints are prefixed with `/api/auth/`.

## Endpoints Overview

| Endpoint | Method | Auth Required | Description |
|----------|--------|---------------|-------------|
| `/api/auth/register` | POST | No | Create a new user |
| `/api/auth/login` | POST | No | Authenticate and get token |
| `/api/auth/me` | GET | Yes | Get current user info |
| `/api/auth/logout` | POST | Yes | Revoke current token |
| `/api/auth/refresh` | POST | Yes | Get a new token |
| `/api/auth/forgot-password` | POST | No | Request password reset |
| `/api/auth/reset-password` | POST | No | Complete password reset |
| `/api/auth/verify-email` | GET | No | Verify email address |

## Register

**`POST /api/auth/register`**

Create a new user account.

**Request:**
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "secure123",
    "username": "john"
  }'
```

**Response (201):**
```json
{
  "token": "eyJhbGciOi...",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "username": "john",
    "role": "user",
    "is_verified": 0,
    "is_active": 1,
    "created_at": "2026-04-10T12:00:00+00:00",
    "updated_at": "2026-04-10T12:00:00+00:00"
  }
}
```

**Hooks fired:** `auth:before_register` → `auth:after_register`

**Error responses:**
| Status | Condition |
|--------|-----------|
| 400 | Email already exists |
| 400 | Username already exists |
| 403 | Registration disabled |

## Login

**`POST /api/auth/login`**

Authenticate and receive a token.

**Request:**
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "secure123"
  }'
```

**Response (200):**
```json
{
  "token": "eyJhbGciOi...",
  "user": { ... }
}
```

**Hooks fired:** `auth:before_login` → `auth:after_login`

**Error responses:**
| Status | Condition |
|--------|-----------|
| 401 | Invalid email or password |
| 403 | Account disabled |

## Get Current User

**`GET /api/auth/me`**

Get the authenticated user's profile.

**Request:**
```bash
curl http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer eyJhbGciOi..."
```

**Response (200):**
```json
{
  "id": "550e8400-...",
  "email": "user@example.com",
  "username": "john",
  "role": "user",
  "is_verified": 0,
  "is_active": 1,
  "created_at": "2026-04-10T12:00:00+00:00",
  "updated_at": "2026-04-10T12:00:00+00:00"
}
```

**Error responses:**
| Status | Condition |
|--------|-----------|
| 401 | No token or invalid token |

## Logout

**`POST /api/auth/logout`**

Revoke the current token. The token cannot be used after this.

**Request:**
```bash
curl -X POST http://localhost:8000/api/auth/logout \
  -H "Authorization: Bearer eyJhbGciOi..."
```

**Response (200):**
```json
{
  "message": "Logged out"
}
```

**Hooks fired:** `auth:before_logout` → `auth:after_logout`

## Refresh Token

**`POST /api/auth/refresh`**

Get a new token. The old token is automatically revoked.

**Request:**
```bash
curl -X POST http://localhost:8000/api/auth/refresh \
  -H "Authorization: Bearer eyJhbGciOi..."
```

**Response (200):**
```json
{
  "token": "eyJhbGciOi..."  // New token
}
```

**Security:** Old token is added to blocklist.

## Forgot Password

**`POST /api/auth/forgot-password`**

Request a password reset email.

**Request:**
```bash
curl -X POST http://localhost:8000/api/auth/forgot-password \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com"}'
```

**Response (200):**
```json
{
  "message": "If the email exists, a reset link has been generated"
}
```

**Hooks fired:** `auth:before_password_reset` → `auth:after_password_reset`

**Note:** Always returns the same message to prevent email enumeration.

**Without email configured:** The reset token is logged to the console.

## Reset Password

**`POST /api/auth/reset-password`**

Complete the password reset with a token.

**Request:**
```bash
curl -X POST http://localhost:8000/api/auth/reset-password \
  -H "Content-Type: application/json" \
  -d '{
    "token": "reset-token",
    "new_password": "newsecure123"
  }'
```

**Response (200):**
```json
{
  "message": "Password updated"
}
```

**Error responses:**
| Status | Condition |
|--------|-----------|
| 400 | Invalid or expired token |

## Verify Email

**`GET /api/auth/verify-email?token=<token>`**

Verify a user's email address.

**Request:**
```bash
curl "http://localhost:8000/api/auth/verify-email?token=verification-token"
```

**Response (200):**
```json
{
  "message": "Email verified successfully"
}
```

**Hooks fired:** `auth:after_verify_email`

**Error responses:**
| Status | Condition |
|--------|-----------|
| 400 | Invalid, expired, or already-used token |

## Using Tokens

Include the token in the `Authorization` header:

```bash
curl -X POST http://localhost:8000/api/posts \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOi..." \
  -d '{"title": "My Post"}'
```

**Token format:** `Bearer <token>`

## Error Response Format

All auth endpoints return errors in this format:

```json
{
  "error": "Error message here"
}
```

## Security Notes

- Tokens expire after `token_expiry` seconds (default: 24 hours)
- Logout revokes the token immediately via blocklist
- Invalid tokens return 401
- Passwords are never stored or logged in plain text
- Same error message for wrong email vs wrong password (prevents enumeration)

## Next Steps

- [Setup](/authentication/setup/) — Configure auth
- [User Model](/authentication/user-model/) — Extend user fields
- [Hooks](/authentication/hooks/) — React to auth events
- [Security](/authentication/security/) — How auth protects your users
