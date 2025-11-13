"""Client for interacting with AWS Bedrock Agent Runtime."""

import uuid
from typing import Any, Optional

import boto3
from botocore.exceptions import ClientError


class BedrockAgentClient:
    """Client to invoke AWS Bedrock agents and manage chat sessions."""

    def __init__(
        self,
        agent_id: str,
        agent_alias_id: str,
        region_name: str = "us-west-2",
        session_id: Optional[str] = None,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        aws_session_token: Optional[str] = None,
    ) -> None:
        """Initialize the Bedrock Agent client.

        Args:
            agent_id: The Bedrock agent ID
            agent_alias_id: The agent alias ID
            region_name: AWS region name
            session_id: Optional session ID. If not provided, a new one is generated
            aws_access_key_id: Optional AWS access key ID (overrides default credentials)
            aws_secret_access_key: Optional AWS secret access key (overrides default)
            aws_session_token: Optional AWS session token for temporary credentials
        """
        self.agent_id = agent_id
        self.agent_alias_id = agent_alias_id
        self.region_name = region_name
        self.session_id = session_id or str(uuid.uuid4())

        # Build client kwargs
        client_kwargs = {"region_name": region_name}
        if aws_access_key_id and aws_secret_access_key:
            client_kwargs["aws_access_key_id"] = aws_access_key_id
            client_kwargs["aws_secret_access_key"] = aws_secret_access_key
            if aws_session_token:
                client_kwargs["aws_session_token"] = aws_session_token

        self.client = boto3.client("bedrock-agent-runtime", **client_kwargs)  # type: ignore[call-overload]

    def invoke_agent(
        self,
        prompt: str,
        enable_trace: bool = False,
        end_session: bool = False,
    ) -> dict[str, Any]:
        """Invoke the Bedrock agent with a prompt.

        Args:
            prompt: The user's input text
            enable_trace: Whether to enable trace for debugging
            end_session: Whether to end the session after this invocation

        Returns:
            Dictionary containing the response and metadata

        Raises:
            ClientError: If the AWS API call fails
        """
        try:
            response = self.client.invoke_agent(
                agentId=self.agent_id,
                agentAliasId=self.agent_alias_id,
                sessionId=self.session_id,
                inputText=prompt,
                enableTrace=enable_trace,
                endSession=end_session,
            )

            # Process the event stream
            completion = ""
            trace_data = []

            event_stream = response.get("completion", [])
            for event in event_stream:
                if "chunk" in event:
                    chunk = event["chunk"]
                    if "bytes" in chunk:
                        completion += chunk["bytes"].decode("utf-8")

                if enable_trace and "trace" in event:
                    trace_data.append(event["trace"])

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_message = e.response["Error"]["Message"]
            raise ClientError(
                {
                    "Error": {
                        "Code": error_code,
                        "Message": f"Failed to invoke agent: {error_message}",
                    }
                },
                "invoke_agent",
            ) from e
        else:
            return {
                "completion": completion,
                "session_id": self.session_id,
                "trace": trace_data if enable_trace else None,
            }

    def get_session_id(self) -> str:
        """Get the current session ID.

        Returns:
            The session ID string
        """
        return self.session_id

    def new_session(self) -> str:
        """Create a new session ID.

        Returns:
            The new session ID
        """
        self.session_id = str(uuid.uuid4())
        return self.session_id
