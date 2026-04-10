---
title: Templates
description: Customize email templates for password reset, verification, and more
---

Cinder ships with built-in email templates. Override any of them with your own callable.

## Built-in Templates

Cinder provides three built-in templates:

1. **Password Reset** — Sent when user requests password reset
2. **Email Verification** — Sent on registration
3. **Welcome Email** — Sent manually from hooks

All templates are inline-styled HTML with plain-text alternatives.

## Override a Template

Override any template with a callable that returns `(subject, html_body, text_body)`:

### Plain Function Override

```python
def my_reset_template(ctx):
    url = ctx["reset_url"]
    return (
        "Reset your password",
        f"<h1>Reset link</h1><a href='{url}'>Click here</a>",
        f"Reset link: {url}",
    )

app.email.on_password_reset(my_reset_template)
```

### Jinja2 Override

Install Jinja2 separately:

```bash
pip install jinja2
```

```python
from jinja2 import Environment, FileSystemLoader

jinja = Environment(loader=FileSystemLoader("templates/email"))

def jinja_reset(ctx):
    html = jinja.get_template("reset.html").render(**ctx)
    text = jinja.get_template("reset.txt").render(**ctx)
    return "Reset your password", html, text

app.email.on_password_reset(jinja_reset)
```

## Template Context Keys

| Override Method | Context Keys |
|-----------------|---------------|
| `app.email.on_password_reset(fn)` | `reset_url`, `app_name`, `expiry_minutes` |
| `app.email.on_verification(fn)` | `verify_url`, `app_name` |
| `app.email.on_welcome(fn)` | `user_email`, `app_name` |

## Full Example

```python
from cinder import Cinder, Auth

app = Cinder(database="app.db")
auth = Auth()
app.use_auth(auth)

# Configure email
from cinder.email import SMTPBackend

app.email.use(SMTPBackend.sendgrid(api_key=os.getenv("SENDGRID_API_KEY")))
app.email.configure(
    from_address="no-reply@myapp.com",
    app_name="MyApp",
    base_url="https://myapp.com",
)

# Custom templates
def custom_welcome(ctx):
    return (
        f"Welcome to {ctx['app_name']}!",
        f"<h1>Welcome!</h1><p>Thanks for joining {ctx['app_name']}.</p>",
        f"Welcome! Thanks for joining {ctx['app_name']}.",
    )

app.email.on_welcome(custom_welcome)

app.serve()
```

## Sending Welcome Email from Hook

```python
@app.on("auth:after_register")
async def send_welcome(user, ctx):
    await app.email.send(EmailMessage(
        to=user["email"],
        subject="Welcome!",
        html_body="<h1>Welcome!</h1>",
        text_body="Welcome!",
    ))
```

## Next Steps

- [Setup](/email/setup/) — Configure email
- [Providers](/email/providers/) — SMTP configuration