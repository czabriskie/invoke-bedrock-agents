"""Simple chat application for AWS Bedrock agents."""

import os
import sys
from typing import Optional

from dotenv import load_dotenv

from .bedrock_agent_client import BedrockAgentClient
from .chat_history_logger import ChatHistoryLogger


def parse_agent_arn(arn: str) -> tuple[str, str]:
    """Parse agent ID and region from ARN.

    Args:
        arn: The Bedrock agent ARN

    Returns:
        Tuple of (agent_id, region)

    Raises:
        ValueError: If ARN format is invalid
    """
    try:
        parts = arn.split(":")
        if len(parts) < 6 or parts[2] != "bedrock":
            raise ValueError("Invalid Bedrock agent ARN format")
        region = parts[3]
        agent_id = parts[5].split("/")[-1]
        return agent_id, region
    except (IndexError, AttributeError) as e:
        raise ValueError(f"Invalid ARN format: {arn}") from e


class ChatApp:
    """Interactive chat application for Bedrock agents."""

    def __init__(
        self,
        agent_id: str,
        agent_alias_id: str,
        region_name: str = "us-west-2",
        log_dir: str = "./logs",
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        aws_session_token: Optional[str] = None,
    ) -> None:
        """Initialize the chat application.

        Args:
            agent_id: The Bedrock agent ID
            agent_alias_id: The agent alias ID
            region_name: AWS region name
            log_dir: Directory for chat history logs
            aws_access_key_id: Optional AWS access key ID
            aws_secret_access_key: Optional AWS secret access key
            aws_session_token: Optional AWS session token for temporary credentials
        """
        self.client = BedrockAgentClient(
            agent_id,
            agent_alias_id,
            region_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_session_token=aws_session_token,
        )
        self.logger = ChatHistoryLogger(log_dir, self.client.get_session_id())
        self.running = False

    def display_welcome(self) -> None:
        """Display welcome message and instructions."""
        print("\n" + "=" * 70)
        print("AWS Bedrock Agent Chat")
        print("=" * 70)
        print(f"Session ID: {self.client.get_session_id()}")
        print(f"Log file: {self.logger.get_log_path()}")
        print("\nCommands:")
        print("  - Type your message and press Enter to chat")
        print("  - Type 'quit' or 'exit' to end the session")
        print("  - Type 'new' to start a new session")
        print("  - Type 'history' to view chat history")
        print("=" * 70 + "\n")

    def display_history(self) -> None:
        """Display the chat history."""
        history = self.logger.read_history()
        if not history:
            print("\nNo chat history available.\n")
            return

        print("\n" + "-" * 70)
        print("Chat History")
        print("-" * 70)
        for entry in history:
            role = entry["role"].upper()
            content = entry["content"]
            timestamp = entry["timestamp"]
            print(f"[{timestamp}] {role}:")
            print(f"  {content}\n")
        print("-" * 70 + "\n")

    def new_session(self) -> None:
        """Start a new chat session."""
        session_id = self.client.new_session()
        self.logger = ChatHistoryLogger("./logs", session_id)
        print(f"\n✓ Started new session: {session_id}")
        print(f"✓ New log file: {self.logger.get_log_path()}\n")

    def process_message(self, user_input: str) -> Optional[str]:
        """Process user input and get agent response.

        Args:
            user_input: The user's message

        Returns:
            The agent's response, or None if an error occurred
        """
        try:
            print("\n🤖 Agent is thinking...\n")
            response = self.client.invoke_agent(user_input)
            agent_response = response["completion"]

            # Log the exchange
            self.logger.log_exchange(
                user_input,
                agent_response,
                {"session_id": response["session_id"]},
            )

            return agent_response

        except Exception as e:
            print(f"\n❌ Error: {e}\n")
            return None

    def run(self) -> None:
        """Run the interactive chat loop."""
        self.display_welcome()
        self.running = True

        while self.running:
            try:
                user_input = input("You: ").strip()

                if not user_input:
                    continue

                # Handle commands
                if user_input.lower() in ("quit", "exit"):
                    print("\n👋 Goodbye! Chat history saved.\n")
                    self.running = False
                    break

                if user_input.lower() == "new":
                    self.new_session()
                    continue

                if user_input.lower() == "history":
                    self.display_history()
                    continue

                # Process regular message
                agent_response = self.process_message(user_input)
                if agent_response:
                    print(f"Agent: {agent_response}\n")

            except KeyboardInterrupt:
                print("\n\n👋 Goodbye! Chat history saved.\n")
                self.running = False
                break
            except EOFError:
                self.running = False
                break


def main() -> None:
    """Main entry point for the chat application."""
    load_dotenv()

    # Get configuration from environment or command line
    agent_arn = os.getenv("BEDROCK_AGENT_ARN")
    agent_id = os.getenv("BEDROCK_AGENT_ID")
    agent_alias_id = os.getenv("BEDROCK_AGENT_ALIAS_ID", "TSTALIASID")
    region = os.getenv("AWS_REGION", "us-west-2")
    log_dir = os.getenv("CHAT_HISTORY_DIR", "./logs")

    # Get AWS credentials from environment (optional)
    aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    aws_session_token = os.getenv("AWS_SESSION_TOKEN")

    # Parse ARN if provided
    if agent_arn and not agent_id:
        try:
            agent_id, region = parse_agent_arn(agent_arn)
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)

    # Validate required configuration
    if not agent_id:
        print("Error: BEDROCK_AGENT_ID or BEDROCK_AGENT_ARN must be set")
        print("Set them in .env file or as environment variables")
        sys.exit(1)

    # Create and run the chat app
    app = ChatApp(
        agent_id,
        agent_alias_id,
        region,
        log_dir,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        aws_session_token=aws_session_token,
    )
    app.run()


if __name__ == "__main__":
    main()
