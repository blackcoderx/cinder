---
title: Troubleshooting
description: Common authentication errors and how to fix them
---

## "No ZENO_SECRET set — tokens will not survive restarts"

This warning means Zeno generated a random secret on startup. All tokens issued before the last restart are now invalid.

**Fix:** Set a stable secret in your `.env` file:

```dotenv
ZENO_SECRET=your-long-random-secret
```

Generate one: `zork generate-secret`

---

## 401 "Authentication required"

The request is missing the `Authorization` header.

**Fix:** Include the token:

```bash
curl -H "Authorization: Bearer eyJ..." http://localhost:8000/api/posts
```

---

## 401 "Token has been revoked"

The token was explicitly revoked via `POST /api/auth/logout`.

**Fix:** Log in again to get a new token.

---

## 401 "Token expired" or "Signature has expired"

The token's `exp` claim is in the past.

**Fix:**
- Use `POST /api/auth/refresh` before the token expires to get a new one
- Or log in again
- Increase `token_expiry` if the default (24 hours) is too short for your use case

---

## 403 "Registration is disabled"

`Auth(allow_registration=False)` is set.

**Fix:** Re-enable registration or create users via the database directly.

---

## 400 "Email already registered"

A user with that email exists.

**Fix:** Log in instead, or use a different email.

---

## 400 "Invalid or expired reset token"

The password reset token was already used, expired, or is incorrect.

**Fix:** Request a new reset link via `POST /api/auth/forgot-password`.

---

## Users don't receive verification or reset emails

An email backend is not configured. Without one, Zeno falls back to logging the token to the console.

**Fix:** Configure an email backend:

```python
from zork.email import SMTPBackend

app.email.use(SMTPBackend.sendgrid(api_key="..."))
app.email.configure(
    from_address="no-reply@myapp.com",
    base_url="https://myapp.com",
)
```

See [Email Providers](/email/providers/) for all options.

---

## 403 "Account is disabled"

The user's `is_active` column is `0`.

**Fix:** Update the user in the database:

```sql
UPDATE _users SET is_active = 1 WHERE email = 'user@example.com';
```

---

## Token claims look wrong (role, user ID)

The token encodes the role at login time. If you promote a user after they logged in, they need to log in again to get a token with the updated role.
