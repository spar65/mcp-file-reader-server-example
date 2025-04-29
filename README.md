# MCP File Reader Server

A simple MCP (Model-Control-Protocol) server for Cursor that allows reading files from a dedicated directory.

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
   ```

### 3. Configuration

#### Configure Cursor

The MCP configuration file needs to be placed in your Cursor application settings directory:

- **macOS**: `~/Library/Application Support/Cursor/cursor_mcp_config.json`
- **Windows**: `%APPDATA%\Cursor\cursor_mcp_config.json`
- **Linux**: `~/.config/Cursor/cursor_mcp_config.json`

This repository already includes a `cursor_mcp_config.json` file. You may need to update the file paths to match your system.

```json
{
  "mcpServers": {
    "file-reader": {
      "command": "/FULL/PATH/TO/YOUR/PROJECT/venv/bin/python",
      "args": [
        "/FULL/PATH/TO/YOUR/PROJECT/mcp-file-reader-example/file_reader_server.py"
      ],
      "env": {}
    }
  }
}
```

#### Data Directory

By default, the server uses `~/mcp_data` as the directory for storing files. Make sure this directory exists or the server will create it for you.

### 4. Running the Server

1. Use the provided start script:

   ```
   ./start.sh
   ```

   Or manually run:

   ```
   source venv/bin/activate
   python file_reader_server.py
   ```

2. The server will start and listen for requests from Cursor.

### 5. Using the Server in Cursor

Once the server is running, you can access it from Cursor by typing:

```
read test.txt using the file-reader server
```

or

```
using mcp file-reader tell me what is in test.txt
```

## Troubleshooting

- Make sure the server is running when you try to access it from Cursor
- Check the `server.log` file for any error messages
- Verify that your configuration file paths are correct
- Restart Cursor after making changes to the configuration files

## Advanced Usage

- The server logs all operations to `server.log` in the server directory
- You can modify the `file_reader_server.py` file to add more functionality

## License

MIT
