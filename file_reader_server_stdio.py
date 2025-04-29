from mcp.server.fastmcp import FastMCP
import os
import logging
import sys

# Set up logging to console (stderr)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stderr  # Log to stderr instead of a file
)
logger = logging.getLogger(__name__)

# Create MCP server instance with consistent name (file-reader with hyphen)
mcp = FastMCP("file-reader")

# Define the root directory for files - use more flexible path
ROOT_DIR = os.path.expanduser("~/mcp_data")
if not os.path.exists(ROOT_DIR):
    try:
        os.makedirs(ROOT_DIR)
        logger.info(f"Created data directory at {ROOT_DIR}")
    except Exception as e:
        logger.error(f"Failed to create data directory {ROOT_DIR}: {e}", exc_info=True)
        # Optionally exit if the data directory is critical
        # sys.exit(1)

logger.info(f"Using data directory: {ROOT_DIR}")

@mcp.tool()
def read_file(filename: str) -> str:
    """
    Read the contents of a file from the mcp_data directory.
    
    Args:
        filename: Name of the file to read (must be in ~/mcp_data directory)
    
    Returns:
        The contents of the file as a string
    """
    logger.info(f"Attempting to read file: {filename}")
    # Basic security check to prevent path traversal
    if '..' in filename or filename.startswith('/'):
        error_msg = f"Invalid filename: {filename}"
        logger.error(error_msg)
        return error_msg
        
    file_path = os.path.join(ROOT_DIR, filename)
    logger.info(f"Reading from absolute path: {file_path}")
    try:
        with open(file_path, "r") as f:
            content = f.read()
        logger.info(f"Successfully read file: {filename}")
        return content
    except FileNotFoundError:
        error_msg = f"File not found: {file_path}"
        logger.error(error_msg)
        return error_msg
    except PermissionError:
        error_msg = f"Permission denied when trying to read: {file_path}"
        logger.error(error_msg)
        return error_msg
    except Exception as e:
        error_msg = f"Error reading file {file_path}: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return error_msg

if __name__ == "__main__":
    try:
        logger.info(f"Starting File Reader MCP Server (stdio) with data directory: {ROOT_DIR}")
        logger.info("Server starting with stdio transport for Cursor management...")
        # Use stdio transport
        mcp.run(transport="stdio")
        logger.info("Server finished running.")
    except Exception as e:
        logger.error("Server (stdio) failed to start or crashed.", exc_info=True)
        sys.exit(1)
