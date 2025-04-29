# Understanding the MCP File Reader SSE Server for Cursor

This document provides a detailed explanation of the **SSE version** (`file-reader-sse`) of the MCP server, how it differs from the stdio version, and the critical configuration points to ensure it works reliably when run independently.

## 1. Core Functionality: `file_reader_server_sse.py`

- **Framework:** Still built using the `mcp` Python library (`FastMCP`).
- **Server Definition:** `mcp = FastMCP("file-reader-sse")` creates the server instance. The name `"file-reader-sse"` is crucial – it's the identifier used for discovery via the project's `.mcp.json` and when calling from clients.
- **Data Directory:** `ROOT_DIR = os.path.join(SCRIPT_DIR, "project_mcp_data_sse")` defines where the server looks for files. It uses a directory **within the project folder** (`./project_mcp_data_sse`) to make the project self-contained. The `start_sse.sh` script ensures this directory exists.
- **Tool Definition (`@mcp.tool()`):** The `@mcp.tool()` decorator above the `read_file` function works the same way, registering it as an available action.
- **`read_file` Function:** Functionality is the same (reads file, basic security, error handling), but it operates on the `./project_mcp_data_sse` directory.
- **Logging:** Still uses Python's `logging` module configured to output messages to `stderr`. When running via `./start_sse.sh`, these logs appear directly in your terminal.
- **No `mcp.run()` or `if __name__ == "__main__":`:** The script **only defines** the `mcp = FastMCP(...)` instance and its tools. It **does not** call `mcp.run()`. The server is started externally using an ASGI server like Uvicorn, which loads the `mcp` object from this file.

## 2. Independent Execution: `start_sse.sh`

This script is the **required** way to run the SSE server. It handles several key steps:

1.  **Finds Paths:** Determines the location of the script itself, the virtual environment (`venv`), and the Python executable within it.
2.  **Creates Data Directory:** Ensures `./project_mcp_data_sse` exists.
3.  **Installs Dependencies:** Uses the venv's Python (`./venv/bin/python -m pip install ...`) to ensure both `mcp` and `uvicorn[standard]` are installed within the virtual environment.
4.  **Runs Uvicorn:** Executes the Uvicorn ASGI server using the venv's Python.
    - `uvicorn --host 127.0.0.1 --port 8080 file_reader_server_sse:mcp`
    - `--host 127.0.0.1`: Tells Uvicorn to listen only on the local machine.
    - `--port 8080`: Tells Uvicorn to listen on port 8080.
    - `file_reader_server_sse:mcp`: Tells Uvicorn to load the ASGI application object named `mcp` from the file `file_reader_server_sse.py`.

**Key Point:** The SSE server runs as an independent network service, managed by Uvicorn, **not** by Cursor's MCP settings toggle.

## 3. Client Discovery: Project `.mcp.json`

This file, located within the project directory, advertises the running SSE server to potential clients:

```json
{
  "mcpServers": {
    "file-reader-sse": {
      // <-- KEY: Must EXACTLY match FastMCP("file-reader-sse")
      "type": "sse", // <-- Indicates Server-Sent Events protocol
      "url": "http://127.0.0.1:8080", // <-- URL where server listens
      "description": "Reads files from ./project_mcp_data_sse via SSE/HTTP (Runs Independently)",
      "tools": [ ... schema ... ] // <-- Describes available tools
    }
  }
}
```

**How Clients Use This (Potentially Cursor):**

- A client (like Cursor, if it implements this feature) could scan the open project for `.mcp.json`.
- It sees the `file-reader-sse` entry with `type: "sse"`.
- When asked to `using mcp file-reader-sse ...`, it knows to connect to the specified `url` (`http://127.0.0.1:8080`) using the SSE protocol, instead of trying to manage a process via stdio.

**Note:** This `.mcp.json` is **distinct** from the global `~/.cursor/mcp.json` used for Cursor-managed _stdio_ servers.

## 4. Virtual Environment (`venv`)

- **Purpose:** Same as before - isolates dependencies.
- **Requirement:** `mcp` and `uvicorn[standard]` must be installed here. The `start_sse.sh` script handles this.
- **Execution:** The `start_sse.sh` script explicitly uses the Python interpreter from this `venv` to run both `pip` and `uvicorn`.

## 5. Testing Client: `file_reader_sse_client.py`

- Provides a way to test the running SSE server manually.
- Connects directly to the URL (`http://127.0.0.1:8080`).
- Invokes the `read_file` tool on the `file-reader-sse` server instance.
- Run using `python file_reader_sse_client.py [filename]` (defaults to `sse_test.txt`).

## 6. Ensuring it Works (Checklist for SSE)

To run the SSE server correctly:

1.  **Dependencies:** Ensure `mcp` and `uvicorn[standard]` are installable (the script tries this).
2.  **Server Name:** Verify the name in `FastMCP("...")` in `file_reader_server_sse.py` **exactly** matches the key in the project `.mcp.json` (`"file-reader-sse"`).
3.  **Run Script:** Use `./start_sse.sh` to start the server. Do **not** try to run `file_reader_server_sse.py` directly without Uvicorn, and do **not** try to manage it via Cursor settings.
4.  **Check Uvicorn Output:** Confirm the terminal running `./start_sse.sh` shows Uvicorn started successfully and is listening on `http://127.0.0.1:8080`.
5.  **Data File:** Ensure the test file (`sse_test.txt`) exists in `./project_mcp_data_sse`.
6.  **Client Connection:** Test using the `file_reader_sse_client.py` or try the command in Cursor (`using mcp file-reader-sse ...`) assuming discovery works.
7.  **Check Logs:** Monitor the terminal output from `./start_sse.sh` for any runtime errors from the server or Uvicorn.

By following these steps, the SSE server runs independently and correctly, ready for clients to connect via its network address.
