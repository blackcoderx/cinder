---
title: Auth Hooks
description: Lifecycle events for authentication operations
---

The `Auth` object fires events at key points in each authentication flow. Register handlers the same way you would for collection hooks.

## Available events

| Event | Fires | Payload | Can modify |
|-------|-------|---------|------------|
| `auth:before_register` | Before user is created | Request body dict | Yes |
| `auth:after_register` | After user is created | User dict (no password) | No |
| `auth:before_login` | Before credentials are checked | Request body dict | Yes |
| `auth:after_login` | After successful login | User dict (no password) | No |
| `auth:before_logout` | Before token is revoked | User dict | No |
| `auth:after_logout` | After token is revoked | User dict | No |
| `auth:after_verify_email` | After email is verified | `{"user_id": ..., "email": ...}` | No |
| `auth:before_password_reset` | Before reset link is generated | Request body dict | Yes |
| `auth:after_password_reset` | After reset link is generated | `{"email": ..., "user_id": ...}` | No |

## Registering auth hooks

Use `auth.on()`:

```python
@auth.on("after_register")
async def welcome_user(user, ctx):
    print(f"New user registered: {user['email']}")
```

Or use the app's shorthand with the full event name:

```python
@app.on("auth:after_register")
async def welcome_user(user, ctx):
    print(f"New user registered: {user['email']}")
```

Both forms are equivalent once `app.use_auth(auth)` is called.

## Modifying registration data

Return a modified payload from `before_register` to change what gets stored:

```python
@auth.on("before_register")
async def normalize_email(body, ctx):
    body["email"] = body["email"].lower().strip()
    return body
```

## Sending a custom welcome email

```python
from zork.email import EmailMessage

@auth.on("after_register")
async def send_welcome(user, ctx):
    await app.email.send(EmailMessage(
        to=user["email"],
        subject="Welcome to MyApp!",
        html_body="<p>Thanks for signing up.</p>",
        text_body="Thanks for signing up.",
    ))
```

## Blocking registration

Raise `ZorkError` from a hook to abort the request:

```python
from zork.errors import ZorkError

@auth.on("before_register")
async def check_domain(body, ctx):
    email = body.get("email", "")
    if not email.endswith("@mycompany.com"):
        raise ZorkError(403, "Only company email addresses are allowed")
    return body
```
