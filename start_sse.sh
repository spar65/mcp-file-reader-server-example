#!/bin/bash

# Script to ensure dependencies and run the SSE MCP server using Uvicorn directly

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Define paths relative to the script directory
VENV_DIR="$SCRIPT_DIR/venv"
VENV_PYTHON="$VENV_DIR/bin/python"
PROJECT_DATA_DIR="$SCRIPT_DIR/project_mcp_data_sse"

# Check if virtual environment Python exists
if [ ! -x "$VENV_PYTHON" ]; then
    echo "Error: Virtual environment Python not found or not executable at $VENV_PYTHON" >&2
    echo "Please run setup: python3 -m venv venv" >&2
    exit 1
fi

# Ensure the project-local data directory exists
echo "Ensuring project data directory exists at $PROJECT_DATA_DIR..."
mkdir -p "$PROJECT_DATA_DIR"
if [ $? -ne 0 ]; then
    echo "Error: Failed to create project data directory $PROJECT_DATA_DIR." >&2
    exit 1
fi

# Ensure MCP, Uvicorn, and Starlette packages are installed within the venv
echo "Ensuring MCP, Uvicorn, and Starlette packages are installed in $VENV_DIR..."
"$VENV_PYTHON" -m pip install -q mcp "uvicorn[standard]" starlette
if [ $? -ne 0 ]; then
    echo "Error: Failed to install required server packages using $VENV_PYTHON." >&2
    echo "Please check your internet connection and pip configuration." >&2
    exit 1
fi

# Define the path to the SSE server script module and the app object
APP_MODULE="file_reader_server_sse:app"

# Set Host and Port for Uvicorn directly
HOST="127.0.0.1"
PORT="8080"

# Run the Uvicorn server directly
echo "Starting Uvicorn server for $APP_MODULE on $HOST:$PORT using $VENV_PYTHON..."
"$VENV_PYTHON" -m uvicorn --host "$HOST" --port "$PORT" "$APP_MODULE"

echo "Uvicorn server finished or was interrupted." 
