#!/bin/bash
# Script to run tests

set -e

echo "Running unit tests..."
pytest tests/ -m "not integration" --cov=src --cov-report=term-missing

echo ""
echo "✅ All unit tests passed!"
echo ""
echo "To run integration tests (requires AWS credentials):"
echo "  pytest tests/ -m integration"
