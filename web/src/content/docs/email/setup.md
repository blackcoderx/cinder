---
title: Setup
description: Configure transactional email delivery
sidebar:
  order: 1
---

Zeno can send transactional emails for account verification, password reset, and welcome messages. Configure a backend to activate email sending.

## Without a backend (development)

Without configuration, Zeno uses `ConsoleEmailBackend`, which prints emails to the console instead of sending them. Useful for development.

```python
app = Zeno(database="app.db")
# No email configuration needed — emails print to stdout
```

## With a backend

```python
from zork.email import SMTPBackend

app.email.use(SMTPBackend.sendgrid(api_key="SG.xxx"))
app.email.configure(
    from_address="no-reply@myapp.com",
    app_name="MyApp",
    base_url="https://myapp.com",
)
```

### `.use(backend)`

Set the email backend. Must be called before `app.build()`.

### `.configure(from_address, app_name, base_url)`

| Option | Default | Description |
|--------|---------|-------------|
| `from_address` | `ZENO_EMAIL_FROM` or `"noreply@localhost"` | Sender address on all emails |
| `app_name` | `ZENO_APP_NAME` or `"Your App"` | App name used in email templates |
| `base_url` | `ZENO_BASE_URL` or `"http://localhost:8000"` | Base URL for links in emails (verify, reset) |

Also configurable via environment variables:

```dotenv
ZENO_EMAIL_FROM=no-reply@myapp.com
ZENO_APP_NAME=MyApp
ZENO_BASE_URL=https://myapp.com
```

## Sending custom emails from hooks

```python
from zork.email import EmailMessage

@orders.on("after_create")
async def send_confirmation(order, ctx):
    await app.email.send(EmailMessage(
        to=order["customer_email"],
        subject="Order Confirmed",
        html_body=f"<p>Your order #{order['id']} has been confirmed.</p>",
        text_body=f"Your order #{order['id']} has been confirmed.",
    ))
```

`app.email.send()` is non-blocking — it dispatches the email as a background task and returns immediately.

## See also

- [Email Providers](/email/providers/) — all SMTP backend presets
- [Email Templates](/email/templates/) — customise the built-in templates
