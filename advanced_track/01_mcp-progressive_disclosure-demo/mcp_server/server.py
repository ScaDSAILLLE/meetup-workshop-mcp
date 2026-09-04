"""Zentraler FastMCP-Server mit dem simulierten Workshop-Toolkatalog.

Das Backend bindet diese Instanz per In-Memory-Transport ein. Die Importe
registrieren Wetter-, Kunden-, Bestell-, Finanz- und Ablenkungs-Tools.
"""

from fastmcp import FastMCP

mcp = FastMCP("Progressive Disclosure Demo")

from mcp_server.tools import customers, dummy, finance, orders, weather  # noqa: E402, F401
