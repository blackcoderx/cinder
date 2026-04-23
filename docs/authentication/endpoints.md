# Auth Endpoints

This guide documents all authentication endpoints and their request/response formats.

## Register

Create a new user account.

**Endpoint:** `POST /api/auth/register`

**Request:**

```json
{
  "email": "alice@example.com",
  "password": "secret123",
  "username": "alice"  // optional
}
```

**Extended fields** can be included if configured:

```json
{
  "email": "alice@example.com",
  "password": "secret123",
  "first_name": "Alice",
  "last_name": "Smith"
}
```

**Response (201 Created):**

```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "user-123",
    "email": "alice@example.com",
    "username": "alice",
    "role": "user",
    "is_verified": false,
    "is_active": true,
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

With cookie delivery, the token is set in an HTTP-only cookie instead of the response body.

**Error Responses:**

| Status | Error |
|--------|-------|
| 400 | Email already registered |
| 400 | Username already taken |
| 400 | Password too short |
| 403 | Registration disabled |

## Login

Authenticate and receive tokens.

**Endpoint:** `POST /api/auth/login`

**Request:**

```json
{
  "email": "alice@example.com",
  "password": "secret123"
}
```

**Response (200 OK):**

```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "user-123",
    "email": "alice@example.com",
    "role": "user",
    "is_verified": false,
    "is_active": true
  }
}
```

**Error Responses:**

| Status | Error |
|--------|-------|
| 400 | Email and password are required |
| 401 | Invalid email or password |
| 403 | Account is disabled |

## Logout

Log out and revoke the current token.

**Endpoint:** `POST /api/auth/logout`

**Headers:**

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response (200 OK):**

```json
{
  "message": "Logged out"
}
```

With cookie delivery, the cookies are cleared automatically.

**Error Responses:**

| Status | Error |
|--------|-------|
| 401 | Authentication required |

## Get Current User

Get the authenticated user's profile.

**Endpoint:** `GET /api/auth/me`

**Headers:**

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response (200 OK):**

```json
{
  "id": "user-123",
  "email": "alice@example.com",
  "username": "alice",
  "role": "user",
  "is_verified": false,
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

**Error Responses:**

| Status | Error |
|--------|-------|
| 401 | Authentication required |

## Refresh Token

Get a new access token using the refresh token.

**Endpoint:** `POST /api/auth/refresh`

### With Bearer Delivery

Requires the current access token:

**Headers:**

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response (200 OK):**

```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."  // new token
}
```

### With Cookie Delivery

Sends the refresh token in the cookie automatically:

**Response (200 OK):**

```json
{
  "message": "Token refreshed"
}
```

New access and refresh tokens are set in cookies.

## Forgot Password

Request a password reset email.

**Endpoint:** `POST /api/auth/forgot-password`

**Request:**

```json
{
  "email": "alice@example.com"
}
```

**Response (200 OK):**

```json
{
  "message": "If the email exists, a reset link has been generated"
}
```

Note: The response is always the same, even if the email does not exist. This prevents email enumeration attacks.

If email is configured, a password reset email is sent. If not configured, the reset token is logged to the console.

## Reset Password

Reset password using a token from the forgot password flow.

**Endpoint:** `POST /api/auth/reset-password`

**Request:**

```json
{
  "email": "alice@example.com",
  "token": "reset-token-from-email",
  "new_password": "newsecret123"
}
```

**Response (200 OK):**

```json
{
  "message": "Password updated"
}
```

Note: The `email` field is now required for secure token lookup.

This also revokes all refresh tokens for the user, forcing re-login on all devices.

**Error Responses:**

| Status | Error |
|--------|-------|
| 400 | Invalid or expired reset token |
| 400 | Token and new_password are required |

## Verify Email

Verify an email address using a token.

**Endpoint:** `GET /api/auth/verify-email`

**Query Parameters:**

```
?token=verification-token
```

**Response (200 OK):**

```json
{
  "message": "Email verified successfully"
}
```

This endpoint is typically accessed via a link in a verification email.

**Error Responses:**

| Status | Error |
|--------|-------|
| 400 | Invalid or expired verification token |

## Complete Example Flow

### Registration

```bash
# Register a new user
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "alice@example.com", "password": "secret123"}'
```

### Login

```bash
# Login and save the token
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "alice@example.com", "password": "secret123"}' \
  | jq -r '.token')

# Use the token to access protected endpoints
curl http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

### Password Reset

```bash
# Request password reset
curl -X POST http://localhost:8000/api/auth/forgot-password \
  -H "Content-Type: application/json" \
  -d '{"email": "alice@example.com"}'

# Reset password (token from email)
curl -X POST http://localhost:8000/api/auth/reset-password \
  -H "Content-Type: application/json" \
  -d '{"token": "RESET_TOKEN", "new_password": "newsecret"}'
```

## Next Steps

- [Security](/authentication/security) — Security best practices
- [User Model](/authentication/user-model) — Understanding the user table
