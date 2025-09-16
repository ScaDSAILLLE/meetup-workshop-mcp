#!/usr/bin/env python3
"""
FastMCP Workshop - Teil 5: Intelligente Prompts (Verbessert)
============================================================

Lernziel: Prompts (@mcp.prompt) verstehen und einsetzen

Was sind Prompts?
- Wiederverwendbare Nachrichten-Templates für KI-Assistenten
- Helfen bei strukturierten Anfragen an die KI
- Können Parameter enthalten für dynamische Inhalte
- Verbessern die Qualität der KI-Antworten

Verbesserte Version mit korrekter Typ-Behandlung!
"""

from fastmcp import FastMCP
from datetime import datetime, timedelta
from typing import Optional, List, Union
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
    {"titel": "Code Review", "priorität": "hoch", "deadline": "2025-09-16", "status": "offen"},
    {"titel": "Dokumentation schreiben", "priorität": "mittel", "deadline": "2025-09-17", "status": "in_arbeit"},
    {"titel": "Newsletter lesen", "priorität": "niedrig", "deadline": "2025-09-20", "status": "offen"}
]

NOTIZEN = [
    "FastMCP Workshop vorbereiten - noch Beispiele für Prompts finden",
    "Neue Python Version 3.12 Features anschauen",
    "Backup der wichtigen Projekte machen"
]

def validate_datum(datum: Optional[str]) -> str:
    """Validiert und normalisiert ein Datum."""
    if datum is None or datum == "null" or datum == "":
        return datetime.now().strftime("%Y-%m-%d")
    
    # Versuche verschiedene Formate zu parsen
    try:
        # ISO Format YYYY-MM-DD
        parsed_date = datetime.strptime(datum, "%Y-%m-%d")
        return parsed_date.strftime("%Y-%m-%d")
    except ValueError:
        try:
            # Deutsches Format DD.MM.YYYY
            parsed_date = datetime.strptime(datum, "%d.%m.%Y")
            return parsed_date.strftime("%Y-%m-%d")
        except ValueError:
            # Fallback auf heute
            return datetime.now().strftime("%Y-%m-%d")

# Prompt Templates
@mcp.prompt
def tagesplanung_prompt(datum: Optional[str] = None) -> str:
    """Erstellt einen strukturierten Prompt für die Tagesplanung.
    
    Args:
        datum: Das Datum im Format YYYY-MM-DD (optional, Standard: heute)
    """
    # Datum validieren und normalisieren
    gültiges_datum = validate_datum(datum)
    
    # Termine für den Tag finden
    tages_termine = [t for t in TERMINE if t["datum"] == gültiges_datum]
    
    termine_text = ""
    if tages_termine:
        termine_text = f"Termine für {gültiges_datum}:\n"
        for termin in tages_termine:
            termine_text += f"- {termin['zeit']}: {termin['titel']} ({termin['ort']}, {termin['dauer']}min)\n"
    else:
        termine_text = f"Keine Termine für {gültiges_datum} geplant.\n"
    
    # Aufgaben mit Deadline heute oder hoher Priorität
    wichtige_aufgaben = [a for a in AUFGABEN if a["deadline"] == gültiges_datum or a["priorität"] == "hoch"]
    
    aufgaben_text = ""
    if wichtige_aufgaben:
        aufgaben_text = "\nWichtige Aufgaben:\n"
        for aufgabe in wichtige_aufgaben:
            status_emoji = "✅" if aufgabe["status"] == "erledigt" else "🔄" if aufgabe["status"] == "in_arbeit" else "⏳"
            aufgaben_text += f"- {status_emoji} {aufgabe['titel']} (Priorität: {aufgabe['priorität']}, Status: {aufgabe['status']})\n"
    
    return f"""Bitte hilf mir bei der Planung für den {gültiges_datum}.

{termine_text}{aufgaben_text}

Erstelle eine strukturierte Tagesplanung mit:
1. **Zeitplan-Optimierung** - Sind alle Termine machbar?
2. **Pufferzeiten** - Realistische Zeiten zwischen Terminen
3. **Aufgaben-Priorisierung** - Was ist heute am wichtigsten?
4. **Effiziente Reihenfolge** - Optimale Abarbeitung
5. **Pausen-Empfehlungen** - Wann sollte ich Pausen einlegen?

Berücksichtige dabei:
- Mögliche Fahrzeiten zwischen verschiedenen Orten
- Energielevel zu verschiedenen Tageszeiten
- Deadlines und Prioritäten
- Work-Life-Balance

Gib konkrete, umsetzbare Empfehlungen!"""

@mcp.prompt  
def email_schreiben_prompt(empfänger: str, thema: str, ton: Optional[str] = "professionell") -> str:
    """Prompt für das Schreiben strukturierter E-Mails.
    
    Args:
        empfänger: Name des E-Mail Empfängers
        thema: Das Hauptthema der E-Mail
        ton: Der gewünschte Ton (professionell, freundlich, formal, informell)
    """
    ton_anweisungen = {
        "professionell": "höflich und geschäftsmäßig",
        "freundlich": "warm und persönlich", 
        "formal": "sehr höflich und respektvoll",
        "informell": "locker und entspannt"
    }
    
    ton_beschreibung = ton_anweisungen.get(ton or "professionell", "professionell")
    
    return f"""Schreibe eine E-Mail an **{empfänger}** zum Thema "**{thema}**".

**Gewünschter Ton:** {ton_beschreibung}

**E-Mail Struktur:**
1. **Anrede** - Passend für {empfänger} und den gewählten Ton
2. **Einleitung** - Kurz und freundlich, Bezug zum Thema
3. **Hauptteil** - Kern der Nachricht zu "{thema}"
   - Klar und präzise formuliert
   - Strukturiert in logische Absätze
   - Alle wichtigen Punkte abdecken
4. **Handlungsaufforderung** - Nächste Schritte oder Antwort-Erwartung
5. **Abschluss** - Professionell und freundlich

**Zusätzliche Anforderungen:**
- Deutsche Geschäfts-/Kommunikationsstandards beachten
- Länge: Prägnant aber vollständig (idealerweise 3-5 Absätze)
- Bei wichtigen Punkten gerne Aufzählungen verwenden
- Höflich aber nicht übertrieben formell

Erstelle eine E-Mail, die den Empfänger zur gewünschten Aktion motiviert!"""

@mcp.prompt
def notizen_zusammenfassung_prompt(notizen_liste: Optional[List[str]] = None) -> str:
    """Prompt für intelligente Notizen-Zusammenfassung.
    
    Args:
        notizen_liste: Liste von Notizen als Strings (optional, verwendet Standard-Notizen)
    """
    if not notizen_liste:
        notizen_liste = NOTIZEN
    
    notizen_text = "\n".join([f"• {notiz}" for notiz in notizen_liste])
    
    return f"""Analysiere diese {len(notizen_liste)} Notizen und erstelle eine strukturierte Zusammenfassung:

**Notizen:**
{notizen_text}

**Erstelle eine Analyse mit:**

1. **📂 Kategorisierung**
   - Gruppiere ähnliche Themen und Bereiche
   - Identifiziere Haupt-Kategorien

2. **⚡ Prioritäten-Matrix**
   - Wichtig & Dringlich (sofort erledigen)
   - Wichtig & Nicht dringlich (planen)
   - Dringlich & Nicht wichtig (delegieren/schnell abarbeiten)
   - Weder wichtig noch dringlich (eliminieren?)

3. **✅ Aktions-Items**
   - Konkrete To-Dos ableiten
   - Wer macht was bis wann?
   - Benötigte Ressourcen identifizieren

4. **📅 Zeitplan-Vorschlag**
   - Empfohlene Reihenfolge
   - Zeitschätzungen
   - Deadline-Management

5. **🔗 Abhängigkeiten**
   - Was muss vorher erledigt sein?
   - Welche Punkte bauen aufeinander auf?
   - Bottlenecks identifizieren

**Ziel:** Aus den Notizen einen klaren, umsetzbaren Aktionsplan machen!"""

@mcp.prompt
def meeting_vorbereitung_prompt(meeting_titel: str, teilnehmer: List[str], dauer: int) -> str:
    """Prompt für Meeting-Vorbereitung.
    
    Args:
        meeting_titel: Titel des Meetings
        teilnehmer: Liste der Teilnehmer
        dauer: Dauer in Minuten
    """
    teilnehmer_anzahl = len(teilnehmer)
    teilnehmer_text = ", ".join(teilnehmer)
    
    # Zeitberechnung für Agenda-Punkte
    diskussions_zeit = max(dauer - 15, 10)  # Mindestens 10 Min für Diskussion
    
    return f"""Hilf mir bei der professionellen Vorbereitung für das Meeting "**{meeting_titel}**".

**Meeting-Details:**
- 👥 Teilnehmer ({teilnehmer_anzahl}): {teilnehmer_text}
- ⏰ Dauer: {dauer} Minuten
- 📋 Thema: {meeting_titel}

**1. 📋 Optimierte Agenda:**
- **Begrüßung & Check-in** (3-5 Min)
- **Agenda-Review & Ziele** (2-3 Min)  
- **Hauptdiskussion** ({diskussions_zeit} Min)
  - [Spezifische Unterpunkte basierend auf Titel]
- **Entscheidungen & Next Steps** (5-7 Min)
- **Abschluss & Termine** (2-3 Min)

**2. ✅ Vorbereitungs-Checkliste:**
- [ ] Meeting-Raum/Link vorbereiten
- [ ] Agenda 24h vorher versenden  
- [ ] Materialien/Dokumente bereitstellen
- [ ] Technische Ausrüstung testen
- [ ] Moderation vorbereiten

**3. 💬 Diskussions-Starter:**
- Einstiegsfragen für produktive Diskussion
- Methoden zur Einbindung aller Teilnehmer
- Techniken bei schwierigen Gesprächen

**4. 📝 Meeting-Notizen Template:**
- Strukturiertes Format für Protokoll
- Aktions-Items mit Verantwortlichen
- Entscheidungs-Dokumentation

**5. 🎯 Effizienz-Tipps:**
- Zeitmanagement bei {teilnehmer_anzahl} Teilnehmern
- Fokus-Techniken für {dauer} Minuten
- Follow-up Strategie

Erstelle einen detaillierten Plan für ein produktives Meeting!"""

@mcp.prompt
def code_review_prompt(sprache: str, code_typ: str, komplexität: Optional[str] = "mittel") -> str:
    """Prompt für strukturierte Code-Reviews.
    
    Args:
        sprache: Programmiersprache (Python, JavaScript, etc.)
        code_typ: Art des Codes (API, Frontend, Script, etc.)  
        komplexität: Komplexität des Codes (einfach, mittel, hoch)
    """
    komplexitäts_focus = {
        "einfach": "Grundlagen und Best Practices",
        "mittel": "Architektur und Performance",
        "hoch": "Design Patterns und Skalierbarkeit"
    }
    
    focus = komplexitäts_focus.get(komplexität or "mittel", "Architektur und Performance")
    
    return f"""Führe ein strukturiertes Code-Review für **{sprache}** {code_typ} durch.

**Code-Kontext:**
- 🖥️ Sprache: {sprache}
- 📦 Typ: {code_typ}
- 📊 Komplexität: {komplexität} (Focus: {focus})

**Review-Kategorien:**

**1. 🔍 Code-Qualität**
- Lesbarkeit und Verständlichkeit
- Naming-Conventions  
- Code-Struktur und Organisation
- Kommentierung und Dokumentation

**2. ⚡ Performance & Effizienz**
- Algorithmus-Optimierungen
- Memory-Management
- Laufzeit-Komplexität
- Resource-Nutzung

**3. 🛡️ Sicherheit & Robustheit**
- Input-Validierung
- Error-Handling
- Sicherheitslücken
- Edge-Cases

**4. 🏗️ Architektur & Design**
- Design-Patterns
- Code-Wiederverwendung
- Separation of Concerns
- SOLID-Prinzipien

**5. 🧪 Testbarkeit**
- Unit-Test Möglichkeiten
- Mock-Freundlichkeit
- Test-Coverage Gaps
- Integration-Punkte

**6. 📚 {sprache}-Spezifika**
- Sprachen-spezifische Best Practices
- Framework-Conventions
- Community-Standards

**Review-Format:**
- ✅ **Positive Aspekte** - Was ist gut gemacht?
- ⚠️ **Verbesserungsvorschläge** - Konkrete Empfehlungen
- 🚨 **Kritische Issues** - Muss behoben werden
- 💡 **Optimierungen** - Nice-to-have Verbesserungen

Gib konstruktives, umsetzbares Feedback!"""

# Tools, die Prompts verwenden
@mcp.tool
def plane_tag(datum: Optional[str] = None) -> str:
    """Startet die Tagesplanung für ein bestimmtes Datum.
    
    Args:
        datum: Datum im Format YYYY-MM-DD oder DD.MM.YYYY (Standard: heute)
    """
    try:
        gültiges_datum = validate_datum(datum)
        prompt = tagesplanung_prompt(datum)
        return f"✅ Tagesplanung-Prompt für {gültiges_datum} erstellt:\n\n{prompt}"
    except Exception as e:
        return f"❌ Fehler bei der Tagesplanung: {str(e)}"

@mcp.tool
def email_hilfe(empfänger: str, thema: str, ton: Optional[str] = "professionell") -> str:
    """Erstellt einen Prompt für E-Mail Hilfe.
    
    Args:
        empfänger: Name des Empfängers
        thema: E-Mail Thema  
        ton: Gewünschter Ton (professionell, freundlich, formal, informell)
    """
    try:
        if not empfänger.strip() or not thema.strip():
            return "❌ Empfänger und Thema dürfen nicht leer sein!"
            
        prompt = email_schreiben_prompt(empfänger, thema, ton)
        return f"✅ E-Mail Prompt erstellt:\n\n{prompt}"
    except Exception as e:
        return f"❌ Fehler beim E-Mail Prompt: {str(e)}"

@mcp.tool
def notizen_analysieren(eigene_notizen: Optional[List[str]] = None) -> str:
    """Analysiert Notizen und erstellt Aktionsplan.
    
    Args:
        eigene_notizen: Optional eigene Notizen-Liste (Standard: Demo-Notizen)
    """
    try:
        prompt = notizen_zusammenfassung_prompt(eigene_notizen)
        notizen_anzahl = len(eigene_notizen) if eigene_notizen else len(NOTIZEN)
        return f"✅ Notizen-Analyse Prompt für {notizen_anzahl} Notizen erstellt:\n\n{prompt}"
    except Exception as e:
        return f"❌ Fehler bei der Notizen-Analyse: {str(e)}"

@mcp.tool  
def meeting_planen(titel: str, teilnehmer: List[str], dauer: int) -> str:
    """Plant ein Meeting mit strukturierter Vorbereitung.
    
    Args:
        titel: Meeting-Titel
        teilnehmer: Liste der Teilnehmer-Namen
        dauer: Dauer in Minuten
    """
    try:
        if not titel.strip():
            return "❌ Meeting-Titel darf nicht leer sein!"
        if not teilnehmer or len(teilnehmer) == 0:
            return "❌ Mindestens ein Teilnehmer erforderlich!"
        if dauer < 15 or dauer > 480:
            return "❌ Meeting-Dauer sollte zwischen 15 und 480 Minuten liegen!"
            
        prompt = meeting_vorbereitung_prompt(titel, teilnehmer, dauer)
        return f"✅ Meeting-Vorbereitung Prompt erstellt:\n\n{prompt}"
    except Exception as e:
        return f"❌ Fehler bei der Meeting-Planung: {str(e)}"

@mcp.tool
def code_review_hilfe(sprache: str, code_typ: str, komplexität: Optional[str] = "mittel") -> str:
    """Erstellt einen strukturierten Code-Review Prompt.
    
    Args:
        sprache: Programmiersprache (Python, JavaScript, Java, etc.)
        code_typ: Art des Codes (API, Frontend, Backend, Script, etc.)
        komplexität: Komplexität (einfach, mittel, hoch)
    """
    try:
        if not sprache.strip() or not code_typ.strip():
            return "❌ Sprache und Code-Typ dürfen nicht leer sein!"
            
        prompt = code_review_prompt(sprache, code_typ, komplexität)
        return f"✅ Code-Review Prompt für {sprache} {code_typ} erstellt:\n\n{prompt}"
    except Exception as e:
        return f"❌ Fehler beim Code-Review Prompt: {str(e)}"

if __name__ == "__main__":
    print("🚀 Verbesserter FastMCP Prompt Server startet...")
    print("🔧 Verbesserungen:")
    print("  - Korrekte Optional[str] Type Hints")
    print("  - Datum-Validierung mit Fallback")
    print("  - Bessere Error-Behandlung") 
    print("  - Mehr Prompt-Templates")
    print("  - Verbesserte Dokumentation")
    
    mcp.run(transport="sse", host="localhost", port=8766)

    print("\n🎯 Was haben wir verbessert?")
    print("- Optional[str] statt str = None für korrekte Typ-Behandlung")
    print("- validate_datum() Funktion für robuste Datums-Verarbeitung") 
    print("- Bessere Error-Behandlung in allen Tools")
    print("- Mehr strukturierte Prompt-Templates")
    print("- Emoji und Formatierung für bessere Lesbarkeit")
    
    print("\n🔍 Jetzt funktioniert:")
    print("- plane_tag() auch mit null/None-Werten")
    print("- Flexible Datums-Formate (ISO + deutsch)")
    print("- Robuste Input-Validierung")
    print("- Aussagekräftige Fehlermeldungen")