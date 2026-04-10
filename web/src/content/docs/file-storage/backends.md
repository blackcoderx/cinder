---
title: Backends
description: Configure file storage backends - local disk, S3-compatible, or custom
---

Cinder supports multiple storage backends. Switch backends by changing one line.

## LocalFileBackend

Zero configuration. Files are stored on disk.

```python
from cinder.storage import LocalFileBackend

app.configure_storage(LocalFileBackend("./uploads"))
```

Files are always served by proxying bytes through the Cinder server.

## S3CompatibleBackend

Supports any S3-compatible object store via boto3.

### AWS S3

```python
from cinder.storage import S3CompatibleBackend

app.configure_storage(S3CompatibleBackend.aws(
    bucket="my-bucket",
    access_key="AKIAIOSFODNN7EXAMPLE",
    secret_key="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
    region="us-east-1",
))
```

### Cloudflare R2

```python
app.configure_storage(S3CompatibleBackend.r2(
    account_id="your-cloudflare-account-id",
    bucket="my-bucket",
    access_key="your-r2-access-key",
    secret_key="your-r2-secret-key",
))
```

### MinIO

```python
app.configure_storage(S3CompatibleBackend.minio(
    endpoint="http://localhost:9000",
    bucket="my-bucket",
    access_key="minioadmin",
    secret_key="minioadmin",
))
```

### Backblaze B2

```python
app.configure_storage(S3CompatibleBackend.backblaze(
    endpoint="https://s3.us-west-001.backblazeb2.com",
    bucket="my-bucket",
    key_id="your-key-id",
    app_key="your-app-key",
))
```

### DigitalOcean Spaces

```python
app.configure_storage(S3CompatibleBackend.digitalocean(
    region="nyc3",
    space="my-space",
    access_key="your-access-key",
    secret_key="your-secret-key",
))
```

### Wasabi

```python
app.configure_storage(S3CompatibleBackend.wasabi(
    region="us-east-1",
    bucket="my-bucket",
    access_key="your-access-key",
    secret_key="your-secret-key",
))
```

### Google Cloud Storage (S3 interop)

```python
app.configure_storage(S3CompatibleBackend.gcs(
    bucket="my-bucket",
    access_key="your-hmac-access-key",
    secret_key="your-hmac-secret",
))
```

## Custom Endpoint

Use the constructor directly for custom providers:

```python
app.configure_storage(S3CompatibleBackend(
    bucket="my-bucket",
    access_key="key",
    secret_key="secret",
    endpoint_url="https://my-custom-provider.example.com",
    region_name="us-east-1",
    key_prefix="myapp",
    signed_url_expires=1800,
))
```

## Custom Backend

Subclass `FileStorageBackend` to integrate any storage system:

```python
from cinder.storage import FileStorageBackend

class MyStorageBackend(FileStorageBackend):
    async def put(self, key: str, data: bytes, content_type: str) -> None:
        # Store the file
        ...

    async def get(self, key: str) -> tuple[bytes, str]:
        # Return (data, content_type). Raise FileNotFoundError if missing.
        ...

    async def delete(self, key: str) -> None:
        # Delete the file. No-op if it doesn't exist.
        ...

    async def signed_url(self, key: str, expires_in: int = 900) -> str | None:
        # Return a presigned URL, or None to fall back to proxy mode.
        ...

    async def url(self, key: str) -> str | None:
        # Return a permanent public URL for public=True fields.
        ...

app.configure_storage(MyStorageBackend())
```

## Next Steps

- [Security](/file-storage/security/) — Upload validation
- [Setup](/file-storage/setup/) — FileField configuration