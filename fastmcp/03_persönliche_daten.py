#!/usr/bin/env python3
"""
FastMCP Workshop - Teil 5: Intelligente Prompts
===============================================

Lernziel: Prompts (@mcp.prompt) verstehen und einsetzen

Was sind Prompts?
- Wiederverwendbare Nachrichten-Templates für KI-Assistenten
- Helfen bei strukturierten Anfragen an die KI
- Können Parameter enthalten für dynamische Inhalte
- Verbessern die Qualität der KI-Antworten

Heute erstellen wir intelligente Prompt-Templates!
"""

from fastmcp import FastMCP
from datetime import datetime, timedelta
import json

# Server für intelligente Assistenz
mcp = FastMCP(
    name="IntelligenterAssistent", 
    instructions="Dieser Server bietet strukturierte Prompts für verschiedene Aufgaben."
)

# Simulierte Daten
TERMINE = [
    {"datum": "2025-09-16", "zeit": "10:00", "titel": "Team Meeting", "ort": "Büro", "dauer": 60},
    {"datum": "2025-09-16", "zeit": "14:30", "titel": "Zahnarzt", "ort": "Praxis Dr. Weber", "dauer": 30},
    {"datum": "2025-09-17", "zeit": "09:00", "titel": "Workshop", "ort": "Online", "dauer": 120},
    {"datum": "2025-09-17", "zeit": "15:00", "titel": "Kaffee mit Anna", "ort": "Café Central", "dauer": 45}
]

AUFGABEN = [
    {"titel": "Code Review", "priorität": "hoch", "deadline": "2025-09-12", "status": "offen"},
    {"titel": "Dokumentation schreiben", "priorität": "mittel", "deadline": "2025-09-15", "status": "in_arbeit"},
    {"titel": "Newsletter lesen", "priorität": "niedrig", "deadline": "2025-09-20", "status": "offen"}
]

NOTIZEN = [
    "FastMCP Workshop vorbereiten - noch Beispiele für Prompts finden",
    "Neue Python Version 3.12 Features anschauen",
    "Backup der wichtigen Projekte machen"
]

# Prompt Templates
@mcp.prompt
def tagesplanung_prompt(datum: str) -> str:
    """Erstellt einen strukturierten Prompt für die Tagesplanung.
    
    Args:
        datum: Das Datum im Format YYYY-MM-DD
    """
    # Termine für den Tag finden
    tages_termine = [t for t in TERMINE if t["datum"] == datum]
    
    termine_text = ""
    if tages_termine:
        termine_text = "Termine für heute:\n"
        for termin in tages_termine:
            termine_text += f"- {termin['zeit']}: {termin['titel']} ({termin['ort']}, {termin['dauer']}min)\n"
    else:
        termine_text = "Keine Termine für heute geplant.\n"
    
    # Aufgaben mit Deadline heute
    wichtige_aufgaben = [a for a in AUFGABEN if a["deadline"] == datum or a["priorität"] == "hoch"]
    
    aufgaben_text = ""
    if wichtige_aufgaben:
        aufgaben_text = "\nWichtige Aufgaben:\n"
        for aufgabe in wichtige_aufgaben:
            aufgaben_text += f"- {aufgabe['titel']} (Priorität: {aufgabe['priorität']}, Status: {aufgabe['status']})\n"
    
    return f"""
Bitte hilf mir bei der Planung für den {datum}.

{termine_text}{aufgaben_text}

Erstelle eine strukturierte Tagesplanung mit:
1. Zeitplan optimierung (sind alle Termine machbar?)
2. Pufferzeiten zwischen Terminen
3. Priorisierung der Aufgaben
4. Vorschläge für effiziente Reihenfolge
5. Empfehlungen für Pausen

Berücksichtige dabei mögliche Fahrzeiten zwischen Terminen.
"""

@mcp.prompt  
def email_schreiben_prompt(empfänger: str, thema: str, ton: str = "professionell") -> str:
    """Prompt für das Schreiben strukturierter E-Mails.
    
    Args:
        empfänger: Name des E-Mail Empfängers
        thema: Das Hauptthema der E-Mail
        ton: Der gewünschte Ton (professionell, freundlich, formal)
    """
    ton_anweisungen = {
        "professionell": "höflich und geschäftsmäßig",
        "freundlich": "warm und persönlich", 
        "formal": "sehr höflich und respektvoll"
    }
    
    ton_beschreibung = ton_anweisungen.get(ton, "professionell")
    
    return f"""
Schreibe eine E-Mail an {empfänger} zum Thema "{thema}".

Der Ton sollte {ton_beschreibung} sein.

Struktur:
1. Passende Anrede für {empfänger}
2. Kurze, freundliche Einleitung
3. Hauptteil zum Thema "{thema}" - klar und präzise
4. Nächste Schritte oder Call-to-Action falls nötig
5. Professioneller Abschluss

Halte die E-Mail prägnant aber vollständig. Verwende deutschen Geschäfts-Stil.
"""

@mcp.prompt
def notizen_zusammenfassung_prompt(notizen_liste: list) -> str:
    """Prompt für intelligente Notizen-Zusammenfassung.
    
    Args:
        notizen_liste: Liste von Notizen als Strings
    """
    notizen_text = "\n".join([f"- {notiz}" for notiz in notizen_liste])
    
    return f"""
Analysiere diese Notizen und erstelle eine strukturierte Zusammenfassung:

{notizen_text}

Bitte erstelle:
1. **Kategorisierung** - Gruppiere ähnliche Themen
2. **Prioritäten** - Identifiziere wichtige/dringende Punkte  
3. **Aktions-Items** - Was muss getan werden?
4. **Zeitplan** - Wann sollten Dinge erledigt werden?
5. **Abhängigkeiten** - Was hängt voneinander ab?

Gib konkrete, umsetzbare Empfehlungen.
"""

@mcp.prompt
def meeting_vorbereitung_prompt(meeting_titel: str, teilnehmer: list, dauer: int) -> str:
    """Prompt für Meeting-Vorbereitung.
    
    Args:
        meeting_titel: Titel des Meetings
        teilnehmer: Liste der Teilnehmer
        dauer: Dauer in Minuten
    """
    teilnehmer_text = ", ".join(teilnehmer)
    
    return f"""
Hilf mir bei der Vorbereitung für das Meeting "{meeting_titel}".

Details:
- Teilnehmer: {teilnehmer_text}
- Dauer: {dauer} Minuten

Erstelle eine Meeting-Agenda mit:
1. **Begrüßung** (2-3 Min)
2. **Agenda-Review** (2 Min) 
3. **Hauptthemen** - aufgeteilt auf verfügbare Zeit
4. **Entscheidungen/Next Steps** (5-10 Min)
5. **Abschluss** (2-3 Min)

Zusätzlich benötige ich:
- Vorbereitung-Checkliste für mich als Organisator
- Fragen zum Einstieg/zur Diskussion
- Template für Meeting-Notizen
- Tipps für effiziente Durchführung

Berücksichtige die Teilnehmer-Anzahl und Zeitbegrenzung.
"""

# Tools, die Prompts verwenden
@mcp.tool
def plane_tag(datum: str = None) -> str:
    """Startet die Tagesplanung für ein bestimmtes Datum.
    
    Args:
        datum: Datum im Format YYYY-MM-DD (Standard: heute)
    """
    if not datum:
        datum = datetime.now().strftime("%Y-%m-%d")
    
    prompt = tagesplanung_prompt(datum)
    return f"Prompt für Tagesplanung erstellt:\n\n{prompt}"

@mcp.tool
def email_hilfe(empfänger: str, thema: str, ton: str = "professionell") -> str:
    """Erstellt einen Prompt für E-Mail Hilfe.
    
    Args:
        empfänger: Name des Empfängers
        thema: E-Mail Thema  
        ton: Gewünschter Ton
    """
    prompt = email_schreiben_prompt(empfänger, thema, ton)
    return f"E-Mail Prompt erstellt:\n\n{prompt}"

if __name__ == "__main__":
    
    mcp.run(transport="sse", host="localhost", port=8766)

    print("\n🎯 Was haben wir gelernt?")
    print("- @mcp.resource stellt Daten über URIs zur Verfügung")
    print("- Resources sind perfekt für persönliche Informationen") 
    print("- Tools können auf Resource-Daten zugreifen")
    print("- URIs folgen dem Schema 'data://name'")
    
    print("\n🔍 Probiere aus:")
    print("- Füge deine eigenen persönlichen Daten hinzu")
    print("- Erstelle eine Resource für deine Lieblingsmusik")
    print("- Baue ein Tool, das Hobbies auflistet")
    
    print("\n➡️  Weiter mit: 04_dynamische_resources.py")