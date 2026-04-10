---
title: Authentication
description: Complete authentication system for Cinder apps
---

Cinder provides a full-featured authentication system out of the box. No third-party libraries needed.

## Features

| Feature | Description |
|---------|-------------|
| User registration & login | Email/password authentication |
| JWT tokens | Stateless, self-contained tokens |
| Token refresh | Rotate tokens without re-login |
| Token revocation | Logout invalidates tokens immediately |
| Email verification | Verify user emails with one-click links |
| Password reset | Secure reset flow via email |
| Role-based access | User/admin roles for permissions |
| Extendable user model | Add custom fields to users |

## Quick Setup

```python
from cinder import Cinder, Auth

app = Cinder(database="app.db")
auth = Auth()
app.use_auth(auth)
app.serve()
```

This gives you registration, login, logout, token refresh, password reset, and email verification — no additional configuration required.

## What's Included

### Auth Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/register` | POST | Create a new user |
| `/api/auth/login` | POST | Authenticate and get token |
| `/api/auth/me` | GET | Get current user info |
| `/api/auth/logout` | POST | Revoke current token |
| `/api/auth/refresh` | POST | Get a new token |
| `/api/auth/forgot-password` | POST | Request password reset |
| `/api/auth/reset-password` | POST | Complete password reset |
| `/api/auth/verify-email` | GET | Verify email address |

### Auth Hooks

Trigger custom logic on auth events:

```python
@app.on("auth:after_register")
async def welcome_email(user, ctx):
    await app.email.send(EmailMessage(...))
```

See [Auth Hooks](/authentication/hooks/) for all available events.

## Sections

- [Setup](/authentication/setup/) — Configure auth for your app
- [User Model](/authentication/user-model/) — Extend the user schema
- [Endpoints](/authentication/endpoints/) — API reference
- [Hooks](/authentication/hooks/) — React to auth events
- [Security](/authentication/security/) — How auth protects your users
- [Troubleshooting](/authentication/troubleshooting/) — Common issues and solutions

## Related

- [Access Control](/core-concepts/access-control/) — Use auth with collections
- [Hooks](/core-concepts/lifecycle-hooks/) — Hook system for all events
- [Email](/email/setup/) — Configure email for verification and password reset
