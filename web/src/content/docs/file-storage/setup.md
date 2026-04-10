---
title: Setup
description: Set up file storage with FileField
---

Cinder auto-generates upload, download, and delete endpoints for any collection field defined as `FileField`.

## Install the S3 Extra

For cloud storage, install the S3 extra:

```bash
pip install cinder[s3]
# or
uv add cinder[s3]
```

## Defining a FileField

```python
from cinder import Cinder, Collection, TextField
from cinder.collections.schema import FileField
from cinder.storage import LocalFileBackend

posts = Collection("posts", fields=[
    TextField("title", required=True),
    FileField("cover", max_size=5_000_000, allowed_types=["image/*"], public=True),
    FileField("attachments", multiple=True, allowed_types=["application/pdf"]),
])

app = Cinder("app.db")
app.register(posts, auth=["read:public", "write:authenticated"])
app.configure_storage(LocalFileBackend("./uploads"))
```

## FileField Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `max_size` | `int` | `10_000_000` | Maximum file size in bytes (10 MB) |
| `allowed_types` | `list[str]` | `["*/*"]` | Accepted MIME types (supports wildcards) |
| `multiple` | `bool` | `False` | Allow multiple files per field |
| `public` | `bool` | `False` | Download without authentication |

## Auto-Generated Endpoints

For every `FileField`, Cinder generates three endpoints:

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/{collection}/{id}/files/{field}` | Upload a file |
| `GET` | `/api/{collection}/{id}/files/{field}` | Download or redirect to file |
| `DELETE` | `/api/{collection}/{id}/files/{field}` | Delete a file |

## Next Steps

- [Backends](/file-storage/backends/) — Local, S3, and custom storage
- [Security](/file-storage/security/) — Upload validation and protections