---
title: Authentication
description: Built-in JWT authentication for Zeno apps
---

Zeno ships with a complete authentication system: user registration and login, JWT access tokens, email verification, and password reset — all wired up with a single call.

## How it works

1. A user registers or logs in and receives a **JWT access token**
2. The client sends the token in the `Authorization: Bearer <token>` header on subsequent requests
3. Zeno's middleware validates the token and attaches the user to `request.state.user`
4. [Access control rules](/core-concepts/access-control/) use the authenticated user to decide whether to allow the request

## Enabling auth

```python
from zeno import Auth

auth = Auth(token_expiry=86400, allow_registration=True)
app.use_auth(auth)
```

`use_auth()` mounts all `/api/auth/*` endpoints and activates the JWT middleware for every request.

## Auth endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/auth/register` | Register a new user |
| `POST` | `/api/auth/login` | Log in and get a token |
| `GET` | `/api/auth/me` | Get the current user |
| `POST` | `/api/auth/logout` | Revoke the current token |
| `POST` | `/api/auth/refresh` | Issue a new token |
| `POST` | `/api/auth/forgot-password` | Request a password reset link |
| `POST` | `/api/auth/reset-password` | Apply a password reset |
| `GET` | `/api/auth/verify-email` | Verify email address via link |

## In this section

- [Setup](/authentication/setup/) — `Auth` constructor options and configuration
- [User Model](/authentication/user-model/) — the `_users` table structure
- [Endpoints](/authentication/endpoints/) — request/response shapes for each auth route
- [Hooks](/authentication/hooks/) — auth lifecycle events
- [Security](/authentication/security/) — JWT expiry, bcrypt, email verification
- [Troubleshooting](/authentication/troubleshooting/) — common errors and fixes
