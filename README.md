# Bedrock Agent Chat Application

[![CI](https://github.com/czabriskie/invoke-bedrock-agents/actions/workflows/ci.yml/badge.svg)](https://github.com/czabriskie/invoke-bedrock-agents/actions/workflows/ci.yml)

A simple, interactive command-line chat application for AWS Bedrock agents with automatic chat history logging, comprehensive testing, and code quality checks.

## Features

- 🤖 **Interactive Chat**: Simple CLI interface for conversing with AWS Bedrock agents
- 📝 **Automatic Logging**: All conversations are automatically logged with timestamps
- 🔄 **Session Management**: Support for multiple chat sessions with context preservation
- ✅ **Well Tested**: Comprehensive unit and integration tests
- 🔍 **Code Quality**: Linting with ruff, type checking with mypy, security scanning with bandit
- 🚀 **CI/CD Ready**: GitHub Actions workflow for automated testing and linting

## Prerequisites

- Python 3.9 or higher
- AWS credentials configured (via AWS CLI or environment variables)
- Access to an AWS Bedrock agent

## Installation

1. Clone the repository:
```bash
git clone https://github.com/czabriskie/invoke-bedrock-agents.git
cd invoke-bedrock-agents
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the package with development dependencies:
```bash
pip install -e ".[dev]"
```

## Configuration

Create a `.env` file in the project root (copy from `.env.example`):

```bash
# Your Bedrock agent configuration
BEDROCK_AGENT_ARN=arn:aws:bedrock:us-west-2:123456789:agent/KYXJLSSOTU
# OR
BEDROCK_AGENT_ID=KYXJLSSOTU
BEDROCK_AGENT_ALIAS_ID=TSTALIASID

# AWS Configuration (optional if using AWS CLI credentials)
AWS_REGION=us-west-2
AWS_PROFILE=default

# Chat Configuration
CHAT_HISTORY_DIR=./logs
```

### AWS Credentials

The application requires AWS credentials with permissions to invoke Bedrock agents. Configure credentials using one of these methods:

1. **AWS CLI** (recommended):
   ```bash
   aws configure
   ```

2. **Environment Variables**:
   ```bash
   export AWS_ACCESS_KEY_ID=your_access_key
   export AWS_SECRET_ACCESS_KEY=your_secret_key
   export AWS_REGION=us-west-2
   ```

3. **IAM Role** (when running on EC2/ECS)

Required IAM permissions:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeAgent"
      ],
      "Resource": "arn:aws:bedrock:*:*:agent/*"
    }
  ]
}
```

## Usage

### Running the Chat Application

Start the interactive chat:

```bash
python -m src.chat_app
```

### Chat Commands

Once in the chat interface:

- **Type a message** and press Enter to chat with the agent
- **`quit`** or **`exit`**: End the session
- **`new`**: Start a new session (clears context)
- **`history`**: View the current session's chat history

### Example Session

```
======================================================================
AWS Bedrock Agent Chat
======================================================================
Session ID: 3f8b2c1a-4d5e-6f7a-8b9c-0d1e2f3a4b5c
Log file: ./logs/chat_history_20241113_120000_3f8b2c1a.log

Commands:
  - Type your message and press Enter to chat
  - Type 'quit' or 'exit' to end the session
  - Type 'new' to start a new session
  - Type 'history' to view chat history
======================================================================

You: Hello! Can you help me with something?

🤖 Agent is thinking...

Agent: Of course! I'd be happy to help. What do you need assistance with?

You: quit

👋 Goodbye! Chat history saved.
```

## Using as a Library

You can also use the components programmatically:

```python
from src.bedrock_agent_client import BedrockAgentClient
from src.chat_history_logger import ChatHistoryLogger

# Create a client
client = BedrockAgentClient(
    agent_id="KYXJLSSOTU",
    agent_alias_id="TSTALIASID",
    region_name="us-west-2"
)

# Create a logger
logger = ChatHistoryLogger("./logs", client.get_session_id())

# Send a message
response = client.invoke_agent("Hello, how are you?")
print(response["completion"])

# Log the conversation
logger.log_exchange(
    "Hello, how are you?",
    response["completion"],
    {"session_id": response["session_id"]}
)
```

## Development

### Running Tests

Run unit tests (no AWS credentials needed):
```bash
pytest tests/ -m "not integration"
```

Run all tests including integration tests (requires AWS credentials):
```bash
pytest tests/
```

Run tests with coverage:
```bash
pytest tests/ -m "not integration" --cov=src --cov-report=html
```

### Linting and Type Checking

Run all linting checks:
```bash
# Format check
ruff format --check .

# Lint
ruff check .

# Type checking
mypy src/

# Security scanning
bandit -r src/ -c pyproject.toml
```

Or use the convenience script:
```bash
bash scripts/lint.sh
```

### Auto-formatting

Format code automatically:
```bash
ruff format .
```

Fix auto-fixable linting issues:
```bash
ruff check --fix .
```

## Project Structure

```
invoke-bedrock-agents/
├── src/
│   ├── __init__.py
│   ├── bedrock_agent_client.py   # AWS Bedrock agent client
│   ├── chat_history_logger.py    # Chat logging functionality
│   └── chat_app.py                # CLI application
├── tests/
│   ├── __init__.py
│   ├── test_bedrock_agent_client.py
│   ├── test_chat_history_logger.py
│   ├── test_chat_app.py
│   └── test_integration.py        # Integration tests
├── scripts/
│   ├── lint.sh                    # Linting script
│   └── test.sh                    # Testing script
├── .github/
│   └── workflows/
│       └── ci.yml                 # GitHub Actions CI workflow
├── logs/                          # Chat history logs (gitignored)
├── pyproject.toml                 # Project configuration
├── .env.example                   # Environment variables template
├── .gitignore
└── README.md
```

## Chat History Logs

All conversations are automatically logged to `./logs/` (configurable via `CHAT_HISTORY_DIR`).

Log file format:
- Filename: `chat_history_YYYYMMDD_HHMMSS_[session_id].log`
- Format: JSON Lines (one JSON object per line)

Example log entry:
```json
{"timestamp": "2024-11-13T12:00:00.123456+00:00", "role": "user", "content": "Hello!", "metadata": {"session_id": "abc123"}}
{"timestamp": "2024-11-13T12:00:01.234567+00:00", "role": "agent", "content": "Hi there!", "metadata": {"session_id": "abc123"}}
```

## CI/CD

The project includes a GitHub Actions workflow (`.github/workflows/ci.yml`) that runs on every push and pull request:

- **Linting**: ruff format check, ruff lint, mypy, bandit
- **Testing**: Unit tests across Python 3.9, 3.10, 3.11, and 3.12
- **Coverage**: Code coverage reporting

## Troubleshooting

### AWS Credentials Error

If you see `NoCredentialsError` or `AccessDeniedException`:
1. Ensure AWS credentials are configured: `aws configure`
2. Verify credentials have Bedrock agent permissions
3. Check the agent ID and alias are correct

### Module Import Errors

If you see import errors when running the app:
```bash
# Make sure you install in development mode
pip install -e .
```

### Agent Not Responding

1. Verify the agent ARN/ID is correct
2. Check the agent alias ID (usually `TSTALIASID` for test aliases)
3. Ensure the agent is in the correct AWS region
4. Verify the agent is deployed and active in the Bedrock console

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Run linting and tests locally
5. Submit a pull request

Make sure all tests pass and linting checks succeed before submitting.

## Agent ARN

The default agent ARN in this project:
```
arn:aws:bedrock:us-west-2:123456789:agent/KYXJLSSOTU
```

Replace this with your own Bedrock agent ARN in the `.env` file.
