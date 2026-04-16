# File Storage Setup

Zork provides a flexible file storage system for handling file uploads. This guide explains how to configure and use file storage.

## Overview

File storage in Zork works in two parts:

1. **FileField** in your collection stores metadata about uploaded files
2. **Storage backend** handles the actual file bytes

This separation allows you to switch storage providers without changing your data schema.

## Adding FileFields

Add a FileField to your collection:

```python
from zork import Collection, TextField, FileField

posts = Collection("posts", fields=[
    TextField("title", required=True),
    TextField("body"),
    FileField("cover_image"),
])
```

Now file upload endpoints are automatically created for this field.

## Configuring Storage Backend

Configure storage in your app:

### Local File Storage (Development)

Store files on the local filesystem:

```python
from zork import Zork
from zork.storage import LocalFileBackend

app = Zork()
app.configure_storage(LocalFileBackend("./uploads"))
```

Files are stored in the `./uploads/` directory.

### Cloud Storage (Production)

For production, use S3-compatible storage:

```python
from zork import Zork
from zork.storage import S3CompatibleBackend

app = Zork()
app.configure_storage(S3CompatibleBackend.aws(
    bucket="my-app-uploads",
    access_key="YOUR_ACCESS_KEY",
    secret_key="YOUR_SECRET_KEY",
    region="us-east-1",
))
```

See the [Storage Providers](/file-storage/providers) guide for all cloud provider options.

## File Upload Endpoints

When you add a FileField, Zork creates these endpoints:

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/{collection}/{id}/files/{field}` | Upload file(s) |
| GET | `/api/{collection}/{id}/files/{field}` | Download file(s) |
| DELETE | `/api/{collection}/{id}/files/{field}` | Delete file(s) |

## Uploading Files

### Single File Upload

```bash
curl -X POST http://localhost:8000/api/posts/POST_ID/files/cover_image \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@image.jpg"
```

### Multiple Files

For fields with `multiple=True`:

```bash
curl -X POST http://localhost:8000/api/posts/POST_ID/files/attachments \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "files=@doc1.pdf" \
  -F "files=@doc2.pdf"
```

### Response

```json
{
  "id": "file-uuid",
  "name": "image.jpg",
  "size": 102400,
  "mime": "image/jpeg"
}
```

## Downloading Files

### Download a file

```bash
curl -O http://localhost:8000/api/posts/POST_ID/files/cover_image \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### With query parameters

```bash
# Download a specific file from a multiple field
curl "http://localhost:8000/api/posts/POST_ID/files/attachments?index=0"
```

## Deleting Files

### Delete all files in a field

```bash
curl -X DELETE http://localhost:8000/api/posts/POST_ID/files/cover_image \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Delete specific file from multiple field

```bash
curl -X DELETE "http://localhost:8000/api/posts/POST_ID/files/attachments?index=0" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## FileField Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `max_size` | int | 10_000_000 | Maximum file size in bytes |
| `allowed_types` | list | `["*/*"]` | MIME types to accept |
| `multiple` | bool | `False` | Allow multiple files |
| `public` | bool | `False` | No auth required for download |

### Restricting File Types

```python
# Only images
FileField("avatar", allowed_types=["image/*"])

# Specific types
FileField("document", allowed_types=["application/pdf", "application/msword"])

# Size limit
FileField("video", max_size=100_000_000)  # 100 MB
```

### Public Files

Files marked as public can be downloaded without authentication:

```python
FileField("cover_image", public=True)
```

## Automatic Cleanup

When a record is deleted, Zork automatically deletes associated files:

```python
# When a post is deleted, its files are also deleted
posts = Collection("posts", fields=[
    TextField("title"),
    FileField("cover_image"),  # Deleted automatically
])
```

## Storing File Metadata

FileField stores metadata in your database:

```json
{
  "id": "file-uuid",
  "name": "image.jpg",
  "size": 102400,
  "mime": "image/jpeg",
  "key": "posts/POST_ID/cover_image/uuid_image.jpg"
}
```

## Custom Storage Backends

Create a custom storage backend by implementing the FileStorageBackend interface:

```python
from zork.storage import FileStorageBackend

class CustomStorage(FileStorageBackend):
    async def put(self, key, data, content_type):
        # Save file
        pass
    
    async def get(self, key):
        # Read file
        pass
    
    async def delete(self, key):
        # Remove file
        pass
```

Then configure it:

```python
app.configure_storage(CustomStorage())
```

## Next Steps

- [Storage Providers](/file-storage/providers) — AWS, R2, MinIO, and more
- [FileField](/core-concepts/fields) — Field reference
