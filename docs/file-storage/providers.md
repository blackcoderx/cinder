# Storage Providers

Zork supports multiple storage providers through S3-compatible backends. This guide covers all available providers.

## Installation

Cloud storage requires the S3 extra:

```bash
pip install "zork[s3]"
```

## AWS S3

Store files in Amazon Web Services S3:

```python
from zork.storage import S3CompatibleBackend

app.configure_storage(S3CompatibleBackend.aws(
    bucket="my-app-bucket",
    access_key="AKIAIOSFODNN7EXAMPLE",
    secret_key="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
    region="us-east-1",
))
```

## Cloudflare R2

R2 provides S3-compatible object storage without egress fees:

```python
from zork.storage import S3CompatibleBackend

app.configure_storage(S3CompatibleBackend.r2(
    account_id="your-account-id",
    bucket="my-bucket",
    access_key="your-access-key",
    secret_key="your-secret-key",
))
```

Get your account ID from the Cloudflare dashboard.

## MinIO

For self-hosted S3-compatible storage:

```python
from zork.storage import S3CompatibleBackend

app.configure_storage(S3CompatibleBackend.minio(
    endpoint="http://localhost:9000",
    bucket="my-bucket",
    access_key="minioadmin",
    secret_key="minioadmin",
))
```

MinIO is great for local development and private deployments.

## Backblaze B2

Backblaze B2 offers affordable cloud storage:

```python
from zork.storage import S3CompatibleBackend

app.configure_storage(S3CompatibleBackend.backblaze(
    endpoint="https://s3.us-west-001.backblazeb2.com",
    bucket="my-bucket",
    key_id="your-key-id",
    app_key="your-app-key",
))
```

## DigitalOcean Spaces

DigitalOcean's S3-compatible object storage:

```python
from zork.storage import S3CompatibleBackend

app.configure_storage(S3CompatibleBackend.digitalocean(
    region="nyc3",
    space="my-space",
    access_key="DOXXX",
    secret_key="your-secret-key",
))
```

## Wasabi

Wasabi provides hot cloud storage:

```python
from zork.storage import S3CompatibleBackend

app.configure_storage(S3CompatibleBackend.wasabi(
    region="us-east-1",
    bucket="my-bucket",
    access_key="your-access-key",
    secret_key="your-secret-key",
))
```

## Google Cloud Storage

GCS via S3-compatible interoperability:

```python
from zork.storage import S3CompatibleBackend

app.configure_storage(S3CompatibleBackend.gcs(
    bucket="my-bucket",
    access_key="GOOG...",
    secret_key="...",
))
```

Note: GCS requires HMAC credentials, not a service account JSON key. Generate them in Cloud Console → Storage → Settings → Interoperability.

## Custom Configuration

For providers not in the presets:

```python
from zork.storage import S3CompatibleBackend

app.configure_storage(S3CompatibleBackend(
    bucket="my-bucket",
    access_key="your-access-key",
    secret_key="your-secret-key",
    endpoint_url="https://custom-provider.example.com",
    region_name="custom-region",
))
```

## Provider Comparison

| Provider | Preset Method | Best For |
|---------|---------------|----------|
| AWS S3 | `aws()` | General purpose cloud storage |
| Cloudflare R2 | `r2()` | Low-cost, no egress fees |
| MinIO | `minio()` | Self-hosted, local dev |
| Backblaze B2 | `backblaze()` | Affordable long-term storage |
| DigitalOcean | `digitalocean()` | DO infrastructure users |
| Wasabi | `wasabi()` | Hot storage with good pricing |
| GCS | `gcs()` | GCP infrastructure users |

## Environment-Based Configuration

Switch providers based on environment:

```python
import os
from zork.storage import LocalFileBackend, S3CompatibleBackend

if os.getenv("ENV") == "production":
    app.configure_storage(S3CompatibleBackend.r2(
        account_id=os.getenv("R2_ACCOUNT_ID"),
        bucket=os.getenv("R2_BUCKET"),
        access_key=os.getenv("R2_ACCESS_KEY"),
        secret_key=os.getenv("R2_SECRET_KEY"),
    ))
else:
    app.configure_storage(LocalFileBackend("./uploads"))
```

## Security Best Practices

### Access Keys

- Never commit access keys to version control
- Use environment variables or secrets management
- Rotate keys periodically
- Use minimal required permissions

### Bucket Policies

Configure your bucket for:

- Private access by default
- Signed URLs for authenticated downloads
- Appropriate CORS settings if using in-browser uploads

### Example S3 Bucket Policy

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:*",
      "Resource": "arn:aws:s3:::my-bucket/*",
      "Condition": {
        "Bool": {
          "aws:SecureTransport": "false"
        }
      }
    }
  ]
}
```

This denies non-HTTPS access to the bucket.

## Uploading with Presigned URLs

For large files, generate presigned URLs on your server and let clients upload directly:

```python
@app.on("posts:before_create")
async def generate_upload_url(data, ctx):
    if "cover_image" in data:
        key = f"posts/{data['id']}/cover_image"
        url = await app.storage.signed_url(key, expires_in=3600)
        data["upload_url"] = url
    return data
```

Note: This requires custom implementation beyond Zork's built-in file handling.

## Next Steps

- [File Storage Setup](/file-storage/setup) — Basic file storage configuration
