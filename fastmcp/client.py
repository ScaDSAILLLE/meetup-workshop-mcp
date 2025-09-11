import asyncio
from fastmcp import Client, FastMCP


# Local Python script
client = Client("02_erste_funktion.py")

async def main():
    async with client:
        # Basic server interaction
        await client.ping()
        
        # List available operations
        tools = await client.list_tools()
        resources = await client.list_resources()
        prompts = await client.list_prompts()
        
        # Execute operations
        result = await client.call_tool("begrüße", {"name": "Thorsten"})
        print(result)

asyncio.run(main())