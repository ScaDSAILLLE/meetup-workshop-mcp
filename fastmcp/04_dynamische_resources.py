#!/usr/bin/env python3
"""
FastMCP Workshop - Teil 4: Dynamische Resources mit Templates
=============================================================

Lernziel: Resource Templates verstehen - parametrisierte Resources

Was sind Resource Templates?
- Resources mit Parametern in der URI: "users://{user_id}/profile"
- Der Parameter wird automatisch an die Funktion übergeben
- Ermöglichen flexible, dynamische Datenabfrage
- Perfekt für strukturierte Daten wie Notizen, Kontakte, etc.

Heute bauen wir ein flexibles Notizen-System!
"""

from fastmcp import FastMCP
from datetime import datetime
import json

# Server für Notizen-Management
mcp = FastMCP(
    name="NotizenAssistent",
    instructions="Dieser Server verwaltet persönliche Notizen und Kategorien."
)

# Simulierte Notizen-Datenbank
NOTIZEN = {
    "arbeit": [
        {"id": 1, "titel": "Meeting Vorbereitung", "inhalt": "Agenda für Montag erstellen", "datum": "2025-09-11"},
        {"id": 2, "titel": "Code Review", "inhalt": "Pull Request #123 reviewen", "datum": "2025-09-10"}
    ],
    "privat": [
        {"id": 3, "titel": "Einkaufsliste", "inhalt": "Milch, Brot, Äpfel", "datum": "2025-09-11"},
        {"id": 4, "titel": "Geschenk für Anna", "inhalt": "Buch über Python suchen", "datum": "2025-09-09"}
    ],
    "lernen": [
        {"id": 5, "titel": "FastMCP Tutorial", "inhalt": "Workshop Materialien erstellen", "datum": "2025-09-11"}
    ]
}

KONTAKTE = {
    "anna": {"name": "Anna Schmidt", "telefon": "0123-456789", "email": "anna@example.com", "relation": "Kollegin"},
    "max": {"name": "Max Weber", "telefon": "0987-654321", "email": "max@example.com", "relation": "Freund"},
    "mama": {"name": "Elisabeth Müller", "telefon": "0555-123456", "email": "eli@example.com", "relation": "Familie"}
}

# Resource Templates - mit Parametern!
@mcp.resource("notizen://{kategorie}")
def hole_notizen_kategorie(kategorie: str) -> list:
    """Holt alle Notizen einer bestimmten Kategorie.
    
    Args:
        kategorie: Die Kategorie (arbeit, privat, lernen)
    """
    if kategorie not in NOTIZEN:
        return []
    return NOTIZEN[kategorie]

@mcp.resource("notizen://{kategorie}/{notiz_id}")
def hole_einzelne_notiz(kategorie: str, notiz_id: str) -> dict:
    """Holt eine spezifische Notiz.
    
    Args:
        kategorie: Die Kategorie 
        notiz_id: Die ID der Notiz
    """
    try:
        notiz_id_int = int(notiz_id)
        notizen = NOTIZEN.get(kategorie, [])
        for notiz in notizen:
            if notiz["id"] == notiz_id_int:
                return notiz
        return {"fehler": f"Notiz {notiz_id} in Kategorie {kategorie} nicht gefunden"}
    except ValueError:
        return {"fehler": "Ungültige Notiz-ID"}

@mcp.resource("kontakte://{name}")
def hole_kontakt(name: str) -> dict:
    """Holt Kontaktinformationen für eine Person.
    
    Args:
        name: Der Name oder Spitzname der Person
    """
    name_lower = name.lower()
    if name_lower in KONTAKTE:
        return KONTAKTE[name_lower]
    return {"fehler": f"Kontakt '{name}' nicht gefunden"}

# Statische Resources für Übersichten
@mcp.resource("data://kategorien")
def hole_kategorien() -> list:
    """Listet alle verfügbaren Notiz-Kategorien auf."""
    return list(NOTIZEN.keys())

@mcp.resource("data://kontakte")
def hole_alle_kontakte() -> list:
    """Listet alle verfügbaren Kontakte auf."""
    return list(KONTAKTE.keys())

# Tools die mit Templates arbeiten
@mcp.tool
def suche_notizen(suchbegriff: str) -> list:
    """Sucht in allen Notizen nach einem Begriff.
    
    Args:
        suchbegriff: Der zu suchende Text
    """
    gefundene_notizen = []
    for kategorie, notizen in NOTIZEN.items():
        for notiz in notizen:
            if (suchbegriff.lower() in notiz["titel"].lower() or 
                suchbegriff.lower() in notiz["inhalt"].lower()):
                notiz_mit_kategorie = notiz.copy()
                notiz_mit_kategorie["kategorie"] = kategorie
                gefundene_notizen.append(notiz_mit_kategorie)
    
    return gefundene_notizen

@mcp.tool
def neue_notiz(kategorie: str, titel: str, inhalt: str) -> str:
    """Erstellt eine neue Notiz in der angegebenen Kategorie.
    
    Args:
        kategorie: Die Kategorie für die Notiz
        titel: Der Titel der Notiz
        inhalt: Der Inhalt der Notiz
    """
    if kategorie not in NOTIZEN:
        NOTIZEN[kategorie] = []
    
    neue_id = max([notiz["id"] for notizen in NOTIZEN.values() for notiz in notizen], default=0) + 1
    
    neue_notiz_obj = {
        "id": neue_id,
        "titel": titel,
        "inhalt": inhalt,
        "datum": datetime.now().strftime("%Y-%m-%d")
    }
    
    NOTIZEN[kategorie].append(neue_notiz_obj)
    return f"✅ Notiz '{titel}' in Kategorie '{kategorie}' erstellt (ID: {neue_id})"

if __name__ == "__main__":
    mcp.run()
    
    print("\n🎯 Was haben wir gelernt?")
    print("- Resource Templates verwenden {parameter} in URIs")
    print("- Parameter werden automatisch an Funktionen übergeben")
    print("- Templates ermöglichen strukturierten Datenzugriff")
    print("- Kombination aus statischen und dynamischen Resources")
    
    print("\n🔍 Probiere aus:")
    print("- Erstelle ein Template für 'termine://{datum}'")
    print("- Baue ein Tool, das alle Templates auflistet")
    print("- Füge Parameter-Validierung hinzu")
    
    print("\n➡️  Weiter mit: 05_intelligente_prompts.py")