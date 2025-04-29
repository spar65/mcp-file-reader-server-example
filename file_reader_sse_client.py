import sys
import asyncio
from contextlib import AsyncExitStack

# Import the specific SSE client factory and Session handler
from mcp.client.sse import sse_client
from mcp import ClientSession, McpError

# URL where the MCP SSE endpoint is expected
# Even if mounted at root in Starlette, the SSE client usually targets /sse
SERVER_URL = "http://127.0.0.1:8080/sse"

# Name of the server instance (must match FastMCP("...") in the server script)
SERVER_NAME = "file-reader-sse"

# Name of the file to read
FILENAME_TO_READ = sys.argv[1] if len(sys.argv) > 1 else "sse_test.txt"

async def main():
    print(f"Attempting to connect to MCP SSE server '{SERVER_NAME}' at {SERVER_URL}...")
    
    session = None # Define session outside try to ensure it's available in finally
    streams_context = None
    session_context = None

    try:
        # Use AsyncExitStack for cleaner context management
        async with AsyncExitStack() as stack:
            # 1. Establish SSE connection streams
            print(f"Establishing SSE streams to {SERVER_URL}...")
            streams_context = sse_client(url=SERVER_URL) 
            read_stream, write_stream = await stack.enter_async_context(streams_context)
            print("SSE streams established.")

            # 2. Create MCP Session using the streams
            print("Creating MCP ClientSession...")
            session_context = ClientSession(read_stream, write_stream)
            session = await stack.enter_async_context(session_context)
            print("MCP ClientSession created.")

            # 3. Initialize the MCP session
            print("Initializing MCP session...")
            await session.initialize()
            print("MCP session initialized.")

            # Optional: list_tools commented out
            # tools_response = await session.list_tools()
            # available_tools = [t.name for t in tools_response.tools]
            # print(f"Available tools: {available_tools}")
            # No need to check server name here, call_tool uses only tool name

            # 5. Call the specific tool using only its name
            tool_name = "read_file"
            print(f"Calling tool '{tool_name}' with filename='{FILENAME_TO_READ}'...")
            result = await session.call_tool(tool_name, arguments={"filename": FILENAME_TO_READ})

            print("\n--- Server Response (Tool Result) ---")
            # Assuming the result content holds the file data
            print(result.content)
            print("---------------------------------------\n")

    except McpError as e:
        print(f"\nMCP Error: Could not connect or communicate properly.", file=sys.stderr)
        print(f"Please ensure the SSE server (started via ./start_sse.sh) is running at {SERVER_URL}.")
        print(f"Details: {e}", file=sys.stderr)
        sys.exit(1)
    except httpx.ConnectError as e: # Need to import httpx if we catch this specifically
         print(f"\nConnection Error: Failed to connect to {SERVER_URL}.", file=sys.stderr)
         print("Is the server running? Is the URL correct?", file=sys.stderr)
         print(f"Details: {e}", file=sys.stderr)
         sys.exit(1)
    except AttributeError as e:
        # This might happen if the tool name format is wrong or tool doesn't exist
        print(f"\nAttribute Error: Problem accessing tool or method.", file=sys.stderr)
        print(f"Check tool name format used in call_tool().", file=sys.stderr)
        print(f"Details: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    # Need httpx for ConnectError
    try:
        import httpx
    except ImportError:
        print("Error: httpx library not found. Please install it ('pip install httpx').", file=sys.stderr)
        sys.exit(1)
        
    asyncio.run(main()) 