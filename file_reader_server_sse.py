import os
import logging
import sys
from mcp.server.fastmcp import FastMCP
# Import Starlette components
from starlette.applications import Starlette
from starlette.routing import Mount

# Set up logging to console (stderr)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

# Create MCP server instance with SSE-specific name
mcp = FastMCP("file-reader-sse")

# Define the root directory for files relative to the script's location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.join(SCRIPT_DIR, "project_mcp_data_sse")

# Create the directory if it doesn't exist (server-side check)
if not os.path.exists(ROOT_DIR):
    try:
        os.makedirs(ROOT_DIR)
        logger.info(f"Created data directory at {ROOT_DIR}")
    except Exception as e:
        logger.error(f"Failed to create data directory {ROOT_DIR}: {e}", exc_info=True)
        # Let Starlette/Uvicorn handle startup failure

logger.info(f"Using data directory: {ROOT_DIR}")

# --- Define MCP Tools --- 
@mcp.tool()
def read_file(filename: str) -> str:
    """
    Read the contents of a file from the project_mcp_data_sse directory.
    
    Args:
        filename: Name of the file to read (must be in ./project_mcp_data_sse directory)
    
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

# --- Create Starlette App and Mount MCP SSE Handler ---
# This 'app' object is what Uvicorn will run
app = Starlette(routes=[
    Mount('/', app=mcp.sse_app()) # Mount the MCP SSE handler at the root
])

logger.info(f"Starlette app 'app' created, mounting MCP SSE app from '{mcp.name}' at root '/'.")

# Note: No if __name__ == "__main__" needed as Uvicorn loads 'app' directly
