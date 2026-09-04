#!/usr/bin/env python3
"""
Workshop Dashboard Server
Sammelt Updates von 20 Workshop-PCs und zeigt sie live auf dem Beamer
Mit JSON-Persistierung für Datenspeicherung bei Neustart
"""

import asyncio
import json
import socket
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# =============================================================================
# DATENMODELLE
# =============================================================================

class TodoUpdate(BaseModel):
    task: str
    pc_id: str
    timestamp: str = None

class MoodUpdate(BaseModel):
    mood: str  # 😊😐😴🤯
    pc_id: str
    timestamp: str = None

# Datenmodell
class TugUpdate(BaseModel):
    direction: str  # "left" or "right"
    pc_id: str
    timestamp: str = None

class ToolUsageUpdate(BaseModel):
    tool_name: str
    pc_id: str
    timestamp: str = None

# =============================================================================
# DASHBOARD DATA STORE
# =============================================================================

class WorkshopDashboard:
    def __init__(self, data_file: str = "workshop_data.json"):
        self.data_file = Path(data_file)
        self.todos: List[Dict] = []
        self.moods: Dict[str, str] = {}  # pc_id -> mood
        self.tool_usage: Dict[str, int] = {}  # tool_name -> count
        self.active_pcs: Set[str] = set()
        self.connected_clients: Set[WebSocket] = set()
        self.tug_left_pulls: int = 0
        self.tug_right_pulls: int = 0
        self.tug_position = 50
        
        # Daten beim Start laden
        self.load_data()

    def save_data(self):
        """Speichere aktuelle Daten in JSON-Datei"""
        try:
            data = {
                "todos": self.todos,
                "moods": self.moods,
                "tool_usage": self.tool_usage,
                "active_pcs": list(self.active_pcs),  # Set -> List für JSON
                "tug_left_pulls": self.tug_left_pulls,
                "tug_right_pulls": self.tug_right_pulls,
                "tug_position": self.tug_position,
                "last_saved": datetime.now().isoformat()
            }
            
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"⚠️  Fehler beim Speichern: {e}")

    def load_data(self):
        """Lade Daten aus JSON-Datei beim Start"""
        try:
            if self.data_file.exists():
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                self.todos = data.get("todos", [])
                self.moods = data.get("moods", {})
                self.tool_usage = data.get("tool_usage", {})
                self.active_pcs = set(data.get("active_pcs", []))  # List -> Set
                self.tug_left_pulls = data.get("tug_left_pulls", 0)
                self.tug_right_pulls = data.get("tug_right_pulls", 0)
                self.tug_position = data.get("tug_position", 50)
                
                print(f"✅ Daten geladen: {len(self.todos)} Todos, {len(self.active_pcs)} aktive PCs")
            else:
                print("📂 Keine vorherigen Daten gefunden, starte mit leeren Daten")
                
        except Exception as e:
            print(f"⚠️  Fehler beim Laden: {e} - Starte mit leeren Daten")

    def add_todo(self, update: TodoUpdate):
        todo_data = {
            "task": update.task,
            "pc_id": update.pc_id,
            "timestamp": update.timestamp or datetime.now().isoformat()
        }
        self.todos.append(todo_data)
        self.active_pcs.add(update.pc_id)
        
        # Nur letzte 50 Todos behalten
        if len(self.todos) > 50:
            self.todos = self.todos[-50:]
        
        self.save_data()  # Nach Änderung speichern

    def update_mood(self, update: MoodUpdate):
        self.moods[update.pc_id] = update.mood
        self.active_pcs.add(update.pc_id)
        self.save_data()

    def track_tool_usage(self, update: ToolUsageUpdate):
        self.tool_usage[update.tool_name] = self.tool_usage.get(update.tool_name, 0) + 1
        self.active_pcs.add(update.pc_id)
        self.save_data()

    def update_tug(self, update: TugUpdate):
        """Update Tauziehen-State (mit ausführlichen Debug-Prints)"""
        # --- Debug: Eingangszustand ------------------------------------------------
        print("\n[TUG][DEBUG] ---- update_tug() aufgerufen ----")
        print(f"[TUG][DEBUG] Eingabe: direction={getattr(update, 'direction', None)!r}, pc_id={getattr(update, 'pc_id', None)!r}")

        prev_left = getattr(self, "tug_left_pulls", 0)
        prev_right = getattr(self, "tug_right_pulls", 0)
        prev_pos = getattr(self, "tug_position", 50)
        prev_active_count = len(getattr(self, "active_pcs", set()))

        print(f"[TUG][DEBUG] Vorher: left={prev_left}, right={prev_right}, position={prev_pos}, active_pcs={prev_active_count}")

        # --- Zähler aktualisieren ---------------------------------------------------
        if update.direction == "left":
            self.tug_left_pulls += 1
            print(f"[TUG][DEBUG] Pull nach LINKS registriert -> left: {prev_left} -> {self.tug_left_pulls}")
        elif update.direction == "right":
            self.tug_right_pulls += 1
            print(f"[TUG][DEBUG] Pull nach RECHTS registriert -> right: {prev_right} -> {self.tug_right_pulls}")
        else:
            print(f"[TUG][WARN ] Unbekannte direction {update.direction!r} – Zähler bleiben unverändert.")

        # --- active_pcs aktualisieren ----------------------------------------------
        was_active = update.pc_id in self.active_pcs
        self.active_pcs.add(update.pc_id)
        now_active_count = len(self.active_pcs)
        if was_active:
            print(f"[TUG][DEBUG] PC {update.pc_id!r} war bereits aktiv. active_pcs bleibt {now_active_count}.")
        else:
            print(f"[TUG][DEBUG] PC {update.pc_id!r} hinzugefügt. active_pcs: {prev_active_count} -> {now_active_count}")

        # --- Position berechnen -----------------------------------------------------
        total_pulls = self.tug_left_pulls + self.tug_right_pulls
        print(f"[TUG][DEBUG] total_pulls={total_pulls} (L={self.tug_left_pulls}, R={self.tug_right_pulls})")

        if total_pulls == 0:
            self.tug_position = 50
            print("[TUG][DEBUG] Keine Pulls -> Position auf Mitte (50) gesetzt.")
        else:
            shift = (self.tug_right_pulls - self.tug_left_pulls) * 2  # 2 Punkte pro Pull-Differenz
            unclamped = 50 + shift
            clamped = max(0, min(100, unclamped))
            self.tug_position = clamped
            print(f"[TUG][DEBUG] shift={shift}, unclamped={unclamped}, clamped={clamped}, vorher={prev_pos}")

        print(f"[TUG][DEBUG] Neue Position: {self.tug_position}")

        # --- Victory-Check ----------------------------------------------------------
        winner = self.check_tug_victory()
        print(f"[TUG][DEBUG] Victory-Check Ergebnis: {winner!r}")

        if winner:
            print(f"🎉 {winner.upper()} GEWINNT das Tauziehen!")
            print("[TUG][DEBUG] Auto-Reset in 4 Sekunden wird gestartet …")
            asyncio.create_task(self.reset_tug_after_victory())

        # --- Persistenz -------------------------------------------------------------
        try:
            self.save_data()
            print("[TUG][DEBUG] State erfolgreich gespeichert.")
        except Exception as e:
            print(f"[TUG][ERROR] save_data fehlgeschlagen: {e!r}")

        print("[TUG][DEBUG] ---- update_tug() fertig ----\n")


    def check_tug_victory(self):
        """Prüfe ob jemand gewonnen hat"""
        if self.tug_position <= 10:
            return "links"
        elif self.tug_position >= 90:
            return "rechts"
        return None

    async def reset_tug_after_victory(self):
        """Reset Tauziehen nach Victory-Celebration"""
        await asyncio.sleep(4)  # 4 Sekunden warten
        self.tug_left_pulls = 0
        self.tug_right_pulls = 0
        self.tug_position = 50
        self.save_data()
        print("🔄 Neues Tauziehen-Spiel gestartet!")
        
        # Broadcast update to all clients
        await self.broadcast_to_clients()
    
    async def broadcast_to_clients(self):
        """Helper method to broadcast updates"""
        if not self.connected_clients:
            return
        
        data = json.dumps(self.get_dashboard_data())
        disconnected = set()
        
        for client in self.connected_clients:
            try:
                await client.send_text(data)
            except:
                disconnected.add(client)
        
        # Getrennte Clients entfernen
        for client in disconnected:
            self.connected_clients.discard(client)

    def reset_data(self):
        """Setze alle Daten zurück (für Admin/Reset-Zwecke)"""
        self.todos = []
        self.moods = {}
        self.tool_usage = {}
        self.active_pcs = set()
        self.tug_left_pulls = 0
        self.tug_right_pulls = 0
        self.tug_position = 50
        self.save_data()
        print("🔄 Alle Daten zurückgesetzt")

    def get_dashboard_data(self) -> Dict:
        """Aktuelle Dashboard-Daten für Frontend"""
        mood_summary = {}
        for mood in ["😊", "😐", "😴", "🤯"]:
            mood_summary[mood] = sum(1 for m in self.moods.values() if m == mood)

        return {
            "todos": self.todos[-10:],  # Letzte 10 Todos
            "mood_summary": mood_summary,
            "active_pcs": len(self.active_pcs),
            "total_todos": len(self.todos),
            "tool_usage": dict(sorted(self.tool_usage.items(), key=lambda x: x[1], reverse=True)[:10]),
            "timestamp": datetime.now().isoformat(),
            "tug_left_pulls": self.tug_left_pulls,
            "tug_right_pulls": self.tug_right_pulls,
            "tug_position": self.tug_position,
            "tug_winner": self.check_tug_victory()  # Victory state für Frontend
        }

# =============================================================================
# FASTAPI APP
# =============================================================================

app = FastAPI(title="Workshop Dashboard Server")
dashboard = WorkshopDashboard()

# Static files für HTML Dashboard
dashboard_dir = Path(__file__).parent / "dashboard"
dashboard_dir.mkdir(exist_ok=True)

# Mount static files 
app.mount("/static", StaticFiles(directory=dashboard_dir), name="static")

# =============================================================================
# WEBSOCKET FÜR LIVE UPDATES
# =============================================================================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    dashboard.connected_clients.add(websocket)
    
    print(f"📱 Dashboard Client verbunden. Insgesamt: {len(dashboard.connected_clients)}")
    
    try:
        # Aktuelle Daten sofort senden
        await websocket.send_text(json.dumps(dashboard.get_dashboard_data()))
        
        # Connection alive halten
        while True:
            await asyncio.sleep(1)
            
    except WebSocketDisconnect:
        dashboard.connected_clients.remove(websocket)
        print(f"📱 Dashboard Client getrennt. Verbleibend: {len(dashboard.connected_clients)}")

async def broadcast_update():
    """Sende Update an alle verbundenen Dashboard-Clients"""
    await dashboard.broadcast_to_clients()

# =============================================================================
# HTTP ENDPOINTS FÜR WORKSHOP-PC UPDATES
# =============================================================================

@app.post("/api/todo")
async def receive_todo(update: TodoUpdate):
    """Empfange Todo-Update von Workshop-PC"""
    dashboard.add_todo(update)
    await broadcast_update()
    return {"status": "success", "message": f"Todo von {update.pc_id} hinzugefügt"}

@app.post("/api/mood")
async def receive_mood(update: MoodUpdate):
    """Empfange Stimmungs-Update von Workshop-PC"""
    dashboard.update_mood(update)
    await broadcast_update()
    return {"status": "success", "message": f"Stimmung von {update.pc_id} aktualisiert"}

@app.post("/api/tool-usage")
async def receive_tool_usage(update: ToolUsageUpdate):
    """Empfange Tool-Usage von Workshop-PC"""
    dashboard.track_tool_usage(update)
    await broadcast_update()
    return {"status": "success", "message": f"Tool-Usage von {update.pc_id} getrackt"}

@app.get("/api/dashboard-data")
async def get_dashboard_data():
    """Hole aktuelle Dashboard-Daten (Fallback für Polling)"""
    return dashboard.get_dashboard_data()

@app.post("/api/tug")
async def receive_tug(update: TugUpdate):
    """Empfange Tauziehen-Update von Workshop-PC"""
    dashboard.update_tug(update)
    await broadcast_update()
    return {"status": "success", "message": f"Tauziehen von {update.pc_id}: {update.direction}"}

# BONUS: Reset-Endpoint für Admin
@app.post("/api/reset")
async def reset_dashboard():
    """Setze alle Dashboard-Daten zurück"""
    dashboard.reset_data()
    await broadcast_update()
    return {"status": "success", "message": "Dashboard zurückgesetzt"}

# =============================================================================
# MAIN DASHBOARD PAGE
# =============================================================================

@app.get("/", response_class=HTMLResponse)
async def dashboard_page():
    """Hauptseite für Beamer-Dashboard (Apple-like, minimal, projector-friendly)"""
    return """
    <!DOCTYPE html>
    <html lang="de">
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
      <title>Workshop Live Dashboard</title>
      <style>
        :root{
          /* Apple-ähnliche Farb-/Typo-Tokens */
          --bg: #f5f5f7;
          --card: #ffffff;
          --text: #1d1d1f;
          --muted: #6e6e73;
          --accent: #0a84ff;
          --border: rgba(0,0,0,0.08);
          --ok: #34c759;
          --warn: #ff9f0a;
          --bad: #ff3b30;
          --shadow: 0 10px 30px rgba(0,0,0,0.06), 0 2px 8px rgba(0,0,0,0.05);
        }
        *{box-sizing:border-box}
        html,body{height:100%}
        body{
          margin:0;
          background: var(--bg);
          color: var(--text);
          font: 400 18px/1.35 -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, "Apple Color Emoji","Segoe UI Emoji";
          -webkit-font-smoothing: antialiased;
          -moz-osx-font-smoothing: grayscale;
        }
        .wrap{
          max-width: 1600px;
          margin: 0 auto;
          padding: 24px clamp(16px, 3vw, 32px) 40px;
        }
        header{
          display:flex;align-items:center;justify-content:space-between;
          gap:16px;margin-bottom:24px
        }
        .title{
          display:flex;align-items:baseline;gap:16px;flex-wrap:wrap
        }
        h1{
          margin:0;
          font-weight:700;
          letter-spacing:-0.02em;
          font-size: clamp(28px, 4vw, 44px);
        }
        .subtitle{
          color:var(--muted);
          font-size: clamp(14px, 2.2vw, 18px);
        }
        .live{
          display:flex;align-items:center;gap:10px;
          background: var(--card);
          border:1px solid var(--border);
          padding:10px 14px;border-radius:14px;box-shadow: var(--shadow);
        }
        .dot{
          width:10px;height:10px;border-radius:50%;
          background: var(--ok);
          box-shadow: 0 0 0 0 rgba(52,199,89,0.6);
          animation: pulse 1.8s infinite;
        }
        @keyframes pulse{
          0%{box-shadow:0 0 0 0 rgba(52,199,89,0.6)}
          70%{box-shadow:0 0 0 16px rgba(52,199,89,0)}
          100%{box-shadow:0 0 0 0 rgba(52,199,89,0)}
        }
        .grid{
          display:grid;
          grid-template-columns: repeat(12, 1fr);
          gap: clamp(14px, 2vw, 22px);
        }
        /* KPI Cards oben - nur noch 2 */
        .kpi{
          grid-column: span 6;
          background:var(--card); border:1px solid var(--border);
          border-radius:24px; padding:24px; box-shadow: var(--shadow);
          min-height: 140px; display:flex;flex-direction:column;justify-content:center;
        }
        .kpi h3{
          margin:0 0 6px 0; color:var(--muted); font-weight:600; font-size: clamp(14px,1.8vw,18px);
        }
        .kpi .num{
          font-weight:800; letter-spacing:-0.02em;
          font-size: clamp(36px, 6.5vw, 72px);
          line-height:1.05;
        }
        .kpi .num-small{
          font-weight:800; letter-spacing:-0.02em;
          font-size: clamp(24px,4.2vw,24px);
          line-height:1.05;
        }

        .kpi small{color:var(--muted); font-size: clamp(12px,1.6vw,16px)}
        /* Stimmung + Tools + Todos */
        .card{
          background:var(--card); border:1px solid var(--border);
          border-radius:24px; padding:24px; box-shadow: var(--shadow);
          min-width: 300px;
        }
        .mood-card{
          min-width: 70vw;
        }
        .span-6{grid-column: span 6}
        .span-8{grid-column: span 8}
        .span-12{grid-column: span 12}
        .card h3{margin:0 0 16px 0; font-size: clamp(18px,3vw,24px)}
        /* Stimmung */
        .mood-row{
          display:grid; grid-template-columns: repeat(4,1fr); gap:14px; 
        }
        .mood{
          border:1px solid var(--border); border-radius:18px; padding:16px;
          display:flex;align-items:center;gap:14px; background:#fbfbfc;
        }
        .emoji{font-size: clamp(28px, 5vw, 42px)}
        .mood .count{
          font-weight:700; font-size: clamp(24px,4.2vw,40px); letter-spacing:-0.02em;
        }
        .mood .label{color:var(--muted); font-size: clamp(12px,1.6vw,16px)}
        .bar{flex:1;height:10px;background:#ececf0;border-radius:999px;overflow:hidden}
        .fill{height:100%; background:var(--accent); border-radius:999px; transform-origin:left center}
        /* Tool Badges */
        .tool-list{display:flex;flex-wrap:wrap; gap:10px}
        .badge{
          border:1px solid var(--border); background:#fbfbfc;
          padding:10px 14px; border-radius:999px; font-weight:600;
          font-size: clamp(12px,1.6vw,16px)
        }
        /* Todos */
        .todos{display:grid; grid-template-columns: repeat(3,1fr); gap:12px}
        .todo{
          border:1px solid var(--border); border-radius:16px; padding:16px; background:#fbfbfc;
          min-height:84px; display:flex;flex-direction:column;justify-content:space-between;
        }
        .todo b{font-size: clamp(14px,2.1vw,18px); font-weight:700; letter-spacing:-0.01em}
        .meta{color:var(--muted); font-size: clamp(12px,1.6vw,14px)}
        /* Tauziehen - schlicht im bestehenden Design */
        .tug-container{
          display: flex; align-items: center; gap: 20px;
        }
        .tug-side{
          display: flex; flex-direction: column; align-items: center; gap: 8px;
          min-width: 100px;
        }
        .tug-label{
          color: var(--muted); font-weight: 600; 
          font-size: clamp(14px,1.8vw,18px);
        }
        .tug-count{
          font-weight: 800; letter-spacing: -0.02em;
          font-size: clamp(24px,4.2vw,40px); line-height: 1.05;
        }
        .tug-rope-container{
          flex: 1; height: 40px; position: relative;
          background: #ececf0; border-radius: 20px; overflow: hidden;
        }
        .tug-rope{
          position: relative; width: 100%; height: 100%;
        }
        .tug-marker{
          position: absolute; top: 50%; left: 50%;
          transform: translate(-50%, -50%);
          font-size: clamp(20px, 3vw, 28px);
          transition: left 0.3s ease;
        }
        /* Fußleiste */
        footer{
          margin-top: 24px; color:var(--muted); display:flex;justify-content:space-between;align-items:center;
          font-size: clamp(12px,1.6vw,14px)
        }
        .mono{font-family: ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace}
        /* Responsiv */
        @media (max-width: 1200px){
          .kpi{grid-column: span 12}
          .span-8{grid-column: span 12}
          .span-6{grid-column: span 12}
          .todos{grid-template-columns: repeat(2,1fr)}
        }
        @media (max-width: 780px){
          .mood-row{grid-template-columns: 1fr 1fr}
          .todos{grid-template-columns: 1fr}
          .tug-container{flex-direction: column; gap: 16px;}
          .tug-rope-container{width: 100%;}
        }
        /* Victory Celebration */
        .victory-overlay{
          position: fixed; top: 0; left: 0; right: 0; bottom: 0;
          background: rgba(0,0,0,0.8); z-index: 1000;
          display: flex; align-items: center; justify-content: center;
          animation: fadeIn 0.3s ease;
        }
        .victory-message{
          background: var(--card); border-radius: 32px; padding: 48px;
          text-align: center; box-shadow: var(--shadow);
          animation: popIn 0.4s ease;
        }
        .victory-title{
          font-size: clamp(32px, 6vw, 64px); font-weight: 800;
          margin: 0 0 16px 0; letter-spacing: -0.02em;
        }
        .victory-subtitle{
          color: var(--muted); font-size: clamp(16px, 2.5vw, 24px);
          margin: 0;
        }
        .confetti{
          position: fixed; width: 10px; height: 10px; z-index: 999;
          animation: confetti-fall 3s linear forwards;
        }
        @keyframes fadeIn{
          from{opacity:0} to{opacity:1}
        }
        @keyframes popIn{
          from{transform:scale(0.8);opacity:0}
          to{transform:scale(1);opacity:1}
        }
        @keyframes confetti-fall{
          0%{transform:translateY(-100vh) rotate(0deg);opacity:1}
          100%{transform:translateY(100vh) rotate(720deg);opacity:0}
        }
      </style>
    </head>
    <body>
      <div class="wrap">
        <header>
          <div class="title">
            <h1>FastMCP Workshop – Live Dashboard</h1>
            <div class="subtitle">ScaDS.AI Living Lab · MCP Workshop</div>
          </div>
          <div class="live" id="liveBox" title="Verbindungsstatus">
            <div class="dot" id="liveDot"></div>
            <span id="statusTxt">Live</span>
          </div>
        </header>

        <section class="grid" id="grid">
          <!-- KPIs - nur noch 2 -->
          <div class="kpi"><h3>Aktive PCs</h3><div class="num" id="activePcs">–</div></div>
          <div class="kpi"><h3>Gesamt Todos</h3><div class="num" id="totalTodos">–</div></div>

          <!-- Stimmung -->
          <div class="card mood-card span-8">
            <h3>Stimmung im Raum</h3>
            <div class="mood-row" id="moodRow">
              <!-- dynamisch -->
            </div>
          </div>

          <!-- Tool Usage -->
          <div class="card span-4">
            <h3>Tool-Nutzung</h3>
            <div class="tool-list" id="toolUsage"></div>
          </div>

          <!-- Todos -->
          <div class="card span-12">
            <h3>Live Todos (letzte 10)</h3>
            <div class="todos" id="todosList"></div>
          </div>

          <!-- Tauziehen -->
          <div class="card span-12">
            <h3>Tauziehen</h3>
            <div class="tug-container">
              <div class="tug-side">
                <div class="tug-label">Links</div>
                <div class="tug-count" id="tugLeftCount">0</div>
              </div>
              <div class="tug-rope-container">
                <div class="tug-rope">
                  <div class="tug-marker" id="tugMarker">🪢</div>
                </div>
              </div>
              <div class="tug-side">
                <div class="tug-label">Rechts</div>
                <div class="tug-count" id="tugRightCount">0</div>
              </div>
            </div>
          </div>
        </section>

        <footer>
          <div>Zuletzt aktualisiert: <span id="ts">–</span></div>
          <div class="mono">v1 · Projektor-Modus · Persistent</div>
        </footer>
      </div>

      <script>
        // ——— Utilities
        const $ = (id) => document.getElementById(id);
        const two = (n)=> (Math.round(n*10)/10).toFixed(1);

        // ——— WebSocket mit Auto-Reconnect + sanftem Fallback
        const WS_URL = (location.protocol === 'https:' ? 'wss://' : 'ws://') + location.host + '/ws';
        let ws, backoff = 800, pollTimer = null;

        function setStatus(ok, msg){
          $('statusTxt').textContent = msg || (ok ? 'Live' : 'Getrennt – Reconnect…');
          $('liveDot').style.background = ok ? 'var(--ok)' : 'var(--warn)';
          $('liveBox').style.borderColor = ok ? 'var(--border)' : 'rgba(255,159,10,0.45)';
        }

        function startPolling(){
          if(pollTimer) return;
          pollTimer = setInterval(()=> {
            fetch('/api/dashboard-data').then(r=>r.json()).then(updateDashboard).catch(()=>{});
          }, 1200);
        }
        function stopPolling(){
          if(pollTimer){ clearInterval(pollTimer); pollTimer = null; }
        }

        function connectWS(){
          try{
            ws = new WebSocket(WS_URL);
            ws.onopen = () => { setStatus(true,'Live'); backoff = 800; stopPolling(); };
            ws.onmessage = (ev) => updateDashboard(JSON.parse(ev.data));
            ws.onclose = () => {
              setStatus(false,'Getrennt – Reconnect…');
              startPolling();
              setTimeout(connectWS, Math.min(6000, backoff));
              backoff = Math.min(6000, backoff * 1.6);
            };
            ws.onerror = () => { try{ ws.close(); }catch(e){} };
          }catch(e){
            // Fallback sofort starten
            startPolling();
            setTimeout(connectWS, 2000);
          }
        }
        connectWS();

        // ——— Rendering
        let currentWinner = null;
        
        function updateDashboard(data){
          // KPIs - nur noch 2
          $('activePcs').textContent = data.active_pcs ?? '–';
          $('totalTodos').textContent = data.total_todos ?? '–';
          $('ts').textContent = new Date(data.timestamp || Date.now()).toLocaleTimeString();

          // Stimmung
          const moods = [
            { key:'😊', label:'Super' },
            { key:'😐', label:'Okay' },
            { key:'😴', label:'Müde' },
            { key:'🤯', label:'Overwhelmed' },
          ];
          const total = Object.values(data.mood_summary || {}).reduce((a,b)=>a+(b||0),0) || 1;
          $('moodRow').innerHTML = moods.map(m=>{
            const count = (data.mood_summary && data.mood_summary[m.key]) || 0;
            const pct = Math.max(0, Math.min(100, Math.round(100*count/total)));
            return `
              <div class="mood">
                <div class="emoji">${m.key}</div>
                <div class="count">${count}</div>
                <div class="bar"><div class="fill" style="width:${pct}%"></div></div>
                <div class="label">${m.label}</div>
              </div>`;
          }).join('');

          // Tool Usage
          const tools = Object.entries(data.tool_usage || {});
          $('toolUsage').innerHTML = tools.length
            ? tools.map(([tool,count])=>`<span class="badge">${tool}&nbsp;·&nbsp;${count}</span>`).join('')
            : '<span class="badge">-</span>';

          // Todos (3 Spalten, große Lesbarkeit)
          const todos = (data.todos || []);
          $('todosList').innerHTML = todos.length
            ? todos.map(t => `
              <div class="todo">
                <b>${escapeHTML(t.task)}</b>
                <div class="meta">📻 ${escapeHTML(t.pc_id)} · ${new Date(t.timestamp).toLocaleTimeString()}</div>
              </div>`).join('')
            : '<div class="meta">Noch keine Todos…</div>';

          // Tauziehen
          $('tugLeftCount').textContent = data.tug_left_pulls || 0;
          $('tugRightCount').textContent = data.tug_right_pulls || 0;
          const tugPos = data.tug_position || 50;
          $('tugMarker').style.left = tugPos + '%';
          
          // Victory Check
          const winner = data.tug_winner;
          if(winner && winner !== currentWinner){
            currentWinner = winner;
            showVictoryCelebration(winner);
          } else if(!winner && currentWinner){
            currentWinner = null;
            hideVictoryCelebration();
          }
        }

        function showVictoryCelebration(winner){
          // Victory Overlay
          const overlay = document.createElement('div');
          overlay.className = 'victory-overlay';
          overlay.id = 'victoryOverlay';
          overlay.innerHTML = `
            <div class="victory-message">
              <div class="victory-title">🎉 ${winner.toUpperCase()} GEWINNT! 🎉</div>
              <div class="victory-subtitle">Neues Spiel startet in <span id="countdown">5</span> Sekunden...</div>
            </div>`;
          document.body.appendChild(overlay);
          
          // Konfetti starten
          createConfetti();
          
          // Countdown und Reset nach 5 Sekunden
          let countdown = 5;
          const countdownEl = document.getElementById('countdown');
          const countdownTimer = setInterval(() => {
            countdown--;
            if(countdownEl) countdownEl.textContent = countdown;
            
            if(countdown <= 0) {
              clearInterval(countdownTimer);
              // Frontend triggert den Reset
              fetch('/api/tug-reset', { method: 'POST' })
                .then(() => console.log('🔄 Tauziehen resettet'))
                .catch(e => console.error('Reset fehler:', e));
            }
          }, 1000);
        }

        function hideVictoryCelebration(){
          const overlay = $('victoryOverlay');
          if(overlay) overlay.remove();
        }

        function createConfetti(){
          const colors = ['#ff6b6b','#4ecdc4','#45b7d1','#f9ca24','#f0932b','#eb4d4b','#6c5ce7'];
          
          for(let i = 0; i < 50; i++){
            setTimeout(()=>{
              const confetti = document.createElement('div');
              confetti.className = 'confetti';
              confetti.style.left = Math.random() * 100 + '%';
              confetti.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
              confetti.style.animationDelay = Math.random() * 0.5 + 's';
              confetti.style.animationDuration = (Math.random() * 2 + 2) + 's';
              document.body.appendChild(confetti);
              
              // Konfetti nach Animation entfernen
              setTimeout(()=> confetti.remove(), 4000);
            }, i * 20);
          }
        }

        function escapeHTML(s){
          return String(s || '').replace(/[&<>"']/g, m=>({ '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;' }[m]));
        }

        // Optional: „Kiosk"-Fullscreen mit Taste F
        document.addEventListener('keydown', (e)=>{
          if(e.key.toLowerCase()==='f'){
            if(!document.fullscreenElement){ document.documentElement.requestFullscreen().catch(()=>{}); }
            else{ document.exitFullscreen().catch(()=>{}); }
          }
        });
      </script>
    </body>
    </html>
    """


# =============================================================================
# SERVER UTILITIES
# =============================================================================

def get_local_ip():
    """Finde lokale IP-Adresse für Workshop-Netzwerk"""
    try:
        # Erstelle Socket-Verbindung um lokale IP zu finden
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "localhost"

# =============================================================================
# STARTUP
# =============================================================================

if __name__ == "__main__":
    local_ip = get_local_ip()
    port = 8080
    
    print("🚀 " + "="*50)
    print("🚀 Workshop Dashboard Server startet!")
    print("🚀 " + "="*50)
    print(f"📱 Dashboard URL: http://{local_ip}:{port}")
    print(f"📡 API Endpoint: http://{local_ip}:{port}/api/")
    print(f"🔗 Für Workshop-PCs: DASHBOARD_URL = 'http://{local_ip}:{port}'")
    print(f"💾 Daten werden in 'workshop_data.json' gespeichert")
    print("🚀 " + "="*50)
    
    uvicorn.run(
        "dashboard_server:app",
        host="0.0.0.0",  # Auf allen Interfaces hören
        port=port,
        reload=False,
        log_level="info"
    )