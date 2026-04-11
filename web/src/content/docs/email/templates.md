---
title: Email Templates
description: Customise the built-in transactional email templates
sidebar:
  order: 3
---

Cinder includes built-in HTML and plain-text templates for three system emails. You can override each one with a custom function.

## Built-in templates

| Template | Sent when |
|----------|-----------|
| Verification | User registers (if email backend is configured) |
| Password reset | `POST /api/auth/forgot-password` is called |
| Welcome | After registration (disabled by default — override to enable) |

## Overriding a template

Pass a callable to the appropriate method on `app.email`. The callable receives a context dict and must return a `(subject, html_body, text_body)` tuple.

### Password reset

```python
def my_reset_email(ctx):
    url = ctx["reset_url"]
    app_name = ctx["app_name"]
    expiry = ctx["expiry_minutes"]
    return (
        f"Reset your {app_name} password",
        f"""
        <h1>Password Reset</h1>
        <p>Click the link below to reset your password. It expires in {expiry} minutes.</p>
        <p><a href="{url}">Reset Password</a></p>
        """,
        f"Reset your password: {url}\n\nThis link expires in {expiry} minutes.",
    )

app.email.on_password_reset(my_reset_email)
```

Context keys: `reset_url`, `app_name`, `expiry_minutes`

### Email verification

```python
def my_verify_email(ctx):
    url = ctx["verify_url"]
    app_name = ctx["app_name"]
    return (
        f"Verify your {app_name} email",
        f'<p>Click to verify: <a href="{url}">Verify Email</a></p>',
        f"Verify your email: {url}",
    )

app.email.on_verification(my_verify_email)
```

Context keys: `verify_url`, `app_name`

### Welcome email

```python
def my_welcome_email(ctx):
    email = ctx["user_email"]
    app_name = ctx["app_name"]
    return (
        f"Welcome to {app_name}!",
        f"<h1>Welcome, {email}!</h1><p>Thanks for joining.</p>",
        f"Welcome to {app_name}, {email}! Thanks for joining.",
    )

app.email.on_welcome(my_welcome_email)
```

Context keys: `user_email`, `app_name`

Note: The welcome email is not sent automatically. Override and then call it from an auth hook if you want to send it:

```python
@auth.on("after_register")
async def send_welcome(user, ctx):
    # Welcome email will be triggered via the template system
    pass
```

## Using a template engine

You can use any template engine (Jinja2, etc.) inside the template function:

```python
from jinja2 import Template

reset_template = Template("""
<html>
<body>
  <h1>Reset your password</h1>
  <p><a href="{{ reset_url }}">Click here</a> — expires in {{ expiry_minutes }} minutes.</p>
</body>
</html>
""")

def my_reset_email(ctx):
    html = reset_template.render(**ctx)
    return (
        "Reset your password",
        html,
        f"Reset link: {ctx['reset_url']}",
    )

app.email.on_password_reset(my_reset_email)
```
