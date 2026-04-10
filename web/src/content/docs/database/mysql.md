---
title: MySQL
description: Use MySQL as your database backend
---

## Install the MySQL Extra

```bash
pip install cinder[mysql]
# or
uv add cinder[mysql]
```

## Connection String

```python
app = Cinder(database="mysql://user:pass@localhost:3306/mydb")
```

Dialect aliases also accepted:

```python
# These all work
app = Cinder(database="mysql://user:pass@localhost/mydb")
app = Cinder(database="mysql+aiomysql://user:pass@localhost/mydb")
app = Cinder(database="mysql+asyncmy://user:pass@localhost/mydb")
```

## Environment Variable

```bash
export CINDER_DATABASE_URL=mysql://user:pass@localhost:3306/mydb
```

## Features

- **Connection pool** — Uses `aiomysql.create_pool` with `DictCursor`
- **Autocommit** — Enabled by default
- **TEXT PRIMARY KEY** — Automatically rewritten to `VARCHAR(36)` (MySQL requires a length prefix)

## Example

```python
import os
from cinder import Cinder, Collection, TextField

app = Cinder(database=os.environ["DATABASE_URL"])

posts = Collection("posts", fields=[
    TextField("title", required=True),
])

app.register(posts, auth=["read:public", "write:authenticated"])
app.serve()
```

## Why MySQL?

- **Widely used** — Popular choice for web applications
- **Good documentation** — Extensive resources available
- **Compatible** — Many hosting platforms support it

## Next Steps

- [PostgreSQL](/database/postgresql/) — Alternative SQL database
- [SQLite](/database/sqlite/) — Development database
- [Indexes](/database/indexes/) — Optimize queries