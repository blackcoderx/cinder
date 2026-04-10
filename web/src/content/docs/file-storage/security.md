---
title: Security
description: File upload security features and best practices
---

Cinder enforces several protections on every file upload.

## MIME Type Validation

Cinder checks both the `Content-Type` header and the file's magic bytes (first 512 bytes):

```python
FileField("avatar", allowed_types=["image/*"])
```

If a file claims to be `image/jpeg` but contains a PDF binary, it's rejected with `422`.

## Size Enforcement

Streaming read with a byte counter. The connection is aborted mid-stream if `max_size` is exceeded:

```python
FileField("attachment", max_size=5_000_000)  # 5 MB limit
```

Returns `413 Payload Too Large` if exceeded.

## Path Traversal Prevention

Storage keys are always formatted as:

```
{collection}/{id}/{field}/{uuid}_{sanitized_name}
```

The user-supplied filename is sanitized (alphanumeric, `-`, `_`, `.` only) and prefixed with a UUID. User input never controls the storage path directly.

## Authentication Gating

- **Upload** — always requires write permission
- **Delete** — always requires write permission
- **Download** — requires read permission, unless `FileField(public=True)` is set

## Signed URL Expiry

Presigned download URLs expire after 15 minutes by default (configurable via `signed_url_expires`):

```python
S3CompatibleBackend(
    bucket="my-bucket",
    signed_url_expires=1800,  # 30 minutes
)
```

The URL is generated fresh per request and never stored.

## Best Practices

### Use Allowed Types

```python
# Images only
FileField("photos", multiple=True, allowed_types=["image/*"])

# Documents only
FileField("documents", allowed_types=["application/pdf", "application/msword"])
```

### Set Size Limits

```python
# Profile photos - small
FileField("avatar", max_size=1_000_000)  # 1 MB

# Large files - be generous but bounded
FileField("video", max_size=100_000_000)  # 100 MB
```

### Use Public for Static Assets

```python
# Profile pictures - public read
FileField("avatar", public=True)

# Private documents - authenticated read
FileField("contract", public=False)
```

## Next Steps

- [Setup](/file-storage/setup/) — FileField basics
- [Backends](/file-storage/backends/) — Storage configuration