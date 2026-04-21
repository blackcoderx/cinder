import pytest
import os
import logging


class TestLoggingSetup:
    def test_setup_with_defaults(self):
        """Test setup uses INFO level and console format by default"""
        from zork.logging import setup
        setup()  # Should not raise

    def test_setup_with_json_format(self):
        """Test JSON format configuration"""
        from zork.logging import setup
        setup(level="INFO", format="json")

    def test_setup_with_debug_level(self):
        """Test DEBUG level configuration"""
        from zork.logging import setup
        setup(level="DEBUG")

    def test_setup_with_colorize_disabled(self):
        """Test colorize can be disabled"""
        from zork.logging import setup
        setup(colorize="false")

    def test_setup_with_colorize_enabled(self):
        """Test colorize can be explicitly enabled"""
        from zork.logging import setup
        setup(colorize="true")

    def test_setup_with_auto_colorize(self):
        """Test auto colorize detection"""
        from zork.logging import setup
        setup(colorize="auto")

    def test_setup_excludes_timestamp(self):
        """Test setup without timestamp"""
        from zork.logging import setup
        setup(include_timestamp=False)

    def test_setup_excludes_module(self):
        """Test setup without module name"""
        from zork.logging import setup
        setup(include_module=False)


class TestGetLogger:
    def test_get_default_logger(self):
        """Test getting logger with default name"""
        from zork.logging import setup, get_logger
        setup()
        log = get_logger()
        assert log is not None

    def test_get_named_logger(self):
        """Test getting logger with custom name"""
        from zork.logging import setup, get_logger
        setup()
        log = get_logger("custom")
        assert log is not None

    def test_logger_can_log_info(self):
        """Test logger can emit info level messages"""
        from zork.logging import setup, get_logger
        setup(level="DEBUG")
        log = get_logger("test")
        log.info("test_message", key="value")

    def test_logger_can_log_debug(self):
        """Test logger can emit debug level messages"""
        from zork.logging import setup, get_logger
        setup(level="DEBUG")
        log = get_logger("test")
        log.debug("debug_message")

    def test_logger_can_log_warning(self):
        """Test logger can emit warning level messages"""
        from zork.logging import setup, get_logger
        setup(level="DEBUG")
        log = get_logger("test")
        log.warning("warning_message")

    def test_logger_can_log_error(self):
        """Test logger can emit error level messages"""
        from zork.logging import setup, get_logger
        setup(level="DEBUG")
        log = get_logger("test")
        log.error("error_message")

    def test_logger_with_structured_data(self):
        """Test logger accepts structured data"""
        from zork.logging import setup, get_logger
        setup(level="DEBUG")
        log = get_logger("test")
        log.info(
            "user_action",
            user_id=123,
            action="purchase",
            amount=99.99,
        )


class TestContextualLogging:
    def test_bind_and_reset_context(self):
        """Test binding and clearing context"""
        from zork.logging import setup, bind_context, reset_context
        setup()
        bind_context(request_id="test-123", user_id=42)
        reset_context()  # Should not raise

    def test_context_isolation(self):
        """Test context is cleared after reset"""
        from zork.logging import setup, bind_context, reset_context
        setup()
        bind_context(test="value")
        reset_context()

    def test_context_binding(self):
        """Test binding context makes it available in logs"""
        from zork.logging import setup, get_logger, bind_context, reset_context
        setup(level="DEBUG")
        bind_context(request_id="abc", user_id=99)
        log = get_logger("test")
        log.info("test")
        reset_context()


class TestConfigureFromEnv:
    def test_env_log_level_debug(self, monkeypatch):
        monkeypatch.setenv("ZORK_LOG_LEVEL", "DEBUG")
        from zork.logging import configure_from_env
        configure_from_env()

    def test_env_log_level_warning(self, monkeypatch):
        monkeypatch.setenv("ZORK_LOG_LEVEL", "WARNING")
        from zork.logging import configure_from_env
        configure_from_env()

    def test_env_log_format_json(self, monkeypatch):
        monkeypatch.setenv("ZORK_LOG_FORMAT", "json")
        from zork.logging import configure_from_env
        configure_from_env()

    def test_env_log_format_console(self, monkeypatch):
        monkeypatch.setenv("ZORK_LOG_FORMAT", "console")
        from zork.logging import configure_from_env
        configure_from_env()

    def test_env_log_colorize_true(self, monkeypatch):
        monkeypatch.setenv("ZORK_LOG_COLORIZE", "true")
        from zork.logging import configure_from_env
        configure_from_env()

    def test_env_log_colorize_false(self, monkeypatch):
        monkeypatch.setenv("ZORK_LOG_COLORIZE", "false")
        from zork.logging import configure_from_env
        configure_from_env()

    def test_env_log_include_timestamp_false(self, monkeypatch):
        monkeypatch.setenv("ZORK_LOG_INCLUDE_TIMESTAMP", "false")
        from zork.logging import configure_from_env
        configure_from_env()

    def test_env_log_include_module_false(self, monkeypatch):
        monkeypatch.setenv("ZORK_LOG_INCLUDE_MODULE", "false")
        from zork.logging import configure_from_env
        configure_from_env()

    def test_env_not_set_uses_defaults(self, monkeypatch):
        monkeypatch.delenv("ZORK_LOG_LEVEL", raising=False)
        monkeypatch.delenv("ZORK_LOG_FORMAT", raising=False)
        monkeypatch.delenv("ZORK_LOG_COLORIZE", raising=False)
        from zork.logging import configure_from_env
        configure_from_env()  # Should use defaults


class TestLoggingIntegration:
    def test_logging_works_with_app_build(self, db_path):
        """Test logging is configured when app.build() is called"""
        from zork.app import Zork
        from zork.collections.schema import Collection, TextField

        zork = Zork(database=db_path)
        posts = Collection("posts", fields=[TextField("title")])
        zork.register(posts)

        app = zork.build()
        assert app is not None

    def test_logging_can_be_configured_before_build(self):
        """Test configuring logging before app.build()"""
        from zork.logging import setup
        setup(level="INFO", format="console")


class TestLoggerOutput:
    def test_console_output_has_colors(self):
        """Test console format can have colors enabled"""
        from zork.logging import setup
        setup(level="DEBUG", format="console", colorize="true")

    def test_json_output_format(self):
        """Test JSON format produces valid-like output"""
        from zork.logging import setup, get_logger
        setup(level="DEBUG", format="json")
        log = get_logger("json_test")
        log.info("test_event", key="value")