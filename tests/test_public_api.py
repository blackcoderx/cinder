def test_all_public_imports():
    """Verify all public API symbols are importable from the top-level package."""
    from zork import Zork
    from zork import Collection
    from zork import Auth
    from zork import ZorkError
    from zork import TextField, IntField, FloatField, BoolField
    from zork import DateTimeField, URLField, JSONField, RelationField

    assert Zork is not None
    assert Collection is not None
    assert Auth is not None
    assert ZorkError is not None


def test_dotenv_loading(tmp_path, monkeypatch):
    """Verify .env files are loaded."""
    import os

    env_file = tmp_path / ".env"
    env_file.write_text("ZORK_TEST_VAR=hello_from_dotenv\n")
    monkeypatch.chdir(tmp_path)

    from dotenv import load_dotenv

    load_dotenv(str(env_file))

    assert os.getenv("ZORK_TEST_VAR") == "hello_from_dotenv"
