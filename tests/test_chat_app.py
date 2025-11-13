"""Unit tests for ChatApp."""

import tempfile
from unittest.mock import MagicMock, patch

import pytest

from src.chat_app import ChatApp, parse_agent_arn


class TestParseAgentArn:
    """Test suite for parse_agent_arn function."""

    @staticmethod
    def test_parse_valid_arn() -> None:
        """Test parsing a valid Bedrock agent ARN."""
        arn = "arn:aws:bedrock:us-west-2:123456789:agent/KYXJLSSOTU"
        agent_id, region = parse_agent_arn(arn)

        assert agent_id == "KYXJLSSOTU"
        assert region == "us-west-2"

    @staticmethod
    def test_parse_different_region() -> None:
        """Test parsing ARN with different region."""
        arn = "arn:aws:bedrock:us-east-1:123456789012:agent/TESTID"
        agent_id, region = parse_agent_arn(arn)

        assert agent_id == "TESTID"
        assert region == "us-east-1"

    @staticmethod
    def test_parse_invalid_arn_format() -> None:
        """Test parsing invalid ARN format."""
        invalid_arn = "not:a:valid:arn"

        with pytest.raises(ValueError, match="Invalid"):
            parse_agent_arn(invalid_arn)

    @staticmethod
    def test_parse_non_bedrock_arn() -> None:
        """Test parsing ARN from different service."""
        s3_arn = "arn:aws:s3:::my-bucket"

        with pytest.raises(ValueError, match="Invalid"):
            parse_agent_arn(s3_arn)

    @staticmethod
    def test_parse_empty_string() -> None:
        """Test parsing empty string."""
        with pytest.raises(ValueError, match="Invalid"):
            parse_agent_arn("")


class TestChatApp:
    """Test suite for ChatApp."""

    @staticmethod
    def test_init() -> None:
        """Test ChatApp initialization."""
        with (
            patch("src.chat_app.BedrockAgentClient"),
            patch("src.chat_app.ChatHistoryLogger"),
            tempfile.TemporaryDirectory() as tmpdir,
        ):
            app = ChatApp("test-id", "test-alias", "us-west-2", tmpdir)

            assert app.running is False

    @staticmethod
    def test_new_session() -> None:
        """Test creating a new session."""
        with (
            patch("src.chat_app.BedrockAgentClient") as mock_client_cls,
            patch("src.chat_app.ChatHistoryLogger") as mock_logger_cls,
            tempfile.TemporaryDirectory() as tmpdir,
        ):
            mock_client = MagicMock()
            mock_client.new_session.return_value = "new-session-id"
            mock_client_cls.return_value = mock_client

            app = ChatApp("test-id", "test-alias", "us-west-2", tmpdir)
            app.new_session()

            mock_client.new_session.assert_called_once()
            # Check that a new logger was created
            assert mock_logger_cls.call_count >= 2  # noqa: PLR2004

    @staticmethod
    def test_process_message_success() -> None:
        """Test processing a successful message."""
        with (
            patch("src.chat_app.BedrockAgentClient") as mock_client_cls,
            patch("src.chat_app.ChatHistoryLogger") as mock_logger_cls,
            tempfile.TemporaryDirectory() as tmpdir,
        ):
            # Setup mocks
            mock_client = MagicMock()
            mock_response = {
                "completion": "Test response",
                "session_id": "test-session",
            }
            mock_client.invoke_agent.return_value = mock_response
            mock_client_cls.return_value = mock_client

            mock_logger = MagicMock()
            mock_logger_cls.return_value = mock_logger

            # Test
            app = ChatApp("test-id", "test-alias", "us-west-2", tmpdir)
            result = app.process_message("Test input")

            assert result == "Test response"
            mock_client.invoke_agent.assert_called_once_with("Test input")
            mock_logger.log_exchange.assert_called_once()

    @staticmethod
    def test_process_message_error() -> None:
        """Test processing a message that raises an error."""
        with (
            patch("src.chat_app.BedrockAgentClient") as mock_client_cls,
            patch("src.chat_app.ChatHistoryLogger"),
            tempfile.TemporaryDirectory() as tmpdir,
        ):
            # Setup mock to raise error
            mock_client = MagicMock()
            mock_client.invoke_agent.side_effect = Exception("API Error")
            mock_client_cls.return_value = mock_client

            app = ChatApp("test-id", "test-alias", "us-west-2", tmpdir)
            result = app.process_message("Test input")

            assert result is None

    @staticmethod
    def test_display_history(capsys: pytest.CaptureFixture[str]) -> None:
        """Test displaying chat history."""
        with (
            patch("src.chat_app.BedrockAgentClient"),
            patch("src.chat_app.ChatHistoryLogger") as mock_logger_cls,
            tempfile.TemporaryDirectory() as tmpdir,
        ):
            mock_logger = MagicMock()
            mock_history = [
                {
                    "timestamp": "2024-01-01T12:00:00",
                    "role": "user",
                    "content": "Hello",
                },
                {
                    "timestamp": "2024-01-01T12:00:01",
                    "role": "agent",
                    "content": "Hi there",
                },
            ]
            mock_logger.read_history.return_value = mock_history
            mock_logger_cls.return_value = mock_logger

            app = ChatApp("test-id", "test-alias", "us-west-2", tmpdir)
            app.display_history()

            captured = capsys.readouterr()
            assert "Hello" in captured.out
            assert "Hi there" in captured.out
            assert "USER:" in captured.out
            assert "AGENT:" in captured.out

    @staticmethod
    def test_display_history_empty(capsys: pytest.CaptureFixture[str]) -> None:
        """Test displaying empty chat history."""
        with (
            patch("src.chat_app.BedrockAgentClient"),
            patch("src.chat_app.ChatHistoryLogger") as mock_logger_cls,
            tempfile.TemporaryDirectory() as tmpdir,
        ):
            mock_logger = MagicMock()
            mock_logger.read_history.return_value = []
            mock_logger_cls.return_value = mock_logger

            app = ChatApp("test-id", "test-alias", "us-west-2", tmpdir)
            app.display_history()

            captured = capsys.readouterr()
            assert "No chat history" in captured.out
