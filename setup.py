"""Setup script for bedrock-agent-chat."""
from setuptools import find_packages, setup

setup(
    name="bedrock-agent-chat",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.9",
    install_requires=[
        "boto3>=1.28.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.11.0",
            "ruff>=0.1.0",
            "bandit>=1.7.5",
            "mypy>=1.5.0",
            "boto3-stubs[bedrock-agent-runtime]>=1.28.0",
        ],
    },
)
