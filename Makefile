.PHONY: help install install-dev test test-all lint format clean run

help:  ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## Install the package
	pip install -e .

install-dev:  ## Install the package with development dependencies
	pip install boto3 python-dotenv pytest pytest-cov pytest-mock ruff bandit mypy 'boto3-stubs[bedrock-agent-runtime]'

test:  ## Run unit tests only
	PYTHONPATH=$(shell pwd)/src pytest tests/ -m "not integration" --cov=src --cov-report=term-missing

test-all:  ## Run all tests including integration tests
	PYTHONPATH=$(shell pwd)/src pytest tests/ --cov=src --cov-report=term-missing --cov-report=html

test-integration:  ## Run integration tests only
	PYTHONPATH=$(shell pwd)/src pytest tests/ -m integration

lint:  ## Run all linting checks
	ruff format --check .
	ruff check .
	mypy src/
	bandit -r src/ -c pyproject.toml

format:  ## Auto-format code
	ruff format .
	ruff check --fix .

clean:  ## Clean up generated files
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete

run:  ## Run the chat application
	PYTHONPATH=$(shell pwd)/src python -m chat_app

setup:  ## Initial setup (create venv, install deps, copy env file)
	python -m venv venv
	@echo "Virtual environment created. Run 'source venv/bin/activate' to activate it."
	@echo "Then run 'make install-dev' to install dependencies."
	@if [ ! -f .env ]; then cp .env.example .env; echo "Created .env file from .env.example"; fi
