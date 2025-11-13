"""Integration tests for the chat application.

These tests verify end-to-end functionality without mocking AWS services.
They require valid AWS credentials and a real Bedrock agent to run.
"""

import os
import tempfile

import pytest

from src.bedrock_agent_client import BedrockAgentClient
from src.chat_app import parse_agent_arn
from src.chat_history_logger import ChatHistoryLogger


@pytest.mark.integration
@pytest.mark.skipif(
    not os.getenv("BEDROCK_AGENT_ID") and not os.getenv("BEDROCK_AGENT_ARN"),
    reason="Requires BEDROCK_AGENT_ID or BEDROCK_AGENT_ARN environment variable",
)
class TestIntegration:
    """Integration tests requiring real AWS credentials and agent."""

    @staticmethod
    def get_agent_config() -> tuple[str, str, str]:
        """Get agent configuration from environment.

        Returns:
            Tuple of (agent_id, agent_alias_id, region)
        """
        agent_arn = os.getenv("BEDROCK_AGENT_ARN")
        agent_id = os.getenv("BEDROCK_AGENT_ID")
        agent_alias_id = os.getenv("BEDROCK_AGENT_ALIAS_ID", "TSTALIASID")
        region = os.getenv("AWS_REGION", "us-west-2")

        if agent_arn and not agent_id:
            agent_id, region = parse_agent_arn(agent_arn)

        if not agent_id:
            pytest.skip("BEDROCK_AGENT_ID or BEDROCK_AGENT_ARN not configured")

        return agent_id, agent_alias_id, region

    @staticmethod
    def test_bedrock_client_integration() -> None:
        """Test real interaction with Bedrock agent."""
        agent_id, agent_alias_id, region = TestIntegration.get_agent_config()

        client = BedrockAgentClient(agent_id, agent_alias_id, region)

        # Send a simple test message
        response = client.invoke_agent("Hello, can you help me?")

        # Verify response structure
        assert "completion" in response
        assert "session_id" in response
        assert isinstance(response["completion"], str)
        assert len(response["completion"]) > 0
        assert response["session_id"] == client.get_session_id()

    @staticmethod
    def test_session_continuity() -> None:
        """Test that sessions maintain context across multiple messages."""
        agent_id, agent_alias_id, region = TestIntegration.get_agent_config()

        client = BedrockAgentClient(agent_id, agent_alias_id, region)
        session_id = client.get_session_id()

        # Send first message
        response1 = client.invoke_agent("My name is Alice")
        assert response1["session_id"] == session_id

        # Send second message in same session
        response2 = client.invoke_agent("What is my name?")
        assert response2["session_id"] == session_id

        # Verify both responses have content
        assert len(response1["completion"]) > 0
        assert len(response2["completion"]) > 0

    @staticmethod
    def test_new_session_integration() -> None:
        """Test creating a new session."""
        agent_id, agent_alias_id, region = TestIntegration.get_agent_config()

        client = BedrockAgentClient(agent_id, agent_alias_id, region)
        original_session = client.get_session_id()

        # Create new session
        new_session = client.new_session()

        assert new_session != original_session
        assert client.get_session_id() == new_session

    @staticmethod
    def test_end_to_end_with_logging() -> None:
        """Test complete flow with client and logger."""
        agent_id, agent_alias_id, region = TestIntegration.get_agent_config()

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create client and logger
            client = BedrockAgentClient(agent_id, agent_alias_id, region)
            logger = ChatHistoryLogger(tmpdir, client.get_session_id())

            # Send a message
            user_message = "What is 2+2?"
            response = client.invoke_agent(user_message)

            # Log the exchange
            logger.log_exchange(
                user_message,
                response["completion"],
                {"session_id": response["session_id"]},
            )

            # Verify log was written
            assert logger.log_file.exists()

            # Read and verify history
            history = logger.read_history()
            assert len(history) >= 2  # noqa: PLR2004
            assert history[0]["role"] == "user"
            assert history[0]["content"] == user_message
            assert history[1]["role"] == "agent"
            assert len(history[1]["content"]) > 0


@pytest.mark.integration
def test_integration_marker() -> None:
    """Verify integration test marker works."""
    # This is a dummy test to verify the marker works
    assert True
