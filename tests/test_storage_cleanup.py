"""Tests for storage/cleanup.py - orphan file cleanup on record deletion.

These tests cover the hook registration logic. The actual cleanup on record deletion
is covered by test_storage_routes.py::TestCleanup which does full integration testing.
"""

from __future__ import annotations

from zork.collections.schema import Collection, FileField, TextField
from zork.hooks.registry import HookRegistry
from zork.storage.backends import LocalFileBackend
from zork.storage.cleanup import install_file_cleanup


class TestInstallFileCleanup:
    """Tests for install_file_cleanup() function."""

    def test_installs_hook_for_collection_with_filefield(self, tmp_path):
        """install_file_cleanup registers after_delete hook for collections with FileField."""
        backend = LocalFileBackend(str(tmp_path / "storage"))
        collections = {
            "posts": (
                Collection(
                    "posts",
                    fields=[
                        TextField("title"),
                        FileField("cover"),
                    ],
                ),
                ["read:public", "write:public"],
            )
        }
        registry = HookRegistry()

        install_file_cleanup(registry, backend, collections)

        assert "posts:after_delete" in registry._hooks

    def test_no_hook_for_collection_without_filefield(self, tmp_path):
        """Collections without FileField should not get cleanup hooks registered."""
        backend = LocalFileBackend(str(tmp_path / "storage"))
        collections = {
            "posts": (
                Collection(
                    "posts",
                    fields=[
                        TextField("title"),
                    ],
                ),
                ["read:public", "write:public"],
            )
        }
        registry = HookRegistry()

        install_file_cleanup(registry, backend, collections)

        assert "posts:after_delete" not in registry._hooks

    def test_multiple_filefields_each_get_cleanup(self, tmp_path):
        """Multiple FileFields in the same collection still only get one after_delete hook."""
        backend = LocalFileBackend(str(tmp_path / "storage"))
        collections = {
            "posts": (
                Collection(
                    "posts",
                    fields=[
                        TextField("title"),
                        FileField("cover"),
                        FileField("attachments", multiple=True),
                    ],
                ),
                ["read:public", "write:public"],
            )
        }
        registry = HookRegistry()

        install_file_cleanup(registry, backend, collections)

        assert "posts:after_delete" in registry._hooks
        assert len(registry._hooks["posts:after_delete"]) == 1

    def test_non_tuple_collection_form(self, tmp_path):
        """Accepts collection as direct value (non-tuple) when no auth rules passed."""
        backend = LocalFileBackend(str(tmp_path / "storage"))
        collection = Collection(
            "posts",
            fields=[
                TextField("title"),
                FileField("cover"),
            ],
        )
        collections = {"posts": collection}
        registry = HookRegistry()

        install_file_cleanup(registry, backend, collections)

        assert "posts:after_delete" in registry._hooks

    def test_multiple_collections_with_filefields(self, tmp_path):
        """Each collection with FileFields gets its own hook."""
        backend = LocalFileBackend(str(tmp_path / "storage"))
        collections = {
            "posts": (
                Collection(
                    "posts",
                    fields=[
                        TextField("title"),
                        FileField("cover"),
                    ],
                ),
                ["read:public", "write:public"],
            ),
            "avatars": (
                Collection(
                    "avatars",
                    fields=[
                        TextField("name"),
                        FileField("image"),
                    ],
                ),
                ["read:public", "write:owner"],
            ),
        }
        registry = HookRegistry()

        install_file_cleanup(registry, backend, collections)

        assert "posts:after_delete" in registry._hooks
        assert "avatars:after_delete" in registry._hooks
