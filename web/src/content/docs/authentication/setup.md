---
title: Setup
description: Configure authentication for your Cinder app
---

## Basic Setup

```python
from cinder import Cinder, Auth

app = Cinder(database="app.db")
auth = Auth()
app.use_auth(auth)
```

That's it. Cinder creates all necessary tables and endpoints automatically.

## Secret Key

Tokens are signed with a secret key. Set `CINDER_SECRET` for production:

```bash
# Generate a secret
cinder generate-secret

# Set as environment variable
export CINDER_SECRET="your-generated-secret"
```

Without this, Cinder generates a random secret on startup. Tokens won't persist across restarts.

## Configuration Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `token_expiry` | `int` | `86400` | JWT lifetime in seconds (24 hours) |
| `allow_registration` | `bool` | `True` | Enable/disable public registration |
| `extend_user` | `list[Field]` | `None` | Custom fields for user model |

```python
auth = Auth(
    token_expiry=86400 * 7,    # 7 days
    allow_registration=True,
    extend_user=[
        TextField("display_name"),
        TextField("avatar_url"),
    ],
)
```

## Auth Tables

When auth is configured, Cinder creates these tables:

| Table | Purpose |
|-------|---------|
| `_users` | User accounts |
| `_token_blocklist` | Revoked tokens |
| `_password_resets` | Password reset tokens |
| `_email_verifications` | Email verification tokens |

Tables are created automatically on `app.build()`.

## Auth Middleware

The auth middleware runs on every request to decode tokens:

```
Request → Auth Middleware → Routes

Auth Middleware:
1. Looks for Authorization header
2. Decodes JWT if present
3. Sets request.state.user to the user dict
4. Leaves request.state.user as None for no/invalid token
```

Access the user in hooks or custom code:

```python
@posts.on("before_read")
async def hook(data, ctx):
    if ctx.user:
        print(f"Request from user: {ctx.user['email']}")
    return data
```

## Using with Collections

Protect collections with auth rules:

```python
app = Cinder(database="app.db")
auth = Auth()

posts = Collection("posts", fields=[
    TextField("title", required=True),
    TextField("body"),
])

# Public read, authenticated write
app.register(posts, auth=["read:public", "write:authenticated"])

app.use_auth(auth)
```

See [Access Control](/core-concepts/access-control/) for all rule options.

## Auth Hooks

Auth fires hooks at each step of authentication flows:

```python
@auth.on("auth:after_register")
async def welcome(user, ctx):
    await app.email.send(EmailMessage(
        to=user["email"],
        subject="Welcome!",
        html_body="<h1>Thanks for signing up!</h1>"
    ))
```

See [Auth Hooks](/authentication/hooks/) for all available events.

## Complete Example

```python
from cinder import Cinder, Auth, Collection, TextField
from cinder.email import SMTPBackend, EmailMessage

app = Cinder(database="app.db")

# Define your collections
posts = Collection("posts", fields=[
    TextField("title", required=True),
    TextField("content"),
])
app.register(posts, auth=["read:public", "write:authenticated"])

# Configure auth
auth = Auth(
    token_expiry=86400,
    allow_registration=True,
    extend_user=[TextField("display_name")],
)
app.use_auth(auth)

# Configure email (for verification/reset)
app.email.use(SMTPBackend.sendgrid(api_key="..."))
app.email.configure(
    from_address="noreply@example.com",
    app_name="My App",
    base_url="https://api.example.com",
)

# Add auth hooks
@app.on("auth:after_register")
async def send_welcome(user, ctx):
    await app.email.send(EmailMessage(
        to=user["email"],
        subject="Welcome to My App!",
        html_body="<h1>Welcome!</h1>"
    ))

# Start the server
app.serve()
```

## Next Steps

- [User Model](/authentication/user-model/) — Extend with custom fields
- [Endpoints](/authentication/endpoints/) — Auth API reference
- [Hooks](/authentication/hooks/) — React to auth events
- [Security](/authentication/security/) — How auth protects your users
- [Email](/email/setup/) — Configure for verification/reset
