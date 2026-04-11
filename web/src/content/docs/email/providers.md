---
title: Providers
description: SMTP backend presets for popular email services
sidebar:
  order: 2
---

`SMTPBackend` provides preset factory methods for the most popular email delivery services. All use SMTP under the hood via [aiosmtplib](https://github.com/cole/aiosmtplib).

Install the email extra:

```bash
pip install "cinder[email]"
uv add "cinder[email]"
```

---

## SendGrid

```python
from cinder.email import SMTPBackend

app.email.use(SMTPBackend.sendgrid(api_key="SG.xxx"))
```

---

## Mailgun

```python
app.email.use(SMTPBackend.mailgun(
    domain="mg.myapp.com",
    api_key="key-xxx",
))
```

---

## Postmark

```python
app.email.use(SMTPBackend.postmark(server_token="xxx"))
```

---

## Amazon SES

```python
app.email.use(SMTPBackend.ses(
    username="AKIA...",
    password="xxx",
    region="us-east-1",
))
```

---

## Resend

```python
app.email.use(SMTPBackend.resend(api_key="re_xxx"))
```

---

## Mailtrap (testing)

```python
app.email.use(SMTPBackend.mailtrap(
    username="your-username",
    password="your-password",
))
```

---

## Gmail

Not recommended for production (rate limits, less reliable), but useful for personal projects:

```python
app.email.use(SMTPBackend.gmail(
    username="you@gmail.com",
    password="your-app-password",  # use an App Password, not your account password
))
```

---

## Custom SMTP server

```python
from cinder.email import SMTPBackend

app.email.use(SMTPBackend(
    host="smtp.myserver.com",
    port=587,
    username="user",
    password="pass",
    use_tls=True,
))
```

---

## ConsoleEmailBackend (development)

Prints emails to stdout instead of sending them. This is the default when no backend is configured:

```python
from cinder.email.backends import ConsoleEmailBackend

app.email.use(ConsoleEmailBackend())
```
