#!/usr/bin/env python3
"""
Zentraler Workshop Personal Assistant MCP Server
Läuft auf einem zentralen Server und bedient alle Workshop-PCs
"""

import json
import os
import platform
import socket
import webbrowser
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import threading
import time

import psutil
import requests
from fastmcp import FastMCP

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# =============================================================================
# KONFIGURATION
# =============================================================================

# Server-Konfiguration
HOST = os.getenv("MCP_HOST", "0.0.0.0")  # Alle Interfaces
PORT = int(os.getenv("MCP_PORT", "8082"))
DASHBOARD_URL = os.getenv("DASHBOARD_URL", "http://localhost:8080")

# Server-ID
SERVER_ID = socket.gethostname()

# MCP Server initialisieren
mcp = FastMCP(f"Central Workshop Assistant")

# Zentrale Daten-Dateien
DATA_DIR = Path("workshop_data")
DATA_DIR.mkdir(exist_ok=True)

CENTRAL_NOTES_FILE = DATA_DIR / "central_notes.json"
CENTRAL_CONTACTS_FILE = DATA_DIR / "central_contacts.json"
CLIENT_SESSIONS_FILE = DATA_DIR / "client_sessions.json"

# Client-Session Tracking
active_clients = {}
client_lock = threading.Lock()

def ensure_data_files():
    """Stelle sicher, dass zentrale Daten-Dateien existieren"""
    if not CENTRAL_NOTES_FILE.exists():
        CENTRAL_NOTES_FILE.write_text(json.dumps({
            "global_todos": ["Workshop erfolgreich abschließen", "MCP Server zentral testen"],
            "client_todos": {},  # PC_ID -> todos
            "global_notes": ["FastMCP ist sehr praktisch!", f"Zentral gehostet auf {SERVER_ID}"]
        }, indent=2))
    
    if not CENTRAL_CONTACTS_FILE.exists():
        CENTRAL_CONTACTS_FILE.write_text(json.dumps({
            "contacts": [
                {"name": "Workshop Team", "email": "team@workshop.com", "phone": "+49 555 123456"},
                {"name": "Max Mustermann", "email": "max@example.com", "phone": "+49 123 456789"},
                {"name": "Admin Server", "email": f"admin@{SERVER_ID.lower()}.com", "phone": "+49 555 000000"}
            ]
        }, indent=2))
    
    if not CLIENT_SESSIONS_FILE.exists():
        CLIENT_SESSIONS_FILE.write_text(json.dumps({
            "sessions": {}
        }, indent=2))

def get_client_id() -> str:
    """Ermittle Client-ID (aus Request-Header oder generiere eine)"""
    # In einer echten Implementierung würdest du das aus dem Request-Header lesen
    # Für dieses Beispiel verwenden wir eine einfache Methode
    import threading
    thread_id = threading.current_thread().ident
    
    with client_lock:
        # Suche nach existierender Session für diesen Thread
        for client_id, session in active_clients.items():
            if session.get("thread_id") == thread_id:
                session["last_seen"] = datetime.now().isoformat()
                return client_id
        
        # Neue Session erstellen
        client_count = len(active_clients) + 1
        client_id = f"workshop-pc-{client_count:02d}"
        active_clients[client_id] = {
            "thread_id": thread_id,
            "first_seen": datetime.now().isoformat(),
            "last_seen": datetime.now().isoformat(),
            "requests_count": 0
        }
        return client_id

def track_client_request(client_id: str):
    """Tracke Client-Request"""
    with client_lock:
        if client_id in active_clients:
            active_clients[client_id]["requests_count"] += 1
            active_clients[client_id]["last_seen"] = datetime.now().isoformat()

def send_to_dashboard(endpoint: str, data: dict) -> bool:
    """Sende Update an Dashboard-Server"""
    try:
        response = requests.post(
            f"{DASHBOARD_URL}/api/{endpoint}",
            json=data,
            timeout=2
        )
        return response.status_code == 200
    except Exception as e:
        print(f"⚠️ Dashboard-Update fehlgeschlagen: {e}")
        return False

# =============================================================================
# ZENTRALE TOOLS
# =============================================================================

@mcp.tool()
def workshop_add_todo(task: str, global_todo: bool = False) -> str:
    """Füge Todo hinzu (client-spezifisch oder global)"""
    client_id = get_client_id()
    track_client_request(client_id)
    
    ensure_data_files()
    data = json.loads(CENTRAL_NOTES_FILE.read_text())
    
    if global_todo:
        data["global_todos"].append(task)
        target = "Global"
    else:
        if client_id not in data["client_todos"]:
            data["client_todos"][client_id] = []
        data["client_todos"][client_id].append(task)
        target = client_id
    
    CENTRAL_NOTES_FILE.write_text(json.dumps(data, indent=2), encoding='utf-8')
    
    # An Dashboard senden
    dashboard_success = send_to_dashboard("todo", {
        "task": task,
        "pc_id": client_id,
        "global": global_todo,
        "timestamp": datetime.now().isoformat()
    })
    
    status = "📡 Live-Dashboard" if dashboard_success else "💾 Zentral"
    return f"✅ Todo hinzugefügt ({status}, {target}): {task}"

@mcp.tool()
def workshop_set_mood(mood: str) -> str:
    """Setze Workshop-Stimmung: 😊 😐 😴 🤯"""
    client_id = get_client_id()
    track_client_request(client_id)
    
    # Validiere Mood
    valid_moods = ["😊", "😐", "😴", "🤯"]
    if mood not in valid_moods:
        return f"❌ Ungültige Stimmung. Wähle: {' '.join(valid_moods)}"
    
    # An Dashboard senden
    dashboard_success = send_to_dashboard("mood", {
        "mood": mood,
        "pc_id": client_id,
        "timestamp": datetime.now().isoformat()
    })
    
    mood_labels = {
        "😊": "Super!",
        "😐": "Geht so",
        "😴": "Müde",
        "🤯": "Overwhelmed"
    }
    
    status = "📡 Live-Dashboard" if dashboard_success else "💾 Zentral"
    return f"🎭 Stimmung gesetzt ({status}, {client_id}): {mood} {mood_labels[mood]}"

@mcp.tool()
def tug_left() -> str:
    """Ziehe das Seil nach LINKS! ⬅️"""
    client_id = get_client_id()
    track_client_request(client_id)
    
    send_to_dashboard("tug", {
        "direction": "left",
        "pc_id": client_id,
        "timestamp": datetime.now().isoformat()
    })
    return f"⬅️ {client_id}: Seil nach LINKS gezogen!"

@mcp.tool()  
def tug_right() -> str:
    """Ziehe das Seil nach RECHTS! ➡️"""
    client_id = get_client_id()
    track_client_request(client_id)
    
    send_to_dashboard("tug", {
        "direction": "right", 
        "pc_id": client_id,
        "timestamp": datetime.now().isoformat()
    })
    return f"➡️ {client_id}: Seil nach RECHTS gezogen!"

@mcp.tool()
def get_todos(show_global: bool = True) -> str:
    """Zeige Todos an (client-spezifisch und/oder global)"""
    client_id = get_client_id()
    track_client_request(client_id)
    
    ensure_data_files()
    data = json.loads(CENTRAL_NOTES_FILE.read_text())
    
    result = f"📝 **Todos für {client_id}:**\n"
    
    # Client-spezifische Todos
    client_todos = data.get("client_todos", {}).get(client_id, [])
    if client_todos:
        result += "\n🔹 **Deine Aufgaben:**\n"
        for i, todo in enumerate(client_todos, 1):
            result += f"{i}. {todo}\n"
    else:
        result += "\n🔹 **Deine Aufgaben:** Keine\n"
    
    # Globale Todos
    if show_global:
        global_todos = data.get("global_todos", [])
        if global_todos:
            result += "\n🌍 **Globale Aufgaben:**\n"
            for i, todo in enumerate(global_todos, 1):
                result += f"{i}. {todo}\n"
    
    return result

@mcp.tool()
def get_workshop_status() -> str:
    """Zeige Workshop-Status und aktive Clients"""
    client_id = get_client_id()
    track_client_request(client_id)
    
    with client_lock:
        active_count = len(active_clients)
        total_requests = sum(session.get("requests_count", 0) for session in active_clients.values())
    
    result = f"""🚀 **Workshop Status (Zentral gehostet):**
📊 **Server:** {SERVER_ID}
👥 **Aktive Clients:** {active_count}
📨 **Gesamt Requests:** {total_requests}
📻 **Dein Client:** {client_id}
🕒 **Server-Zeit:** {datetime.now().strftime("%H:%M:%S")}

💻 **Aktive Clients:**
"""
    
    with client_lock:
        for cid, session in active_clients.items():
            last_seen = session.get("last_seen", "Unbekannt")
            requests = session.get("requests_count", 0)
            indicator = "🟢" if cid == client_id else "🔵"
            result += f"{indicator} {cid}: {requests} requests, zuletzt: {last_seen[:19]}\n"
    
    return result

@mcp.tool()
def server_system_info() -> str:
    """Zeige Server-System-Informationen"""
    client_id = get_client_id()
    track_client_request(client_id)
    
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    return f"""🖥️ **Zentraler Server Status:**
📊 **Server ID:** {SERVER_ID}
• CPU Nutzung: {cpu_percent}%
• Arbeitsspeicher: {memory.percent}% ({memory.used // 1024**3}GB / {memory.total // 1024**3}GB)
• Festplatte: {disk.percent}% ({disk.used // 1024**3}GB / {disk.total // 1024**3}GB)
• System: {platform.system()} {platform.release()}
• Python: {platform.python_version()}

📡 **Netzwerk:**
• Host: {HOST}:{PORT}
• Dashboard: {DASHBOARD_URL}

📻 **Dein Client:** {client_id}"""

@mcp.tool()
def quick_search(query: str) -> str:
    """Info über Google-Suche (öffnet nicht direkt)"""
    client_id = get_client_id()
    track_client_request(client_id)
    
    search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    return f"""🔍 **Google-Suche für '{query}':**
🌐 URL: {search_url}
📻 Client: {client_id}

💡 **Hinweis:** Da der Server zentral läuft, kann der Browser nicht direkt geöffnet werden.
Kopiere die URL und öffne sie in deinem lokalen Browser."""

# =============================================================================
# RESOURCES
# =============================================================================

@mcp.resource("uri://assistant/contacts")
def contacts_resource() -> str:
    """Zentrale Workshop-Kontakte"""
    ensure_data_files()
    
    data = json.loads(CENTRAL_CONTACTS_FILE.read_text())
    contacts = data.get("contacts", [])
    
    result = f"👥 **Zentrale Workshop-Kontakte:**\n\n"
    for contact in contacts:
        result += f"**{contact['name']}**\n"
        result += f"📧 {contact['email']}\n"
        result += f"📞 {contact['phone']}\n\n"
    
    return result

@mcp.resource("uri://assistant/workshop-schedule")
def workshop_schedule_resource() -> str:
    """Workshop-Terminkalender"""
    current_time = datetime.now()
    today = current_time.strftime("%A, %d. %B %Y")
    client_id = get_client_id()
    
    schedule = [
        {"time": "09:00", "event": "🚀 FastMCP Workshop Start", "location": "Schulungsraum A", "status": "✅"},
        {"time": "09:15", "event": "📚 MCP Grundlagen", "location": "Schulungsraum A", "status": "✅"},
        {"time": "09:30", "event": "💻 Hands-On Development", "location": "Schulungsraum A", "status": "🔄"},
        {"time": "10:30", "event": "☕ Kaffeepause", "location": "Lounge", "status": "⏳"},
        {"time": "11:00", "event": "🔗 Zentrale Server Integration", "location": "Schulungsraum A", "status": "⏳"},
        {"time": "11:30", "event": "🚀 Live Demo & Test", "location": "Schulungsraum A", "status": "⏳"},
        {"time": "12:00", "event": "🎉 Wrap-up & Q&A", "location": "Schulungsraum A", "status": "⏳"}
    ]
    
    result = f"📅 **FastMCP Workshop - {today}:**\n"
    result += f"📻 **Dein Client:** {client_id}\n"
    result += f"🖥️ **Zentraler Server:** {SERVER_ID}\n\n"
    
    for item in schedule:
        result += f"{item['status']} **{item['time']}** - {item['event']}\n"
        result += f"📍 {item['location']}\n\n"
    
    return result

# =============================================================================
# PROMPTS
# =============================================================================

@mcp.prompt()
def workshop_briefing() -> str:
    """Workshop-Briefing für zentralen Server"""
    client_id = get_client_id()
    current_time = datetime.now().strftime("%H:%M")
    
    return f"""👋 **Willkommen zum FastMCP Workshop! (Zentral gehostet)**

🕒 **Aktuelle Zeit:** {current_time}
📻 **Dein Client:** {client_id}
🖥️ **Zentraler Server:** {SERVER_ID}

📡 **Live-Dashboard:** {DASHBOARD_URL}

🚀 **Deine Workshop-Tools:**
• `workshop_add_todo(task, global_todo=False)` - Todo hinzufügen
• `workshop_set_mood(mood)` - Stimmung teilen (😊😐😴🤯)
• `get_workshop_status()` - Workshop-Status anzeigen
• `server_system_info()` - Server-System-Info

💻 **Standard-Tools:**
• `get_todos(show_global=True)` - Todos anzeigen
• `quick_search(query)` - Google-Suche (URL)
• `tug_left()` / `tug_right()` - Seilziehen

📊 **Resources:**
• uri://assistant/contacts - Workshop-Kontakte
• uri://assistant/workshop-schedule - Workshop-Zeitplan

🎯 **Los geht's!** Wie kann ich dir beim Workshop helfen?"""

# =============================================================================
# SERVER CLEANUP & MONITORING
# =============================================================================

def cleanup_inactive_clients():
    """Entferne inaktive Clients (Hintergrund-Task)"""
    while True:
        try:
            current_time = datetime.now()
            with client_lock:
                inactive_clients = []
                for client_id, session in active_clients.items():
                    last_seen = datetime.fromisoformat(session["last_seen"])
                    if (current_time - last_seen).seconds > 300:  # 5 Minuten
                        inactive_clients.append(client_id)
                
                for client_id in inactive_clients:
                    print(f"🧹 Removing inactive client: {client_id}")
                    del active_clients[client_id]
            
            time.sleep(60)  # Prüfe jede Minute
        except Exception as e:
            print(f"❌ Cleanup error: {e}")
            time.sleep(60)

# =============================================================================
# SERVER STARTEN
# =============================================================================

if __name__ == "__main__":
    # Stelle sicher, dass Daten-Dateien existieren
    ensure_data_files()
    
    print("🚀 " + "="*70)
    print("🚀 ZENTRALER Workshop Personal Assistant MCP Server")
    print("🚀 " + "="*70)
    print(f"🖥️ Server ID: {SERVER_ID}")
    print(f"📡 Host: {HOST}:{PORT}")
    print(f"📊 Dashboard URL: {DASHBOARD_URL}")
    print(f"💾 Daten-Verzeichnis: {DATA_DIR}")
    print("🔗 Bereit für Langflow Integration!")
    print("🚀 " + "="*70)
    
    # Dashboard-Verbindung testen
    try:
        response = requests.get(f"{DASHBOARD_URL}/api/dashboard-data", timeout=3)
        if response.status_code == 200:
            print("✅ Dashboard-Verbindung erfolgreich!")
        else:
            print("⚠️ Dashboard erreichbar aber Fehler")
    except:
        print("❌ Dashboard nicht erreichbar (läuft offline)")
    
    # Cleanup-Thread starten
    cleanup_thread = threading.Thread(target=cleanup_inactive_clients, daemon=True)
    cleanup_thread.start()
    print("🧹 Client-Cleanup Thread gestartet")
    
    print("🚀 Server startet...")
    
    # Server starten
    mcp.run(transport="http", host=HOST, port=PORT)