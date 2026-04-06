import pytest
from cinder.db.connection import Database


@pytest.fixture
async def db(db_path):
    database = Database(db_path)
    await database.connect()
    yield database
    await database.disconnect()


@pytest.mark.asyncio
async def test_connect_creates_file(db, db_path):
    import os
    assert os.path.exists(db_path)


@pytest.mark.asyncio
async def test_execute_and_fetch(db):
    await db.execute("CREATE TABLE test (id TEXT, name TEXT)")
    await db.execute("INSERT INTO test (id, name) VALUES (?, ?)", ("1", "Alice"))
    row = await db.fetch_one("SELECT * FROM test WHERE id = ?", ("1",))
    assert row is not None
    assert row["id"] == "1"
    assert row["name"] == "Alice"


@pytest.mark.asyncio
async def test_fetch_all(db):
    await db.execute("CREATE TABLE items (id TEXT, val INTEGER)")
    await db.execute("INSERT INTO items (id, val) VALUES (?, ?)", ("a", 1))
    await db.execute("INSERT INTO items (id, val) VALUES (?, ?)", ("b", 2))
    rows = await db.fetch_all("SELECT * FROM items ORDER BY val")
    assert len(rows) == 2
    assert rows[0]["val"] == 1
    assert rows[1]["val"] == 2


@pytest.mark.asyncio
async def test_fetch_one_returns_none_when_missing(db):
    await db.execute("CREATE TABLE empty (id TEXT)")
    row = await db.fetch_one("SELECT * FROM empty WHERE id = ?", ("nope",))
    assert row is None


@pytest.mark.asyncio
async def test_foreign_keys_enabled(db):
    await db.execute("CREATE TABLE parent (id TEXT PRIMARY KEY)")
    await db.execute(
        "CREATE TABLE child (id TEXT, parent_id TEXT REFERENCES parent(id))"
    )
    await db.execute("INSERT INTO parent (id) VALUES ('p1')")
    await db.execute("INSERT INTO child (id, parent_id) VALUES ('c1', 'p1')")
    with pytest.raises(Exception):
        await db.execute("INSERT INTO child (id, parent_id) VALUES ('c2', 'nonexistent')")
