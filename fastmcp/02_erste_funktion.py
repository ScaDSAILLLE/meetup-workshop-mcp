#!/usr/bin/env python3
"""
FastMCP Workshop - Teil 2: Erste Funktion hinzufügen
====================================================

Lernziel: Tools (@mcp.tool) verstehen und erstellen

Was sind Tools?
- Funktionen, die der KI-Assistent aufrufen kann
- Werden mit @mcp.tool als Decorator markiert
- Brauchen eine gute Beschreibung (Docstring)
- Können Parameter haben und Werte zurückgeben

Heute erstellen wir unser erstes Tool!
"""

from fastmcp import FastMCP, Client
import asyncio

# Server mit Beschreibung erstellen
mcp = FastMCP(
    name="MeinToolServer",
    instructions="Dieser Server kann einfache Berechnungen durchführen."
)

@mcp.tool
def addiere(a: float, b: float) -> float:
    """Addiert zwei Zahlen zusammen.
    
    Args:
        a: Die erste Zahl
        b: Die zweite Zahl
        
    Returns:
        Die Summe von a und b
    """
    ergebnis = a + b
    print(f"🧮 Berechnung: {a} + {b} = {ergebnis}")
    return ergebnis

@mcp.tool
def begrüße(name: str) -> str:
    """Begrüßt eine Person freundlich.
    
    Args:
        name: Der Name der Person
        
    Returns:
        Eine freundliche Begrüßung
    """
    begrüßung = f"Hallo {name}! Schön dich kennenzulernen! 👋"
    print(f"💬 Begrüßung: {begrüßung}")
    return begrüßung

# # Tools testen (normalerweise macht das der KI-Assistent)
# if __name__ == "__main__":
#     mcp.run()

client = Client(mcp)

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
        # print(result)

asyncio.run(main())