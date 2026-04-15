---
title: Setup
description: Configure and enable authentication in your Zeno app
---

## Basic setup

```python
from zork import Zeno, Auth

app = Zeno(database="app.db")

auth = Auth(
    token_expiry=86400,       # token lifetime in seconds (1 day)
    allow_registration=True,  # allow new users to register
)

app.use_auth(auth)
```

## `Auth` options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `token_expiry` | `int` | `86400` | JWT lifetime in seconds. After this time the token is rejected. |
| `allow_registration` | `bool` | `True` | If `False`, `POST /api/auth/register` returns 403. |
| `extend_user` | `list[Field]` | `[]` | Extra fields to add to the `_users` table. |

## Extending the user model

Add custom fields to the user table:

```python
from zork import Auth, TextField, BoolField

auth = Auth(
    extend_user=[
        TextField("display_name"),
        TextField("avatar_url"),
        BoolField("newsletter_opt_in", default=False),
    ]
)
app.use_auth(auth)
```

These fields are automatically accepted on `POST /api/auth/register` if provided in the request body and stored alongside the standard user fields.

## Setting the secret key

Zeno reads the JWT signing secret from `ZENO_SECRET`. Generate a stable key for production:

```bash
zork generate-secret
```

Add it to your `.env`:

```dotenv
ZENO_SECRET=your-generated-secret-here
```

Without a secret, Zeno generates a random one on startup — which means all tokens are invalidated every time the server restarts.

## Email on registration

If you configure an email backend, Zeno automatically sends a verification email after registration:

```python
from zork.email import SMTPBackend

app.email.use(SMTPBackend.sendgrid(api_key="..."))
app.email.configure(
    from_address="no-reply@myapp.com",
    app_name="MyApp",
    base_url="https://myapp.com",
)
```

See [Email Setup](/email/setup/) for all available backends.

## Disabling registration

Lock registration after launch so only admins can create accounts:

```python
auth = Auth(allow_registration=False)
```

You can still create users programmatically by inserting into `_users` directly or by temporarily re-enabling registration.
