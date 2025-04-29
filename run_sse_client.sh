#!/bin/bash

# Script to ensure the virtual environment is set up and run the SSE MCP client script

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Define paths relative to the script directory
VENV_DIR="$SCRIPT_DIR/venv"
VENV_PYTHON="$VENV_DIR/bin/python"

# Check if virtual environment Python exists
if [ ! -x "$VENV_PYTHON" ]; then
    echo "Error: Virtual environment Python not found or not executable at $VENV_PYTHON" >&2
    echo "Please run setup: python3 -m venv venv" >&2
    exit 1
fi

# Ensure MCP and httpx packages are installed within the venv
echo "Ensuring MCP and httpx packages are installed in $VENV_DIR..."
"$VENV_PYTHON" -m pip install -q mcp httpx
if [ $? -ne 0 ]; then
    echo "Error: Failed to install required client packages using $VENV_PYTHON." >&2
    echo "Please check your internet connection and pip configuration." >&2
    exit 1
fi

# Define the path to the SSE client script
CLIENT_SCRIPT="$SCRIPT_DIR/file_reader_sse_client.py"

# Check if the client script exists
if [ ! -f "$CLIENT_SCRIPT" ]; then
    echo "Error: SSE client script not found at $CLIENT_SCRIPT" >&2
    exit 1
fi

# Run the SSE client using the explicit python from the virtual environment
# Pass any arguments given to this script ($@) along to the python script
echo "Running SSE client ($CLIENT_SCRIPT) using $VENV_PYTHON..."
"$VENV_PYTHON" "$CLIENT_SCRIPT" "$@" 