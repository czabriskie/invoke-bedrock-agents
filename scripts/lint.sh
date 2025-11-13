#!/bin/bash
# Script to run all linting and type checking tools

set -e

echo "Running ruff format check..."
ruff format --check .

echo ""
echo "Running ruff lint..."
ruff check .

echo ""
echo "Running mypy type checking..."
mypy src/

echo ""
echo "Running bandit security checks..."
bandit -r src/ -c pyproject.toml

echo ""
echo "✅ All linting checks passed!"
