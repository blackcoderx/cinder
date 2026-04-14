---
title: User Model
description: The _users table structure
---

When you call `app.use_auth(auth)`, Zeno creates a `_users` table in your database. You never define this table yourself — it is managed entirely by Zeno.

## Default columns

| Column | Type | Description |
|--------|------|-------------|
| `id` | `TEXT` (UUID) | Primary key, auto-generated |
| `email` | `TEXT` | Unique email address |
| `username` | `TEXT` | Optional unique username |
| `password` | `TEXT` | bcrypt-hashed password (never returned in API responses) |
| `role` | `TEXT` | User role; defaults to `"user"` |
| `is_verified` | `INTEGER` | `1` if email is verified, `0` otherwise |
| `is_active` | `INTEGER` | `1` if account is active. Inactive accounts cannot log in. |
| `created_at` | `TEXT` | ISO 8601 timestamp |
| `updated_at` | `TEXT` | ISO 8601 timestamp |

## Extended columns

Pass `extend_user` to `Auth` to add extra columns:

```python
auth = Auth(
    extend_user=[
        TextField("display_name"),
        TextField("bio"),
    ]
)
```

Extended fields are accepted in the register request body and stored in `_users`.

## Reading the current user

`GET /api/auth/me` returns all user fields except `password`:

```json
{
  "id": "...",
  "email": "alice@example.com",
  "username": null,
  "role": "user",
  "is_verified": 1,
  "is_active": 1,
  "created_at": "2024-01-01T00:00:00+00:00",
  "updated_at": "2024-01-01T00:00:00+00:00"
}
```

## Roles

The default role for new users is `"user"`. Promote a user to admin:

```bash
zeno promote alice@example.com
zeno promote alice@example.com --role moderator
```

Roles are checked by `read:admin` and `write:admin` access control rules. Any string value is accepted — you can define your own role hierarchy.

## The password field

The `password` column stores a bcrypt hash. It is stripped from all API responses by `_user_response()`. Never expose it to clients.

## Supporting tables

In addition to `_users`, Zeno creates two helper tables:

| Table | Purpose |
|-------|---------|
| `_email_verifications` | Temporary tokens for email verification (auto-cleaned on startup) |
| `_password_resets` | Temporary tokens for password reset (1-hour expiry) |
| `_token_blocklist` | Revoked JWT IDs (auto-cleaned after token expiry) |
