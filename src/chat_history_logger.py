"""Chat history logging functionality."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


class ChatHistoryLogger:
    """Logger for chat conversations with the Bedrock agent."""

    def __init__(self, log_dir: str = "./logs", session_id: Optional[str] = None) -> None:
        """Initialize the chat history logger.

        Args:
            log_dir: Directory to store chat history logs
            session_id: Optional session ID for the log file name
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now(tz=timezone.utc).strftime("%Y%m%d_%H%M%S")
        session_suffix = f"_{session_id[:8]}" if session_id else ""
        self.log_file = self.log_dir / f"chat_history_{timestamp}{session_suffix}.log"

    def log_message(
        self,
        role: str,
        content: str,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        """Log a single message to the chat history.

        Args:
            role: The role of the message sender (e.g., 'user', 'agent')
            content: The message content
            metadata: Optional metadata to include with the message
        """
        entry: dict[str, Any] = {
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
            "role": role,
            "content": content,
        }

        if metadata:
            entry["metadata"] = metadata

        with self.log_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def log_exchange(
        self,
        user_message: str,
        agent_response: str,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        """Log a complete exchange between user and agent.

        Args:
            user_message: The user's input message
            agent_response: The agent's response
            metadata: Optional metadata about the exchange
        """
        self.log_message("user", user_message, metadata)
        self.log_message("agent", agent_response, metadata)

    def get_log_path(self) -> Path:
        """Get the path to the current log file.

        Returns:
            Path object pointing to the log file
        """
        return self.log_file

    def read_history(self) -> list[dict[str, Any]]:
        """Read and parse the chat history from the log file.

        Returns:
            List of chat message dictionaries
        """
        if not self.log_file.exists():
            return []

        with self.log_file.open(encoding="utf-8") as f:
            return [json.loads(line) for line in f if line.strip()]
