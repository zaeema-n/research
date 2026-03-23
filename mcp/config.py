"""
Configuration for the OpenGIN MCP server.
All settings are read from environment variables (optionally loaded from .env).
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Base URL of the OpenGIN Read API, e.g. http://localhost:8081/v1
OPENGIN_READ_API_URL: str = os.environ.get(
    "OPENGIN_READ_API_URL", "http://localhost:8081/v1"
).rstrip("/")

# HTTP request timeout in seconds
try:
    REQUEST_TIMEOUT: int = int(os.environ.get("OPENGIN_REQUEST_TIMEOUT", "30"))
except ValueError:
    REQUEST_TIMEOUT: int = 30 # Fallback to default
