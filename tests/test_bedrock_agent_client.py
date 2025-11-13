"""Unit tests for BedrockAgentClient."""

from unittest.mock import MagicMock, patch

import pytest
from botocore.exceptions import ClientError

from src.bedrock_agent_client import BedrockAgentClient


class TestBedrockAgentClient:
    """Test suite for BedrockAgentClient."""

    def test_init_with_default_session(self) -> None:
        """Test client initialization with auto-generated session ID."""
        with patch("src.bedrock_agent_client.boto3"):
            client = BedrockAgentClient("test-agent-id", "test-alias-id")
            assert client.agent_id == "test-agent-id"
            assert client.agent_alias_id == "test-alias-id"
            assert client.region_name == "us-west-2"
            assert client.session_id is not None
            assert len(client.session_id) > 0

    def test_init_with_custom_session(self) -> None:
        """Test client initialization with provided session ID."""
        custom_session = "custom-session-id"
        with patch("src.bedrock_agent_client.boto3"):
            client = BedrockAgentClient(
                "test-agent-id",
                "test-alias-id",
                session_id=custom_session,
            )
            assert client.session_id == custom_session

    def test_invoke_agent_success(self) -> None:
        """Test successful agent invocation."""
        with patch("src.bedrock_agent_client.boto3") as mock_boto3:
            # Setup mock response
            mock_client = MagicMock()
            mock_boto3.client.return_value = mock_client

            response_text = "Hello! How can I help you?"
            mock_event_stream = [
                {
                    "chunk": {
                        "bytes": response_text.encode("utf-8"),
                    }
                }
            ]
            mock_client.invoke_agent.return_value = {"completion": mock_event_stream}

            # Create client and invoke
            client = BedrockAgentClient("test-agent-id", "test-alias-id")
            result = client.invoke_agent("Hello")

            # Verify result
            assert result["completion"] == response_text
            assert result["session_id"] == client.session_id
            assert result["trace"] is None

            # Verify API was called correctly
            mock_client.invoke_agent.assert_called_once_with(
                agentId="test-agent-id",
                agentAliasId="test-alias-id",
                sessionId=client.session_id,
                inputText="Hello",
                enableTrace=False,
                endSession=False,
            )

    def test_invoke_agent_with_trace(self) -> None:
        """Test agent invocation with trace enabled."""
        with patch("src.bedrock_agent_client.boto3") as mock_boto3:
            mock_client = MagicMock()
            mock_boto3.client.return_value = mock_client

            mock_event_stream = [
                {"chunk": {"bytes": b"Response"}},
                {"trace": {"traceId": "test-trace"}},
            ]
            mock_client.invoke_agent.return_value = {"completion": mock_event_stream}

            client = BedrockAgentClient("test-agent-id", "test-alias-id")
            result = client.invoke_agent("Test", enable_trace=True)

            assert result["trace"] is not None
            assert len(result["trace"]) == 1
            assert result["trace"][0] == {"traceId": "test-trace"}

    def test_invoke_agent_client_error(self) -> None:
        """Test agent invocation with AWS client error."""
        with patch("src.bedrock_agent_client.boto3") as mock_boto3:
            mock_client = MagicMock()
            mock_boto3.client.return_value = mock_client

            # Simulate AWS error
            error_response = {
                "Error": {
                    "Code": "AccessDeniedException",
                    "Message": "Access denied",
                }
            }
            mock_client.invoke_agent.side_effect = ClientError(
                error_response,
                "invoke_agent",
            )

            client = BedrockAgentClient("test-agent-id", "test-alias-id")

            with pytest.raises(ClientError) as exc_info:
                client.invoke_agent("Test")

            assert "Failed to invoke agent" in str(exc_info.value)

    def test_get_session_id(self) -> None:
        """Test getting the current session ID."""
        with patch("src.bedrock_agent_client.boto3"):
            client = BedrockAgentClient("test-agent-id", "test-alias-id")
            session_id = client.get_session_id()
            assert session_id == client.session_id
            assert isinstance(session_id, str)

    def test_new_session(self) -> None:
        """Test creating a new session."""
        with patch("src.bedrock_agent_client.boto3"):
            client = BedrockAgentClient("test-agent-id", "test-alias-id")
            old_session = client.get_session_id()

            new_session = client.new_session()

            assert new_session != old_session
            assert client.session_id == new_session
            assert isinstance(new_session, str)

    def test_invoke_agent_multiple_chunks(self) -> None:
        """Test agent invocation with multiple response chunks."""
        with patch("src.bedrock_agent_client.boto3") as mock_boto3:
            mock_client = MagicMock()
            mock_boto3.client.return_value = mock_client

            mock_event_stream = [
                {"chunk": {"bytes": b"Hello "}},
                {"chunk": {"bytes": b"World"}},
                {"chunk": {"bytes": b"!"}},
            ]
            mock_client.invoke_agent.return_value = {"completion": mock_event_stream}

            client = BedrockAgentClient("test-agent-id", "test-alias-id")
            result = client.invoke_agent("Test")

            assert result["completion"] == "Hello World!"

    def test_invoke_agent_end_session(self) -> None:
        """Test agent invocation with end_session flag."""
        with patch("src.bedrock_agent_client.boto3") as mock_boto3:
            mock_client = MagicMock()
            mock_boto3.client.return_value = mock_client
            mock_client.invoke_agent.return_value = {"completion": []}

            client = BedrockAgentClient("test-agent-id", "test-alias-id")
            client.invoke_agent("Goodbye", end_session=True)

            call_args = mock_client.invoke_agent.call_args
            assert call_args[1]["endSession"] is True
