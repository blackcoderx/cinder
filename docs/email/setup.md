# Email Setup

Zork provides email delivery capabilities for transactional emails like password resets and verification emails.

## Quick Setup

Configure email with minimal settings:

```python
from zork import Zork
from zork.email import SMTPBackend

app = Zork()
app.email.use(SMTPBackend(
    hostname="smtp.example.com",
    port=587,
    username="your-username",
    password="your-password",
))
app.email.configure(
    from_address="noreply@example.com",
    app_name="My App",
    base_url="https://myapp.com",
)
```

## Provider Presets

Zork includes presets for popular email providers:

### Gmail

```python
from zork.email import SMTPBackend

app.email.use(SMTPBackend.gmail(
    username="you@gmail.com",
    app_password="xxxx xxxx xxxx xxxx",  # App password, not regular password
))
```

You need to generate an App Password in your Google Account security settings.

### SendGrid

```python
from zork.email import SMTPBackend

app.email.use(SMTPBackend.sendgrid(
    api_key="SG.your-api-key",
))
```

### Amazon SES

```python
from zork.email import SMTPBackend

app.email.use(SMTPBackend.ses(
    region="us-east-1",
    key_id="your-smtp-username",
    secret="your-smtp-password",
))
```

Generate SMTP credentials in the SES console.

### Mailgun

```python
from zork.email import SMTPBackend

app.email.use(SMTPBackend.mailgun(
    username="postmaster@mg.example.com",
    password="your-smtp-password",
))
```

### Mailtrap (Development)

For testing without sending real emails:

```python
from zork.email import SMTPBackend

app.email.use(SMTPBackend.mailtrap(
    api_token="your-mailtrap-token",
))
```

### Postmark

```python
from zork.email import SMTPBackend

app.email.use(SMTPBackend.postmark(
    api_token="your-server-token",
))
```

### Resend

```python
from zork.email import SMTPBackend

app.email.use(SMTPBackend.resend(
    api_key="re_your-api-key",
))
```

## Configuration Options

### app.email.use()

Set the email backend:

```python
app.email.use(SMTPBackend(...))
```

### app.email.configure()

Set email defaults:

```python
app.email.configure(
    from_address="noreply@example.com",  # Sender email
    app_name="My App",                   # App name for emails
    base_url="https://myapp.com",        # For generating links
)
```

## Email Templates

Zork includes built-in templates for common emails:

### Password Reset Email

Sent when a user requests a password reset.

### Email Verification

Sent when a new user registers (if email verification is enabled).

### Welcome Email

Sent after successful registration.

## Custom Templates

Override the default templates:

```python
def my_password_reset_template(ctx):
    return (
        "Reset your password",
        f"<h1>Reset Password</h1><p>Click <a href='{ctx['reset_url']}'>here</a> to reset.</p>",
        f"Reset your password here: {ctx['reset_url']}"
    )

app.email.on_password_reset(my_password_reset_template)
```

### Template Context

Each template receives a context dictionary:

| Template | Context Keys |
|---------|--------------|
| Password Reset | `reset_url`, `app_name`, `expiry_minutes` |
| Email Verification | `verify_url`, `app_name` |
| Welcome | `user_email`, `app_name` |

## Development Mode

When no email backend is configured, emails are logged to the console:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 EMAIL (console — configure app.email.use(...))
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 From:    noreply@example.com
 To:      user@example.com
 Subject: Reset your password
────────────────────────────────────────
 Click the link to reset: https://myapp.com/reset?token=abc

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

This lets you test email flows without setting up SMTP.

## Custom SMTP Settings

For providers not in the presets:

```python
from zork.email import SMTPBackend

app.email.use(SMTPBackend(
    hostname="smtp.example.com",
    port=587,              # 587 for STARTTLS, 465 for implicit TLS
    username="username",
    password="password",
    start_tls=True,        # Use STARTTLS
    timeout=30,            # Connection timeout
    max_retries=3,         # Retry failed sends
))
```

## Sending Custom Emails

Send emails from hooks or custom code:

```python
from zork.email import EmailMessage

@app.on("orders:after_create")
async def send_order_confirmation(order, ctx):
    await app.email.send(EmailMessage(
        to=order["email"],
        subject=f"Order Confirmed - #{order['id']}",
        html_body=f"<h1>Thank you!</h1><p>Your order is confirmed.</p>",
        text_body="Thank you! Your order is confirmed.",
    ))
```

## Next Steps

- [Authentication](/authentication/setup) — Email verification in auth
- [Lifecycle Hooks](/core-concepts/lifecycle-hooks) — Triggering emails from hooks
