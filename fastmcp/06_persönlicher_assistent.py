#!/usr/bin/env python3
"""
FastMCP Workshop - Teil 6: Persönlicher Assistent (Finale)
==========================================================

Lernziel: Alles zusammenführen zu einem vollständigen persönlichen Assistenten

Was haben wir gelernt?
1. FastMCP Server erstellen (Teil 1)
2. Tools für Funktionen (Teil 2) 
3. Resources für Daten (Teil 3)
4. Resource Templates für strukturierte Daten (Teil 4)
5. Prompts für intelligente KI-Interaktion (Teil 5)

Heute: Vollständiger persönlicher Assistent!
"""

from fastmcp import FastMCP
from datetime import datetime, timedelta
import json
import os

# Hauptserver für persönlichen Assistenten
mcp = FastMCP(
    name="PersönlicherAssistent",
    instructions="""
    Ich bin dein persönlicher Assistent und kann dir bei folgenden Aufgaben helfen:
    
    📅 Terminplanung und Kalender-Management
    📝 Notizen-Verwaltung und Suche
    👥 Kontakt-Management
    ✅ Aufgaben-Tracking
    📧 E-Mail und Kommunikation
    🤖 Intelligente Prompts für verschiedene Workflows
    
    Verwende meine Tools und Resources um produktiv zu bleiben!
    """
)

# =============================================================================
# DATEN-LAYER (normalerweise aus Dateien/Datenbank)
# =============================================================================

PERSÖNLICHE_DATEN = {
    "name": "Maria Müller",
    "email": "maria.mueller@example.com", 
    "telefon": "+49 123 456789",
    "beruf": "Software-Entwicklerin",
    "firma": "TechCorp GmbH",
    "wohnort": "München, Deutschland",
    "zeitzone": "Europe/Berlin"
}

TERMINE = [
    {"id": 1, "datum": "2025-09-12", "zeit": "09:00", "titel": "Daily Standup", "ort": "Online", "dauer": 15, "typ": "meeting"},
    {"id": 2, "datum": "2025-09-12", "zeit": "10:30", "titel": "Code Review Session", "ort": "Büro", "dauer": 60, "typ": "arbeit"},
    {"id": 3, "datum": "2025-09-12", "zeit": "14:00", "titel": "Zahnarzt", "ort": "Dr. Weber Praxis", "dauer": 30, "typ": "privat"},
    {"id": 4, "datum": "2025-09-13", "zeit": "09:00", "titel": "FastMCP Workshop", "ort": "Online", "dauer": 180, "typ": "lernen"},
    {"id": 5, "datum": "2025-09-13", "zeit": "15:30", "titel": "Kaffee mit Anna", "ort": "Café Central", "dauer": 45, "typ": "sozial"}
]

AUFGABEN = [
    {"id": 1, "titel": "FastMCP Workshop finalisieren", "beschreibung": "Alle 6 Python-Skripte fertigstellen", "priorität": "hoch", "deadline": "2025-09-12", "status": "in_arbeit", "kategorie": "arbeit"},
    {"id": 2, "titel": "Code Review für PR #156", "beschreibung": "Authentication Module überprüfen", "priorität": "hoch", "deadline": "2025-09-12", "status": "offen", "kategorie": "arbeit"},
    {"id": 3, "titel": "Backup wichtiger Projekte", "beschreibung": "GitHub Repositories und lokale Dateien sichern", "priorität": "mittel", "deadline": "2025-09-15", "status": "offen", "kategorie": "technik"},
    {"id": 4, "titel": "Geburtstagsgeschenk für Tom", "beschreibung": "Etwas Programmier-bezogenes finden", "priorität": "niedrig", "deadline": "2025-09-20", "status": "offen", "kategorie": "privat"}
]

KONTAKTE = {
    "anna": {"name": "Anna Schmidt", "telefon": "+49 987 654321", "email": "anna.schmidt@techcorp.com", "position": "Senior Developer", "firma": "TechCorp GmbH", "relation": "Kollegin"},
    "tom": {"name": "Tom Wagner", "telefon": "+49 555 123456", "email": "tom@example.com", "position": "Product Manager", "firma": "StartupXYZ", "relation": "Freund"},
    "dr_weber": {"name": "Dr. Michael Weber", "telefon": "+49 89 123456", "email": "praxis@weber-dental.de", "position": "Zahnarzt", "firma": "Zahnarztpraxis Weber", "relation": "Arzt"}
}

NOTIZEN = {
    "arbeit": [
        {"id": 1, "titel": "FastMCP Erkenntnisse", "inhalt": "Resource Templates sind sehr mächtig für strukturierte Daten. Unbedingt in nächstem Projekt einsetzen.", "datum": "2025-09-11", "tags": ["fastmcp", "entwicklung"]},
        {"id": 2, "titel": "Team Meeting Notizen", "inhalt": "Neues Feature wird in Sprint 23 entwickelt. Anna übernimmt Frontend, ich Backend-API.", "datum": "2025-09-10", "tags": ["meeting", "sprint"]}
    ],
    "privat": [
        {"id": 3, "titel": "Wochenend-Pläne", "inhalt": "Samstag: Wanderung im Englischen Garten. Sonntag: Programmier-Projekt weiter.", "datum": "2025-09-11", "tags": ["freizeit"]},
        {"id": 4, "titel": "Buchempfehlung", "inhalt": "\"Clean Code\" von Robert C. Martin - perfekt für Tom's Geburtstag!", "datum": "2025-09-09", "tags": ["bücher", "geschenke"]}
    ]
}

# =============================================================================
# RESOURCES - Datenzugriff
# =============================================================================

@mcp.resource("data://profil")
def hole_profil() -> dict:
    """Persönliche Profil-Informationen."""
    return PERSÖNLICHE_DATEN

@mcp.resource("data://termine")
def hole_alle_termine() -> list:
    """Alle geplanten Termine."""
    return TERMINE

@mcp.resource("termine://{datum}")
def hole_termine_datum(datum: str) -> list:
    """Termine für ein bestimmtes Datum (YYYY-MM-DD)."""
    return [t for t in TERMINE if t["datum"] == datum]

@mcp.resource("termine://typ/{typ}")
def hole_termine_typ(typ: str) -> list:
    """Termine nach Typ (meeting, arbeit, privat, lernen, sozial)."""
    return [t for t in TERMINE if t["typ"] == typ]

@mcp.resource("data://aufgaben") 
def hole_alle_aufgaben() -> list:
    """Alle Aufgaben."""
    return AUFGABEN

@mcp.resource("aufgaben://{status}")
def hole_aufgaben_status(status: str) -> list:
    """Aufgaben nach Status (offen, in_arbeit, erledigt)."""
    return [a for a in AUFGABEN if a["status"] == status]

@mcp.resource("aufgaben://priorität/{priorität}")
def hole_aufgaben_priorität(priorität: str) -> list:
    """Aufgaben nach Priorität (hoch, mittel, niedrig)."""
    return [a for a in AUFGABEN if a["priorität"] == priorität]

@mcp.resource("kontakte://{name}")
def hole_kontakt(name: str) -> dict:
    """Kontaktinformationen für eine Person."""
    name_key = name.lower().replace(" ", "_").replace(".", "_")
    return KONTAKTE.get(name_key, {"fehler": f"Kontakt '{name}' nicht gefunden"})

@mcp.resource("notizen://{kategorie}")
def hole_notizen_kategorie(kategorie: str) -> list:
    """Notizen einer bestimmten Kategorie."""
    return NOTIZEN.get(kategorie, [])

# =============================================================================
# TOOLS - Funktionalität 
# =============================================================================

@mcp.tool
def termine_heute() -> list:
    """Zeigt alle Termine für heute an."""
    heute = datetime.now().strftime("%Y-%m-%d")
    termine_heute = hole_termine_datum(heute)
    return termine_heute

@mcp.tool
def nächster_termin() -> dict:
    """Findet den nächsten anstehenden Termin."""
    jetzt = datetime.now()
    heute = jetzt.strftime("%Y-%m-%d")
    aktuelle_zeit = jetzt.strftime("%H:%M")
    
    # Termine heute nach aktueller Zeit
    termine_heute = [t for t in hole_termine_datum(heute) if t["zeit"] >= aktuelle_zeit]
    
    if termine_heute:
        return termine_heute[0]
    
    # Sonst nächster Tag mit Terminen
    for i in range(1, 8):  # Nächste 7 Tage
        tag = (jetzt + timedelta(days=i)).strftime("%Y-%m-%d")
        termine = hole_termine_datum(tag)
        if termine:
            return termine[0]
    
    return {"nachricht": "Keine Termine in den nächsten 7 Tagen"}

@mcp.tool
def dringende_aufgaben() -> list:
    """Zeigt dringende Aufgaben (hohe Priorität oder deadline heute/morgen)."""
    heute = datetime.now().strftime("%Y-%m-%d")
    morgen = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    
    dringende = []
    for aufgabe in AUFGABEN:
        if (aufgabe["priorität"] == "hoch" or 
            aufgabe["deadline"] in [heute, morgen]) and aufgabe["status"] != "erledigt":
            dringende.append(aufgabe)
    
    return dringende

@mcp.tool
def suche_notizen(suchbegriff: str) -> list:
    """Durchsucht alle Notizen nach einem Begriff."""
    gefunden = []
    for kategorie, notizen_liste in NOTIZEN.items():
        for notiz in notizen_liste:
            if (suchbegriff.lower() in notiz["titel"].lower() or 
                suchbegriff.lower() in notiz["inhalt"].lower() or
                any(suchbegriff.lower() in tag.lower() for tag in notiz.get("tags", []))):
                notiz_kopie = notiz.copy()
                notiz_kopie["kategorie"] = kategorie
                gefunden.append(notiz_kopie)
    return gefunden

@mcp.tool
def neue_aufgabe(titel: str, beschreibung: str, priorität: str = "mittel", deadline: str = None, kategorie: str = "allgemein") -> str:
    """Erstellt eine neue Aufgabe.
    
    Args:
        titel: Kurzer Titel der Aufgabe
        beschreibung: Detaillierte Beschreibung
        priorität: hoch, mittel oder niedrig
        deadline: Deadline im Format YYYY-MM-DD
        kategorie: Kategorie der Aufgabe
    """
    neue_id = max([a["id"] for a in AUFGABEN], default=0) + 1
    
    if not deadline:
        deadline = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
    
    neue_aufgabe_obj = {
        "id": neue_id,
        "titel": titel,
        "beschreibung": beschreibung,
        "priorität": priorität,
        "deadline": deadline,
        "status": "offen",
        "kategorie": kategorie
    }
    
    AUFGABEN.append(neue_aufgabe_obj)
    return f"✅ Aufgabe '{titel}' erstellt (ID: {neue_id}, Deadline: {deadline})"

@mcp.tool
def aufgabe_erledigt(aufgaben_id: int) -> str:
    """Markiert eine Aufgabe als erledigt.
    
    Args:
        aufgaben_id: Die ID der zu erledigenden Aufgabe
    """
    for aufgabe in AUFGABEN:
        if aufgabe["id"] == aufgaben_id:
            aufgabe["status"] = "erledigt"
            return f"✅ Aufgabe '{aufgabe['titel']}' als erledigt markiert!"
    
    return f"❌ Aufgabe mit ID {aufgaben_id} nicht gefunden"

@mcp.tool
def tagesübersicht(datum: str = None) -> dict:
    """Erstellt eine Übersicht für einen Tag.
    
    Args:
        datum: Datum im Format YYYY-MM-DD (Standard: heute)
    """
    if not datum:
        datum = datetime.now().strftime("%Y-%m-%d")
    
    termine = hole_termine_datum(datum)
    dringende = [a for a in dringende_aufgaben() if a["deadline"] == datum]
    
    return {
        "datum": datum,
        "termine_anzahl": len(termine),
        "termine": termine,
        "dringende_aufgaben": dringende,
        "empfehlung": "Früh starten!" if len(termine) > 2 else "Entspannter Tag geplant"
    }

# =============================================================================
# PROMPTS - Intelligente Assistenz
# =============================================================================

@mcp.prompt
def tagesplanung_prompt(datum: str = None) -> str:
    """Erstellt einen intelligenten Prompt für Tagesplanung."""
    if not datum:
        datum = datetime.now().strftime("%Y-%m-%d")
    
    übersicht = tagesübersicht(datum)
    profil = hole_profil()
    
    termine_text = ""
    if übersicht["termine"]:
        termine_text = "Geplante Termine:\n"
        for termin in übersicht["termine"]:
            termine_text += f"- {termin['zeit']}: {termin['titel']} ({termin['ort']}, {termin['dauer']}min)\n"
    
    aufgaben_text = ""
    if übersicht["dringende_aufgaben"]:
        aufgaben_text = "\nDringende Aufgaben:\n"
        for aufgabe in übersicht["dringende_aufgaben"]:
            aufgaben_text += f"- {aufgabe['titel']} (Priorität: {aufgabe['priorität']})\n"
    
    return f"""
Hallo! Ich bin {profil['name']} und brauche Hilfe bei der Planung für {datum}.

{termine_text}{aufgaben_text}

Bitte erstelle mir eine optimale Tagesplanung mit:
1. 📅 Zeitoptimierung zwischen Terminen
2. ⚡ Priorisierung der Aufgaben
3. 🚗 Berücksichtigung von Fahrzeiten (bin in {profil['wohnort']})
4. ☕ Sinnvolle Pausen 
5. 🎯 Konkrete Empfehlungen für den Tag

Mein Arbeitsplatz: {profil['firma']} als {profil['beruf']}
"""

@mcp.prompt
def email_template_prompt(empfänger: str, betreff: str, kontext: str = "") -> str:
    """Intelligenter E-Mail Schreib-Prompt."""
    profil = hole_profil()
    kontakt = hole_kontakt(empfänger)
    
    kontakt_info = ""
    if "fehler" not in kontakt:
        kontakt_info = f"Empfänger: {kontakt['name']} ({kontakt['position']} bei {kontakt['firma']})\n"
    
    return f"""
Schreibe eine professionelle E-Mail:

Absender: {profil['name']} ({profil['beruf']} bei {profil['firma']})
{kontakt_info}Betreff: {betreff}

Kontext: {kontext}

Erstelle eine E-Mail mit:
1. ✉️ Passende Anrede basierend auf Beziehung
2. 📝 Klare, strukturierte Nachricht
3. 🎯 Konkreten nächsten Schritten
4. 🤝 Professionellem deutschen Geschäftsstil

Signatur: {profil['name']}, {profil['beruf']}, {profil['firma']}
"""

@mcp.prompt
def meeting_prep_prompt(meeting_titel: str, teilnehmer_liste: str, dauer: int) -> str:
    """Meeting-Vorbereitungs-Prompt."""
    return f"""
Hilf mir bei der Vorbereitung des Meetings "{meeting_titel}".

Details:
- Teilnehmer: {teilnehmer_liste}
- Dauer: {dauer} Minuten

Erstelle:
1. 📋 Strukturierte Agenda mit Zeitplan
2. 🎯 Konkrete Ziele für das Meeting
3. ❓ Wichtige Diskussionsfragen
4. 📝 Template für Meeting-Notizen
5. ✅ Vorbereitung-Checkliste für mich

Fokus auf Effizienz und klare Ergebnisse!
"""

# =============================================================================
# STARTUP & MAIN
# =============================================================================

@mcp.tool
def assistent_hilfe() -> str:
    """Zeigt alle verfügbaren Funktionen des Assistenten."""
    return """
🤖 Persönlicher Assistent - Verfügbare Funktionen:

📅 TERMINE:
- termine_heute() - Heutige Termine
- nächster_termin() - Nächster anstehender Termin
- tagesübersicht(datum) - Komplette Tagesansicht

✅ AUFGABEN:
- dringende_aufgaben() - Wichtige/dringende Tasks
- neue_aufgabe(titel, beschreibung, ...) - Neue Aufgabe erstellen
- aufgabe_erledigt(id) - Aufgabe abhaken

📝 NOTIZEN & SUCHE:
- suche_notizen(begriff) - Durchsucht alle Notizen
- Resources: notizen://arbeit, notizen://privat

👥 KONTAKTE:
- kontakte://anna, kontakte://tom, etc.

🤖 INTELLIGENTE PROMPTS:
- tagesplanung_prompt(datum) - Für Tagesplanung
- email_template_prompt(empfänger, betreff) - Für E-Mails
- meeting_prep_prompt(titel, teilnehmer, dauer) - Meeting-Prep

📊 RESOURCES:
- data://profil - Persönliche Daten
- termine://2025-09-12 - Termine nach Datum
- aufgaben://hoch - Aufgaben nach Priorität

Einfach die Funktionen aufrufen oder Resources abfragen!
"""

if __name__ == "__main__":
    print("🚀 Persönlicher Assistent wird gestartet...")
    print("=" * 60)
    
    print("✨ SERVER BEREIT!")
    print("Starte mit: mcp.run() oder verwende assistent_hilfe() für alle Funktionen")
    print()
    print("🎯 WORKSHOP ABGESCHLOSSEN!")
    print("Du hast erfolgreich einen vollständigen persönlichen Assistenten erstellt!")
    print()
    print("💡 NÄCHSTE SCHRITTE:")
    print("- Passe die Daten an deine Bedürfnisse an")
    print("- Erweitere um eigene Tools und Resources") 
    print("- Verbinde mit echten Datenquellen (Dateien, APIs)")
    print("- Starte den Server: mcp.run()")
    
    mcp.run()