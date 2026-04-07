def test_all_public_imports():
    """Verify all public API symbols are importable from the top-level package."""
    from cinder import Cinder
    from cinder import Collection
    from cinder import Auth
    from cinder import CinderError
    from cinder import TextField, IntField, FloatField, BoolField
    from cinder import DateTimeField, URLField, JSONField, RelationField

    assert Cinder is not None
    assert Collection is not None
    assert Auth is not None
    assert CinderError is not None


def test_dotenv_loading(tmp_path, monkeypatch):
    """Verify .env files are loaded."""
    import os
    env_file = tmp_path / ".env"
    env_file.write_text("CINDER_TEST_VAR=hello_from_dotenv\n")
    monkeypatch.chdir(tmp_path)

    from dotenv import load_dotenv
    load_dotenv(str(env_file))

    assert os.getenv("CINDER_TEST_VAR") == "hello_from_dotenv"
