---
title: MySQL / MariaDB
description: Use MySQL or MariaDB as your database
---

## Install the extra dependency

```bash
pip install "cinder[mysql]"
# or
uv add "cinder[mysql]"
```

This installs [aiomysql](https://github.com/aio-libs/aiomysql), the async MySQL driver.

## Configuration

```dotenv
DATABASE_URL=mysql://user:password@localhost:3306/mydb
```

Or pass directly:

```python
app = Cinder(database="mysql://user:password@localhost:3306/mydb")
```

## Advanced configuration

```python
from cinder.db.backends.mysql import MySQLBackend

app.configure_database(
    MySQLBackend(
        url="mysql://user:password@localhost:3306/mydb",
        min_size=2,
        max_size=10,
    )
)
```

## Notes

- MariaDB is fully supported — use the same `mysql://` scheme
- Connection URL should include the database name
- Ensure the database exists before starting the app (`CREATE DATABASE mydb`)
