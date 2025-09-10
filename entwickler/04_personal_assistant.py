#!/usr/bin/env python3
"""
Personal Assistant MCP Server
Ein einfacher MCP Server für den FastMCP Workshop
"""

import json
import os
import platform
import subprocess
import webbrowser
from datetime import datetime
from pathlib import Path
from typing import List

import psutil
from fastmcp import FastMCP

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# MCP Server initialisieren
app = FastMCP("Personal Assistant")

# Lokale Daten-Dateien
NOTES_FILE = Path("assistant_notes.json")
CONTACTS_FILE = Path("assistant_contacts.json")

def ensure_data_files():
    """Stelle sicher, dass Daten-Dateien existieren"""
    if not NOTES_FILE.exists():
        NOTES_FILE.write_text(json.dumps({
            "todos": ["Workshop abschließen", "MCP Server testen"],
            "notes": ["FastMCP ist sehr praktisch!", "Großartig für Automatisierung"]
        }, indent=2))
    
    if not CONTACTS_FILE.exists():
        CONTACTS_FILE.write_text(json.dumps({
            "contacts": [
                {"name": "Max Mustermann", "email": "max@example.com", "phone": "+49 123 456789"},
                {"name": "Anna Schmidt", "email": "anna@example.com", "phone": "+49 987 654321"},
                {"name": "Workshop Team", "email": "team@workshop.com", "phone": "+49 555 123456"}
            ]
        }, indent=2))

# =============================================================================
# TOOLS - Executable Funktionen
# =============================================================================

@app.tool()
def add_todo(task: str) -> str:
    """Füge eine neue Aufgabe zur Todo-Liste hinzu"""
    ensure_data_files()
    
    data = json.loads(NOTES_FILE.read_text())
    data["todos"].append(task)
    NOTES_FILE.write_text(json.dumps(data, indent=2))
    
    return f"✅ Aufgabe hinzugefügt: {task}"

@app.tool()
def get_todos() -> str:
    """Zeige alle aktuellen Todo-Aufgaben an"""
    ensure_data_files()
    
    data = json.loads(NOTES_FILE.read_text())
    todos = data.get("todos", [])
    
    if not todos:
        return "📝 Keine Aufgaben vorhanden"
    
    result = "📝 **Deine Aufgaben:**\n"
    for i, todo in enumerate(todos, 1):
        result += f"{i}. {todo}\n"
    
    return result

@app.tool()
def system_info() -> str:
    """Zeige aktuelle System-Informationen an"""
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    return f"""🖥️ **System Status:**
• CPU Nutzung: {cpu_percent}%
• Arbeitsspeicher: {memory.percent}% ({memory.used // 1024**3}GB / {memory.total // 1024**3}GB)
• Festplatte: {disk.percent}% ({disk.used // 1024**3}GB / {disk.total // 1024**3}GB)
• System: {platform.system()} {platform.release()}
• Python: {platform.python_version()}"""

@app.tool()
def list_files(directory: str = ".") -> str:
    """Liste Dateien und Ordner in einem Verzeichnis auf"""
    try:
        path = Path(directory)
        if not path.exists():
            return f"❌ Verzeichnis nicht gefunden: {directory}"
        
        items = []
        for item in sorted(path.iterdir()):
            if item.is_dir():
                items.append(f"📁 {item.name}/")
            else:
                size = item.stat().st_size
                if size < 1024:
                    size_str = f"{size}B"
                elif size < 1024**2:
                    size_str = f"{size//1024}KB"
                else:
                    size_str = f"{size//1024**2}MB"
                items.append(f"📄 {item.name} ({size_str})")
        
        result = f"📂 **Inhalt von {directory}:**\n"
        result += "\n".join(items[:20])  # Erste 20 Items
        
        if len(items) > 20:
            result += f"\n... und {len(items)-20} weitere Items"
        
        return result
    
    except Exception as e:
        return f"❌ Fehler: {str(e)}"

@app.tool()
def open_url(url: str) -> str:
    """Öffne eine URL im Standard-Browser"""
    try:
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        webbrowser.open(url)
        return f"🌐 URL geöffnet: {url}"
    
    except Exception as e:
        return f"❌ Fehler beim Öffnen der URL: {str(e)}"

@app.tool()
def quick_search(query: str) -> str:
    """Führe eine schnelle Google-Suche aus"""
    search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    return open_url(search_url)

# =============================================================================
# RESOURCES - Datenquellen
# =============================================================================

@app.resource("uri://assistant/contacts")
def contacts_resource() -> str:
    """Persönliche Kontakte des Assistenten"""
    ensure_data_files()
    
    data = json.loads(CONTACTS_FILE.read_text())
    contacts = data.get("contacts", [])
    
    result = "👥 **Kontakte:**\n\n"
    for contact in contacts:
        result += f"**{contact['name']}**\n"
        result += f"📧 {contact['email']}\n"
        result += f"📞 {contact['phone']}\n\n"
    
    return result

@app.resource("uri://assistant/schedule")
def schedule_resource() -> str:
    """Heutiger Terminkalender (Beispieldaten)"""
    today = datetime.now().strftime("%A, %d. %B %Y")
    
    schedule = [
        {"time": "09:00", "event": "FastMCP Workshop", "location": "Schulungsraum A"},
        {"time": "10:30", "event": "Kaffeepause", "location": "Lounge"},
        {"time": "11:00", "event": "Hands-On Session", "location": "Schulungsraum A"},
        {"time": "12:00", "event": "Mittagspause", "location": "Cafeteria"},
        {"time": "13:00", "event": "Integration & Demo", "location": "Schulungsraum A"}
    ]
    
    result = f"📅 **Termine für {today}:**\n\n"
    for item in schedule:
        result += f"🕐 **{item['time']}** - {item['event']}\n"
        result += f"📍 {item['location']}\n\n"
    
    return result

@app.resource("uri://assistant/workspace")
def workspace_resource() -> str:
    """Aktuelle Arbeitsbereich-Informationen"""
    current_dir = Path.cwd()
    files_count = len([f for f in current_dir.glob("*") if f.is_file()])
    dirs_count = len([d for d in current_dir.glob("*") if d.is_dir()])
    
    result = f"""💼 **Arbeitsbereich:**
📂 Aktueller Ordner: {current_dir}
📄 Dateien: {files_count}
📁 Unterordner: {dirs_count}
🕒 Arbeitszeit: {datetime.now().strftime("%H:%M")}

💡 **Schnellaktionen:**
• Verwende `list_files()` für Dateiübersicht
• Verwende `system_info()` für Systemstatus
• Verwende `add_todo()` für neue Aufgaben"""

    return result

# =============================================================================
# PROMPTS - Template für Anweisungen
# =============================================================================

@app.prompt()
def daily_briefing(date: str = None, include_weather: bool = True) -> str:
    """Template für tägliches Briefing"""
    if date is None:
        date = datetime.now().strftime("%d.%m.%Y")
    
    weather_note = "\n🌤️ Wetter: Verwende `quick_search('Wetter [Stadt]')` für aktuelle Daten" if include_weather else ""
    
    return f"""👋 **Guten Morgen! Hier ist dein Briefing für {date}:**

📅 **Termine:** Siehe uri://assistant/schedule für den heutigen Kalender

📝 **Aufgaben:** Verwende `get_todos()` für deine aktuellen Aufgaben

👥 **Kontakte:** Bei Bedarf über uri://assistant/contacts verfügbar

🖥️ **System:** Verwende `system_info()` für aktuellen Status{weather_note}

💡 **Tipp:** Nutze `quick_search()` für schnelle Recherchen oder `add_todo()` für neue Aufgaben!

Wie kann ich dir heute helfen?"""

@app.prompt()
def help_assistant() -> str:
    """Hilfe-Template für verfügbare Funktionen"""
    return """🤖 **Personal Assistant - Verfügbare Funktionen:**

🔧 **Tools (ausführbare Aktionen):**
• `add_todo(task)` - Neue Aufgabe hinzufügen
• `get_todos()` - Alle Aufgaben anzeigen  
• `system_info()` - Systemstatus prüfen
• `list_files(directory)` - Dateien auflisten
• `open_url(url)` - URL im Browser öffnen
• `quick_search(query)` - Google-Suche starten

📊 **Resources (Datenquellen):**
• `uri://assistant/contacts` - Persönliche Kontakte
• `uri://assistant/schedule` - Heutiger Terminkalender
• `uri://assistant/workspace` - Arbeitsbereich-Info

📝 **Prompts (Templates):**
• `daily_briefing()` - Tägliches Briefing erstellen
• `help_assistant()` - Diese Hilfe anzeigen

💡 **Beispiel-Anfragen:**
"Zeige mir meine Aufgaben und füge 'E-Mails beantworten' hinzu"
"Wie ist der aktuelle Systemstatus?"
"Öffne Google und suche nach FastMCP Dokumentation"
"Erstelle ein Briefing für heute"
"""

# =============================================================================
# SERVER STARTEN
# =============================================================================

if __name__ == "__main__":
    # Stelle sicher, dass Daten-Dateien existieren
    ensure_data_files()
    
    print("🚀 Personal Assistant MCP Server gestartet!")
    print("📝 Lokale Daten werden in assistant_*.json gespeichert")
    print("🔗 Bereit für Langflow Integration!")
    
    # Server starten
    app.run()