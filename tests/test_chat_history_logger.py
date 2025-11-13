"""Unit tests for ChatHistoryLogger."""

import json
import tempfile
from datetime import datetime
from pathlib import Path

from src.chat_history_logger import ChatHistoryLogger


class TestChatHistoryLogger:
    """Test suite for ChatHistoryLogger."""

    @staticmethod
    def test_init_creates_directory() -> None:
        """Test that logger creates log directory if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = Path(tmpdir) / "test_logs"
            logger = ChatHistoryLogger(str(log_dir))

            assert log_dir.exists()
            assert logger.log_file.parent == log_dir

    @staticmethod
    def test_init_with_session_id() -> None:
        """Test logger initialization with session ID."""
        with tempfile.TemporaryDirectory() as tmpdir:
            session_id = "test-session-123"
            logger = ChatHistoryLogger(tmpdir, session_id)

            # Check that session ID is in filename
            assert session_id[:8] in logger.log_file.name

    @staticmethod
    def test_log_message() -> None:
        """Test logging a single message."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = ChatHistoryLogger(tmpdir)

            logger.log_message("user", "Hello world")

            # Read the log file
            with logger.log_file.open(encoding="utf-8") as f:
                line = f.readline()
                entry = json.loads(line)

            assert entry["role"] == "user"
            assert entry["content"] == "Hello world"
            assert "timestamp" in entry
            # Verify timestamp is valid ISO format
            datetime.fromisoformat(entry["timestamp"])

    @staticmethod
    def test_log_message_with_metadata() -> None:
        """Test logging a message with metadata."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = ChatHistoryLogger(tmpdir)

            metadata = {"session_id": "test-123", "model": "claude"}
            logger.log_message("agent", "Response", metadata)

            with logger.log_file.open(encoding="utf-8") as f:
                entry = json.loads(f.readline())

            assert entry["metadata"] == metadata

    @staticmethod
    def test_log_exchange() -> None:
        """Test logging a complete user-agent exchange."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = ChatHistoryLogger(tmpdir)

            logger.log_exchange("User question", "Agent answer")

            with logger.log_file.open(encoding="utf-8") as f:
                lines = f.readlines()

            assert len(lines) == 2

            user_entry = json.loads(lines[0])
            assert user_entry["role"] == "user"
            assert user_entry["content"] == "User question"

            agent_entry = json.loads(lines[1])
            assert agent_entry["role"] == "agent"
            assert agent_entry["content"] == "Agent answer"

    @staticmethod
    def test_log_exchange_with_metadata() -> None:
        """Test logging an exchange with metadata."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = ChatHistoryLogger(tmpdir)

            metadata = {"temperature": 0.7}
            logger.log_exchange("Question", "Answer", metadata)

            with logger.log_file.open(encoding="utf-8") as f:
                lines = f.readlines()

            for line in lines:
                entry = json.loads(line)
                assert entry["metadata"] == metadata

    @staticmethod
    def test_get_log_path() -> None:
        """Test getting the log file path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = ChatHistoryLogger(tmpdir)
            path = logger.get_log_path()

            assert isinstance(path, Path)
            assert path == logger.log_file

    @staticmethod
    def test_read_history_empty() -> None:
        """Test reading history from empty log file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = ChatHistoryLogger(tmpdir)
            history = logger.read_history()

            assert history == []

    @staticmethod
    def test_read_history() -> None:
        """Test reading chat history."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = ChatHistoryLogger(tmpdir)

            # Log some messages
            logger.log_message("user", "First message")
            logger.log_message("agent", "First response")
            logger.log_message("user", "Second message")

            # Read history
            history = logger.read_history()

            assert len(history) == 3
            assert history[0]["role"] == "user"
            assert history[0]["content"] == "First message"
            assert history[1]["role"] == "agent"
            assert history[1]["content"] == "First response"
            assert history[2]["role"] == "user"
            assert history[2]["content"] == "Second message"

    @staticmethod
    def test_read_history_with_blank_lines() -> None:
        """Test reading history with blank lines in log file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = ChatHistoryLogger(tmpdir)

            # Manually write with blank lines
            with logger.log_file.open("w", encoding="utf-8") as f:
                f.write('{"role": "user", "content": "Test"}\n')
                f.write("\n")  # Blank line
                f.write('{"role": "agent", "content": "Response"}\n')

            history = logger.read_history()

            # Should skip blank lines
            assert len(history) == 2

    @staticmethod
    def test_log_file_naming() -> None:
        """Test that log file has correct naming pattern."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = ChatHistoryLogger(tmpdir)

            filename = logger.log_file.name
            assert filename.startswith("chat_history_")
            assert filename.endswith(".log")

    @staticmethod
    def test_unicode_content() -> None:
        """Test logging messages with unicode characters."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = ChatHistoryLogger(tmpdir)

            unicode_message = "Hello 世界 🌍 émojis"
            logger.log_message("user", unicode_message)

            history = logger.read_history()
            assert history[0]["content"] == unicode_message
