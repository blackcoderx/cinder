from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime
from typing import Any, Callable

from pydantic import BaseModel, Field as PydanticField, AnyUrl, create_model


class Field:
    """Base class for collection field definitions."""

    def __init__(
        self,
        name: str,
        *,
        required: bool = False,
        default: Any = None,
        unique: bool = False,
    ):
        self.name = name
        self.required = required
        self.default = default
        self.unique = unique

    def sqlite_type(self) -> str:
        raise NotImplementedError

    def pydantic_field_info(self) -> tuple[type, Any]:
        """Return (python_type, FieldInfo) for Pydantic model creation."""
        raise NotImplementedError

    def column_sql(self) -> str:
        parts = [self.name, self.sqlite_type()]
        if self.required:
            parts.append("NOT NULL")
        if self.unique:
            parts.append("UNIQUE")
        return " ".join(parts)


class TextField(Field):
    def __init__(self, name: str, *, required: bool = False, default: Any = None,
                 unique: bool = False, min_length: int | None = None,
                 max_length: int | None = None):
        super().__init__(name, required=required, default=default, unique=unique)
        self.min_length = min_length
        self.max_length = max_length

    def sqlite_type(self) -> str:
        return "TEXT"

    def pydantic_field_info(self) -> tuple[type, Any]:
        kwargs = {}
        if self.min_length is not None:
            kwargs["min_length"] = self.min_length
        if self.max_length is not None:
            kwargs["max_length"] = self.max_length
        if self.required:
            return (str, PydanticField(**kwargs))
        if self.default is not None:
            return (str | None, PydanticField(default=self.default, **kwargs))
        return (str | None, PydanticField(default=None, **kwargs))


class IntField(Field):
    def __init__(self, name: str, *, required: bool = False, default: Any = None,
                 unique: bool = False, min_value: int | None = None,
                 max_value: int | None = None):
        super().__init__(name, required=required, default=default, unique=unique)
        self.min_value = min_value
        self.max_value = max_value

    def sqlite_type(self) -> str:
        return "INTEGER"

    def pydantic_field_info(self) -> tuple[type, Any]:
        kwargs = {}
        if self.min_value is not None:
            kwargs["ge"] = self.min_value
        if self.max_value is not None:
            kwargs["le"] = self.max_value
        if self.required:
            return (int, PydanticField(**kwargs))
        if self.default is not None:
            return (int | None, PydanticField(default=self.default, **kwargs))
        return (int | None, PydanticField(default=None, **kwargs))


class FloatField(Field):
    def __init__(self, name: str, *, required: bool = False, default: Any = None,
                 unique: bool = False, min_value: float | None = None,
                 max_value: float | None = None):
        super().__init__(name, required=required, default=default, unique=unique)
        self.min_value = min_value
        self.max_value = max_value

    def sqlite_type(self) -> str:
        return "REAL"

    def pydantic_field_info(self) -> tuple[type, Any]:
        kwargs = {}
        if self.min_value is not None:
            kwargs["ge"] = self.min_value
        if self.max_value is not None:
            kwargs["le"] = self.max_value
        if self.required:
            return (float, PydanticField(**kwargs))
        if self.default is not None:
            return (float | None, PydanticField(default=self.default, **kwargs))
        return (float | None, PydanticField(default=None, **kwargs))


class BoolField(Field):
    def sqlite_type(self) -> str:
        return "INTEGER"

    def pydantic_field_info(self) -> tuple[type, Any]:
        if self.required:
            return (bool, PydanticField())
        if self.default is not None:
            return (bool | None, PydanticField(default=self.default))
        return (bool | None, PydanticField(default=None))


class DateTimeField(Field):
    def __init__(self, name: str, *, required: bool = False, default: Any = None,
                 unique: bool = False, auto_now: bool = False):
        super().__init__(name, required=required, default=default, unique=unique)
        self.auto_now = auto_now

    def sqlite_type(self) -> str:
        return "TEXT"

    def pydantic_field_info(self) -> tuple[type, Any]:
        if self.auto_now:
            return (datetime | None, PydanticField(default=None))
        if self.required:
            return (datetime, PydanticField())
        return (datetime | None, PydanticField(default=self.default))


class URLField(Field):
    def sqlite_type(self) -> str:
        return "TEXT"

    def pydantic_field_info(self) -> tuple[type, Any]:
        if self.required:
            return (AnyUrl, PydanticField())
        if self.default is not None:
            return (AnyUrl | None, PydanticField(default=self.default))
        return (AnyUrl | None, PydanticField(default=None))


class JSONField(Field):
    def sqlite_type(self) -> str:
        return "TEXT"

    def pydantic_field_info(self) -> tuple[type, Any]:
        if self.required:
            return (Any, PydanticField())
        return (Any, PydanticField(default=self.default))


class RelationField(Field):
    def __init__(self, name: str, *, collection: str, required: bool = False,
                 unique: bool = False):
        super().__init__(name, required=required, default=None, unique=unique)
        self.collection = collection

    def sqlite_type(self) -> str:
        return "TEXT"

    def pydantic_field_info(self) -> tuple[type, Any]:
        if self.required:
            return (str, PydanticField())
        return (str | None, PydanticField(default=None))


class Collection:
    """A named schema that Cinder turns into a full CRUD API."""

    def __init__(self, name: str, fields: list[Field]):
        self.name = name
        self.fields = fields
        self._hooks: dict[str, list[Callable]] = defaultdict(list)

    def on(self, event: str, handler: Callable) -> None:
        """Register a hook function for a collection event."""
        self._hooks[event].append(handler)

    def build_create_table_sql(self) -> str:
        """Generate CREATE TABLE SQL for this collection."""
        columns = [
            "id TEXT PRIMARY KEY",
        ]
        for field in self.fields:
            columns.append(field.column_sql())
        columns.append("created_at TEXT NOT NULL")
        columns.append("updated_at TEXT NOT NULL")
        col_str = ", ".join(columns)
        return f"CREATE TABLE IF NOT EXISTS {self.name} ({col_str})"

    def build_pydantic_model(self) -> type[BaseModel]:
        """Dynamically create a Pydantic model for input validation."""
        field_definitions: dict[str, Any] = {}
        for field in self.fields:
            python_type, field_info = field.pydantic_field_info()
            field_definitions[field.name] = (python_type, field_info)
        model = create_model(
            f"{self.name.title()}Model",
            **field_definitions,
        )
        return model
