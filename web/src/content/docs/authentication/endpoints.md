---
title: Endpoints
description: Request and response shapes for every auth route
---

## POST /api/auth/register

Register a new user.

**Request:**
```json
{
  "email": "alice@example.com",
  "password": "secret123",
  "username": "alice"
}
```

`username` is optional. Any extended user fields (from `Auth(extend_user=[...])`) are also accepted.

**Response `201`:**
```json
{
  "token": "eyJ...",
  "user": {
    "id": "...",
    "email": "alice@example.com",
    "username": "alice",
    "role": "user",
    "is_verified": 0,
    "is_active": 1,
    "created_at": "..."
  }
}
```

**Errors:**
- `400` — email or password missing
- `400` — email already registered
- `400` — username already taken
- `403` — registration is disabled (`allow_registration=False`)

---

## POST /api/auth/login

Log in with email and password.

**Request:**
```json
{
  "email": "alice@example.com",
  "password": "secret123"
}
```

**Response `200`:**
```json
{
  "token": "eyJ...",
  "user": { ... }
}
```

**Errors:**
- `400` — email or password missing
- `401` — invalid email or password
- `403` — account is disabled

---

## GET /api/auth/me

Get the currently authenticated user. Requires `Authorization: Bearer <token>`.

**Response `200`:**
```json
{
  "id": "...",
  "email": "alice@example.com",
  "role": "user",
  "is_verified": 1,
  ...
}
```

**Errors:**
- `401` — no token or invalid token

---

## POST /api/auth/logout

Revoke the current token. Requires `Authorization: Bearer <token>`.

The token's JTI is added to a blocklist. Any subsequent request with the same token is rejected.

**Response `200`:**
```json
{ "message": "Logged out" }
```

---

## POST /api/auth/refresh

Revoke the current token and issue a new one with a fresh expiry. Requires `Authorization: Bearer <token>`.

**Response `200`:**
```json
{ "token": "eyJ..." }
```

---

## POST /api/auth/forgot-password

Request a password reset link. Always returns 200 regardless of whether the email exists (to prevent user enumeration).

**Request:**
```json
{ "email": "alice@example.com" }
```

**Response `200`:**
```json
{
  "message": "If the email exists, a reset link has been generated"
}
```

If an email backend is configured, a reset link is sent. Otherwise, the token is logged to the console.

---

## POST /api/auth/reset-password

Apply a password reset using the token from the email.

**Request:**
```json
{
  "token": "the-reset-token",
  "new_password": "newpassword123"
}
```

**Response `200`:**
```json
{ "message": "Password updated" }
```

**Errors:**
- `400` — token or new_password missing
- `400` — invalid or expired token

---

## GET /api/auth/verify-email

Verify a user's email address using the token from the verification email.

```
GET /api/auth/verify-email?token=the-verification-token
```

**Response `200`:**
```json
{ "message": "Email verified successfully" }
```

**Errors:**
- `400` — token missing or invalid
- `400` — token expired
