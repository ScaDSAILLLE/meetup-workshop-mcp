# 00_greeting_mcp.py
from fastmcp import FastMCP

mcp = FastMCP("greeting-sse")

@mcp.tool
def greet(name: str) -> str:
    "Return a short greeting."
    return f"Hello, {name}!"

if __name__ == "__main__":
    # HTTP-Transport (Netzwerk)
    mcp.run(transport="sse", host="localhost", port=8764)
