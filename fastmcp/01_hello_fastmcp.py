#!/usr/bin/env python3
"""
FastMCP Workshop - Teil 1: Erste Schritte
==========================================

Lernziel: Verstehen was FastMCP ist und einen ersten Server erstellen

Was ist FastMCP?
- Ein Framework zum Erstellen von MCP (Model Context Protocol) Servern
- Ermöglicht es, eigene Tools für KI-Assistenten zu entwickeln
- Kommuniziert über verschiedene Transporte (STDIO, HTTP, etc.)

In diesem ersten Schritt erstellen wir einen minimalen Server.
"""

from fastmcp import FastMCP

# Schritt 1: Einen einfachen Server erstellen
# Der Name hilft dabei, den Server zu identifizieren
mcp = FastMCP(name="MeinErsterServer")

print("✅ Server erstellt!")
print(f"📝 Server-Name: {mcp.name}")
print("\n🎯 Was haben wir gelernt?")
print("- FastMCP ist ein Framework für MCP Server")
print("- Ein Server braucht mindestens einen Namen")
print("- Der Server ist jetzt bereit, aber hat noch keine Funktionen")

print("\n🔍 Probiere aus:")
print("- Ändere den Server-Namen zu deinem eigenen Namen")
print("- Führe das Skript erneut aus")

if __name__ == "__main__":
    mcp.run(transport="sse", host="localhost", port=8765)
    print("\n🚀 Um den Server zu starten, führe aus:")
    print("python 01_hello_fastmcp.py")
    print("\n➡️  Weiter mit: 02_erste_funktion.py")