import aiosqlite


class Database:
    """Async SQLite database connection manager.

    Uses WAL mode for concurrent reads and returns rows as dictionaries.
    Supports lazy connection: auto-connects on first use if not already connected.
    """

    def __init__(self, path: str):
        self.path = path
        self._connection: aiosqlite.Connection | None = None

    async def connect(self) -> None:
        if self._connection is not None:
            return
        self._connection = await aiosqlite.connect(self.path)
        self._connection.row_factory = aiosqlite.Row
        await self._connection.execute("PRAGMA journal_mode=WAL")
        await self._connection.execute("PRAGMA foreign_keys=ON")
        await self._connection.commit()

    async def disconnect(self) -> None:
        if self._connection:
            await self._connection.close()
            self._connection = None

    async def _ensure_connected(self) -> None:
        if self._connection is None:
            await self.connect()

    async def execute(self, sql: str, params: tuple = ()) -> None:
        await self._ensure_connected()
        await self._connection.execute(sql, params)
        await self._connection.commit()

    async def fetch_one(self, sql: str, params: tuple = ()) -> dict | None:
        await self._ensure_connected()
        cursor = await self._connection.execute(sql, params)
        row = await cursor.fetchone()
        if row is None:
            return None
        return dict(row)

    async def fetch_all(self, sql: str, params: tuple = ()) -> list[dict]:
        await self._ensure_connected()
        cursor = await self._connection.execute(sql, params)
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]
