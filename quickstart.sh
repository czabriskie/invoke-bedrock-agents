#!/bin/bash
# Quick start script for the Bedrock Agent Chat application

set -e

echo "🚀 Bedrock Agent Chat - Quick Start"
echo "===================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install build dependencies first
echo "📥 Installing build tools..."
pip install --quiet --upgrade pip
pip install --quiet setuptools wheel

# Install package dependencies
echo "📥 Installing package dependencies..."
pip install --quiet boto3 python-dotenv pytest pytest-cov pytest-mock ruff bandit mypy 'boto3-stubs[bedrock-agent-runtime]'

# Add src to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file from template..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file and add your Bedrock agent configuration!"
    echo "   Required: BEDROCK_AGENT_ARN or BEDROCK_AGENT_ID"
    echo ""
    read -p "Press Enter to continue after editing .env file..."
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "📝 Quick commands:"
echo "   Run chat:  PYTHONPATH=\$(pwd)/src python -m chat_app"
echo "   Run tests: PYTHONPATH=\$(pwd)/src pytest tests/"
echo "   Run lint:  make lint"
echo ""
echo "🎉 Starting chat application..."
echo ""

PYTHONPATH="$(pwd)/src" python -m chat_app
