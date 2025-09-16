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

# Tools testen (normalerweise macht das der KI-Assistent)
if __name__ == "__main__":
    mcp.run(transport="sse", host="localhost", port=8765)

    print("\n🎯 Was haben wir gelernt?")
    print("- @mcp.tool macht aus Funktionen MCP Tools")
    print("- Type Hints (: float, : str) sind wichtig")
    print("- Docstrings erklären dem KI-Assistenten, was das Tool macht")
    print("- Tools können getestet werden wie normale Funktionen")
    
    print("\n🔍 Probiere aus:")
    print("- Erstelle ein Tool zum Multiplizieren")
    print("- Erstelle ein Tool, das die aktuelle Zeit zurückgibt")
    
    print("\n➡️  Weiter mit: 03_persönliche_daten.py")