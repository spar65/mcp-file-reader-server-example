# Understanding the MCP File Reader Server for Cursor

This document provides a detailed explanation of the `file-reader` MCP server, how it integrates with Cursor, and the critical configuration points to ensure it works reliably.

## 1. Core Functionality: `file_reader_server.py`

- **Framework:** The server is built using the `mcp` Python library, specifically the `FastMCP` class. This class simplifies creating MCP servers by handling protocol details.
- **Server Definition:** `mcp = FastMCP("file-reader")` creates the server instance. The name `"file-reader"` is crucial – it's the identifier used in the Cursor configuration.
- **Data Directory:** `ROOT_DIR = os.path.expanduser("~/mcp_data")` defines where the server looks for files. It uses your home directory (`~`) expanded to its full path, ensuring it works consistently. The server creates this directory if it doesn't exist.
- **Tool Definition (`@mcp.tool()`):** The `@mcp.tool()` decorator above the `read_file` function registers it as an available action (a "tool") that MCP clients (like Cursor) can invoke.
- **`read_file` Function:**
  - Takes one argument: `filename` (a string).
  - **Security:** Performs a basic check to prevent reading files outside the intended directory (e.g., using `../` or absolute paths in the `filename` argument).
  - Constructs the full, absolute path by joining `ROOT_DIR` and the provided `filename`.
  - Attempts to open and read the file at the constructed path.
  - **Error Handling:** Includes `try...except` blocks to catch `FileNotFoundError`, `PermissionError`, and other potential exceptions during file access.
  - **Return Value:** Returns the file's content as a string on success, or an informative error message string on failure.
- **Logging:** Uses Python's `logging` module configured to output messages to `stderr` (standard error). This is important because when Cursor runs the server, errors printed to `stderr` are more likely to be captured in Cursor's logs, aiding debugging.
- **Transport Method (`mcp.run(transport="stdio")`):** This is the command that starts the server's main loop. Crucially, `transport="stdio"` tells the server to communicate using standard input and standard output streams. This is the method Cursor expects when it manages the server process via `mcp.json`.
- **Top-Level Error Handling:** The `if __name__ == "__main__":` block includes a `try...except` to catch any critical errors during server startup or execution, logging them to `stderr` before exiting.

## 2. Cursor Integration: `~/.cursor/mcp.json`

This file tells Cursor how to find, start, and manage your MCP servers. The entry for our server is key:

```json
{
  "mcpServers": {
    "file-reader": {
      // <-- KEY: Must EXACTLY match FastMCP("file-reader")
      "command": "/Users/spehargreg/Development/mcp-example/venv/bin/python", // <-- CRITICAL: Absolute path to venv Python
      "enabled": true,
      "args": [
        "/Users/spehargreg/Development/mcp-example/file_reader_server.py"
      ], // <-- CRITICAL: Absolute path to server script
      "env": {}
    }
    // other servers...
  }
}
```

**Critical Configuration Points:**

1.  **Server Name (`"file-reader"`):** This key **MUST** exactly match the name given to `FastMCP()` in the Python script. Any mismatch (like `file_reader` vs `file-reader`) will prevent Cursor from recognizing the server.
2.  **Command (`"command"`):** This specifies the executable Cursor should run. It **MUST** be the _absolute path_ to the Python interpreter _inside your project's virtual environment_ (`venv/bin/python`). Using just `"python"` is unreliable because Cursor might use the system Python, which likely doesn't have the `mcp` package installed.
3.  **Arguments (`"args"`):** This is a list of arguments passed to the command. The first argument **MUST** be the _absolute path_ to your server script (`file_reader_server.py`).
4.  **Enabled (`"enabled"`):** `true` means Cursor will try to start and manage this server.
5.  **Environment (`"env"`):** Usually empty unless your server script _specifically_ needs certain environment variables set.

**How Cursor Uses This:**

- When you toggle the server "on" in Cursor settings, Cursor executes the specified `command` with the given `args`.
- Cursor establishes a connection with the started server process using `stdio`.
- If the server starts successfully and responds correctly to the MCP initialization handshake over `stdio`, the status dot turns green.
- If the server crashes, fails to respond, or uses the wrong transport (like `sse`), the connection fails, and the dot stays red, often with a "Client closed" message.

## 3. Virtual Environment (`venv`)

- **Purpose:** Isolates Python packages (like `mcp`) for this project, preventing conflicts with system-wide packages.
- **Requirement:** The `mcp` library MUST be installed within this `venv` (`pip install mcp`).
- **Cursor Link:** The `command` path in `mcp.json` _must_ point to the `python` executable inside this `venv` so that the server can find the installed `mcp` library when Cursor starts it.

## 4. Ensuring it Works in the Future (Checklist)

To avoid the red dot and connection issues:

1.  **Naming:** Ensure the server name in `FastMCP("...")` **exactly** matches the key in `mcp.json`.
2.  **Transport:** Verify the server code uses `mcp.run(transport="stdio")`.
3.  **`mcp.json` Command Path:** Confirm the `command` is the **absolute path** to `venv/bin/python`.
4.  **`mcp.json` Args Path:** Confirm the first element in `args` is the **absolute path** to `file_reader_server.py`.
5.  **Dependencies:** Ensure the `mcp` package (and any others needed by the server) is installed in the `venv`.
6.  **Management:** **Let Cursor manage the process.** Do _not_ run the server manually if it's enabled in `mcp.json`. Use the toggle in Cursor settings.
7.  **Restart Cursor:** After _any_ change to `~/.cursor/mcp.json`, fully restart the Cursor application.
8.  **Check Logs:** If issues persist, check Cursor's logs for `stderr` output from the server script (thanks to our updated logging).

By following these configuration details, particularly the absolute paths in `mcp.json` and the `stdio` transport, you ensure that Cursor can correctly start, manage, and communicate with your MCP server.
