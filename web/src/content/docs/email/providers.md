---
title: Providers
description: Configure email delivery with SMTP providers
---

Cinder supports various SMTP providers with preset configurations.

## Provider Presets

| Preset | Host | Port | TLS Mode |
|--------|------|------|----------|
| `SMTPBackend.gmail(username, app_password)` | smtp.gmail.com | 587 | STARTTLS |
| `SMTPBackend.sendgrid(api_key)` | smtp.sendgrid.net | 587 | STARTTLS |
| `SMTPBackend.ses(region, key_id, secret)` | email-smtp.{region}.amazonaws.com | 587 | STARTTLS |
| `SMTPBackend.mailgun(username, password, eu=False)` | smtp.mailgun.org | 587 | STARTTLS |
| `SMTPBackend.mailtrap(api_token)` | live.smtp.mailtrap.io | 587 | STARTTLS |
| `SMTPBackend.postmark(api_token)` | smtp.postmarkapp.com | 587 | STARTTLS |
| `SMTPBackend.resend(api_key)` | smtp.resend.com | 465 | Implicit TLS |

## Gmail

Requires an App Password (not your account password):

```python
app.email.use(SMTPBackend.gmail(
    username="me@gmail.com",
    app_password="xxxx xxxx xxxx xxxx",
))
```

## SendGrid

```python
app.email.use(SMTPBackend.sendgrid(api_key=os.getenv("SENDGRID_API_KEY")))
```

## Amazon SES

Use SMTP-specific credentials, not IAM keys:

```python
app.email.use(SMTPBackend.ses(
    region="us-east-1",
    key_id=os.getenv("SES_SMTP_USER"),
    secret=os.getenv("SES_SMTP_PASSWORD"),
))
```

## Mailgun

```python
app.email.use(SMTPBackend.mailgun(
    username="postmaster@mg.myapp.com",
    password=os.getenv("MAILGUN_SMTP_PASSWORD"),
))
```

## Resend

Uses port 465 implicit TLS:

```python
app.email.use(SMTPBackend.resend(api_key=os.getenv("RESEND_API_KEY")))
```

## Custom SMTP Server

```python
from cinder.email import SMTPBackend

app.email.use(SMTPBackend(
    hostname="smtp.myhost.com",
    port=587,
    username="user@myhost.com",
    password="smtp-password",
    start_tls=True,
))
```

## Retry Behavior

`SMTPBackend` retries transient failures:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `max_retries` | `3` | Maximum send attempts |
| `retry_base_delay` | `1.0` | Initial retry delay in seconds (doubles each attempt) |
| `timeout` | `30` | Connection and command timeout in seconds |

Permanent failures (authentication errors, rejected recipients) raise immediately without retrying.

## Next Steps

- [Templates](/email/templates/) — Customize email content
- [Setup](/email/setup/) — Email configuration