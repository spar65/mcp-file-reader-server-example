# MCP File Reader Server

This project provides a simple MCP (Model-Control-Protocol) server for reading files, runnable in two modes:

1.  **Stdio Mode (`file-reader`):** Managed by Cursor via global config.
2.  **SSE Mode (`file-reader-sse`):** Runs independently via manual start.

## Setup Instructions

### 1. Prerequisites

- Python 3.8 or higher
- Cursor app installed
- pip package manager

### 2. Installation

1. Clone or download this repository
2. Create a virtual environment:
   ```
   python3 -m venv venv
   ```
3. Activate the virtual environment:
   ```
   source venv/bin/activate  # On macOS/Linux
   venv\Scripts\activate  # On Windows
   ```
4. Install the required packages:
   ```
   pip install mcp
   # Uvicorn & Starlette are needed for running the SSE server
   # httpx is needed for the SSE client
   pip install "uvicorn[standard]" starlette httpx
   ```

### 3. Configuration

#### Option 1: Configure Cursor for Stdio Mode (`file-reader`)

To let Cursor manage the `stdio` server:

1.  Edit your global MCP config file:
    - **macOS**: `~/Library/Application Support/Cursor/cursor_mcp_config.json`
    - **Windows**: `%APPDATA%\Cursor\cursor_mcp_config.json`
    - **Linux**: `~/.config/Cursor/cursor_mcp_config.json`
2.  Ensure an entry exists for `file-reader`, pointing to the correct venv Python and the main `file_reader_server.py` script:
    ```json
    {
      "mcpServers": {
        "file-reader": {
          // Server name for stdio mode
          "command": "/FULL/PATH/TO/YOUR/PROJECT/venv/bin/python",
          "args": [
            "/FULL/PATH/TO/YOUR/PROJECT/mcp-file-reader-example/file_reader_server.py"
          ],
          "enabled": true,
          "env": {}
        }
        // ... other servers ...
      }
    }
    ```
3.  _(See `cursor_mcp_config.json` in this repo for a template)_

#### Option 2: Configure Project for SSE Discovery (`file-reader-sse`)

The project-local `.mcp.json` file is already configured to describe the SSE server (`file-reader-sse`) running at `http://127.0.0.1:8080`. Note that the client will likely need to connect to the `/sse` subpath (`http://127.0.0.1:8080/sse`).

#### Data Directory

- The **stdio** server (`file-reader`) uses `~/mcp_data` by default (in your home directory).
- The **SSE** server (`file-reader-sse`) uses `./project_mcp_data_sse` by default (within this project directory).

Make sure these directories exist before running the respective servers. The `./start_sse.sh` script will create `./project_mcp_data_sse` if it's missing.

### 4. Running the Server

Choose **one** method:

#### Method A: Stdio Mode (`file-reader` via Cursor)

1.  Complete the global configuration (Option 1 above).
2.  Restart Cursor.
3.  Go to Cursor Settings -> MCP.
4.  Find `file-reader` and toggle it ON.

#### Method B: SSE Mode (`file-reader-sse` Manually)

Use the provided start script. In your terminal:

```bash
./start_sse.sh
```

This script ensures dependencies (including `uvicorn`, `starlette`) are installed and runs the Uvicorn ASGI server, loading the Starlette `app` defined in `file_reader_server_sse.py`. The Starlette app mounts the MCP server's SSE handler (`mcp.sse_app()`) at the root path.

The server will start listening on `http://127.0.0.1:8080`.

### 5. Using the Server in Cursor

- **If using Stdio Mode (Method A):**
  Reads from `~/mcp_data`:
  ```
  read test.txt using the file-reader server
  ```
- **If using SSE Mode (Method B):**
  Assuming Cursor discovers the server via `.mcp.json`. Reads from `./project_mcp_data_sse`:
  ```
  read sse_test.txt using the file-reader-sse server
  ```
  _(Note: Use the specific server name `file-reader-sse` and a filename expected in `./project_mcp_data_sse`)_

### 6. Using the SSE Client Script (Manual Testing)

This project includes a Python client script (`file_reader_sse_client.py`) and a wrapper shell script (`run_sse_client.sh`) to test the SSE server independently using the `mcp` library's SSE client capabilities.

1.  **Ensure the SSE server is running (use `./start_sse.sh`).**
2.  Run the client wrapper script in your terminal:

    ```bash
    # Connects, initializes, lists tools, and calls read_file for sse_test.txt
    ./run_sse_client.sh

    # Tries to read a different file (e.g., another_sse.txt)
    ./run_sse_client.sh another_sse.txt
    ```

    _(The wrapper script ensures dependencies like `httpx` are installed and uses the correct Python.)_

3.  The client will connect to `http://127.0.0.1:8080/sse`, initialize the MCP session, call the `read_file` tool by name, and print the response or any errors.

## Troubleshooting

- **Stdio:** Check Cursor Settings -> MCP for status (green dot), verify global config paths, check `stderr` via Cursor logs if startup fails.
- **SSE:** Ensure the server is running manually (use `./start_sse.sh`), check its terminal output (`stderr`) for errors, verify the client can reach `http://127.0.0.1:8080/sse`.
- Restart Cursor after config changes.

## Advanced Usage

- The `stdio` server uses `file_reader_server.py`.
- The `sse` server uses `file_reader_server_sse.py`.
- Logging is to `stderr` for both.
- A basic client for the SSE server is provided in `file_reader_sse_client.py`.
- A startup script for the SSE server is provided: `start_sse.sh`.
- The SSE server uses Starlette to mount the MCP SSE application (`mcp.sse_app()`) which is then run by Uvicorn via `start_sse.sh`.
- A wrapper script for the SSE client is provided: `run_sse_client.sh`.
- The SSE client script uses `mcp.client.sse.sse_client` and `mcp.ClientSession` to interact with the server.

## License

MIT

## Server Details

- **`file-reader` (Stdio):**
  - Script: `file_reader_server.py`
  - Transport: Stdio
  - Management: Via Cursor global config (`~/.cursor/mcp.json`) & Settings toggle.
  - Rules: `00-MCP-Server-Rules.txt`, `00-MCP-Client-Rules.txt`
  - Data Dir: `~/mcp_data`
- **`file-reader-sse` (SSE):**
  - Script: `file_reader_server_sse.py` (defines FastMCP instance and Starlette app)
  - Transport: SSE via Starlette/Uvicorn (listens on `http://127.0.0.1:8080`, client connects to `/sse` path)
  - Management: Manual start/stop via `start_sse.sh` (runs `uvicorn ...:app`).
  - Discovery: Via project `.mcp.json`.
  - Rules: `00-MCP-SSE-Server-Rule.txt`, `00-MCP-SSE-Client-Rule.txt`
  - Data Dir: `./project_mcp_data_sse` (relative to project root)
