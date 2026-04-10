---
title: Setup
description: Configure email delivery for your Cinder app
---

Cinder has a built-in email delivery layer that powers password-reset links and email verification.

## Install the Email Extra

```bash
pip install cinder[email]
# or
uv add cinder[email]
```

## Zero-Config (Console Fallback)

No configuration is needed in development. Cinder falls back to `ConsoleEmailBackend` automatically when no backend is configured:

```python
app = Cinder("app.db")
app.use_auth(Auth())   # email verification + password-reset emails → console log
```

All outbound emails are printed to the server log so you can inspect links and content.

## Connecting an SMTP Provider

Use `app.email.use(backend)` to plug in a real delivery backend:

```python
from cinder.email import SMTPBackend

app.email.use(SMTPBackend.sendgrid(api_key=os.getenv("SENDGRID_API_KEY")))
app.email.configure(
    from_address="no-reply@myapp.com",
    app_name="MyApp",
    base_url="https://myapp.com",
)
```

## Environment Variables

These can be set in your `.env` file:

```sh
CINDER_EMAIL_FROM=no-reply@myapp.com
CINDER_APP_NAME=MyApp
CINDER_BASE_URL=https://myapp.com
```

Or configured programmatically:

```python
app.email.configure(
    from_address="no-reply@myapp.com",
    app_name="MyApp",
    base_url="https://myapp.com",
)
```

## Sending Custom Emails

`app.email.send()` can be called from hooks or anywhere in your code:

```python
from cinder.email import EmailMessage

@app.on("orders:after_create")
async def send_order_confirmation(order, ctx):
    await app.email.send(EmailMessage(
        to=order["customer_email"],
        subject=f"Order #{order['id']} confirmed",
        html_body=f"<p>Your order <b>#{order['id']}</b> is confirmed.</p>",
        text_body=f"Your order #{order['id']} is confirmed.",
    ))
```

All emails are dispatched via `asyncio.create_task` — they never block the HTTP response.

## Next Steps

- [Providers](/email/providers/) — SMTP provider presets
- [Templates](/email/templates/) — Custom email templates