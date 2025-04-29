# Understanding the MCP File Reader SSE Server

This document provides a detailed explanation of the **SSE version** (`file-reader-sse`) of the MCP server, how it differs from the stdio version, and the critical configuration points to ensure it works reliably when run independently.

## 1. Core Functionality: `file_reader_server_sse.py`

- **Framework:** Built using `mcp.server.fastmcp.FastMCP`.
- **Server Definition:** `mcp = FastMCP("file-reader-sse")` creates the server instance. The name `"file-reader-sse"` is crucial for discovery and client calls.
- **Data Directory:** Uses `./project_mcp_data_sse` (relative to the script) for portability.
- **Tool Definition:** `@mcp.tool()` registers the `read_file` function.
- **`read_file` Function:** Reads content from the specified file within `./project_mcp_data_sse`.
- **Logging:** Configured to output to `stderr` for visibility when run via the start script.
- **ASGI App:** Instead of `mcp.run()`, the script defines a Starlette application (`app = Starlette(...)`) and mounts the MCP SSE handler using `mcp.sse_app()` at the root path (`/`). This `app` object is what Uvicorn runs.

## 2. Independent Execution: `start_sse.sh`

This script is the **required** way to run the SSE server:

1.  **Finds Paths:** Locates `venv/bin/python`.
2.  **Creates Data Directory:** Ensures `./project_mcp_data_sse` exists.
3.  **Installs Dependencies:** Ensures `mcp`, `uvicorn[standard]`, and `starlette` are installed in the venv.
4.  **Runs Uvicorn:** Executes Uvicorn (`./venv/bin/python -m uvicorn ...`) pointing it to the `app` object within `file_reader_server_sse.py` (`file_reader_server_sse:app`). It binds to `127.0.0.1:8080`.

**Key Point:** The server runs as an independent ASGI application via Uvicorn, **not** managed by Cursor settings.

## 3. Client Discovery: Project `.mcp.json`

- Located in the project root, describes the server for potential discovery.
- `"file-reader-sse"`: Matches the `FastMCP` name.
- `"type": "sse"`: Specifies the protocol.
- `"url": "http://127.0.0.1:8080"`: **Base URL** where the server listens. Clients (like ours or potentially Cursor) need to know to connect to the `/sse` path relative to this base URL (i.e., `http://127.0.0.1:8080/sse`).
- `"tools"`: Includes schema for the `read_file` tool.

**Note:** Distinct from global `~/.cursor/mcp.json`.

## 4. Virtual Environment (`venv`)

- Isolates project dependencies (`mcp`, `uvicorn`, `starlette`, `httpx`).
- `start_sse.sh` and `run_sse_client.sh` ensure packages are installed and use the python from `./venv/bin/python`.

## 5. Testing Client: `file_reader_sse_client.py` & `run_sse_client.sh`

- `file_reader_sse_client.py`:
  - Imports `sse_client` from `mcp.client.sse` and `ClientSession` from `mcp`.
  - Uses `sse_client(url="http://127.0.0.1:8080/sse")` to get connection streams.
  - Passes streams to `ClientSession(...)`.
  - Initializes the session (`await session.initialize()`).
  - Calls the tool using `await session.call_tool("read_file", ...)` (using only the tool name).
- `run_sse_client.sh`:
  - Ensures `mcp` and `httpx` are installed in venv.
  - Runs the client script using the venv python.
  - Passes command-line arguments (like filename) to the python script.

## 6. Ensuring it Works (Checklist for SSE)

1.  **Dependencies:** `mcp`, `uvicorn`, `starlette`, `httpx` must be installed in `venv` (`start_sse.sh` and `run_sse_client.sh` attempt this).
2.  **Server Name:** `FastMCP("file-reader-sse")` matches key in `.mcp.json`.
3.  **Run Server:** Use `./start_sse.sh`.
4.  **Check Server Logs:** Confirm Uvicorn starts, mentions Starlette/`app`, and listens on `127.0.0.1:8080`.
5.  **Data File:** `sse_test.txt` exists in `./project_mcp_data_sse`.
6.  **Run Client:** Use `./run_sse_client.sh`.
7.  **Check Client Output:** Verify connection, initialization, and tool call succeed, printing file content.
8.  **Check Client Logs:** Monitor terminal for errors (connection, MCP, attribute errors).
9.  **URL Path:** Ensure client connects to the `/sse` path (`http://127.0.0.1:8080/sse`).
10. **Tool Name:** Ensure `call_tool` uses only the tool name (`"read_file"`).

Following these steps ensures the Starlette/Uvicorn server hosting the MCP application runs correctly and the client connects using the appropriate library functions.
