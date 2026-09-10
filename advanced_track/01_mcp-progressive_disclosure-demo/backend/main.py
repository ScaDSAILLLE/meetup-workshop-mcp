"""Kombinierte Starlette-Anwendung für Workshop-Frontend und Demo-API."""

from pathlib import Path

import httpx
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import FileResponse, JSONResponse
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles

from backend.naive_mode import run_naive_mode
from backend.progressive_mode import run_progressive_mode

FRONTEND_DIR = Path(__file__).parent.parent / "frontend"


async def index(request: Request):
    """Liefert die Workshop-Oberfläche aus."""
    return FileResponse(FRONTEND_DIR / "index.html")


async def run_demo(request: Request):
    """Validiert eine Anfrage und führt beide Vergleichsmodi aus."""
    try:
        body = await request.json()
    except ValueError:
        return JSONResponse({"error": "Der Request enthält kein gültiges JSON."}, status_code=400)
    user_message = body.get("message") if isinstance(body, dict) else None
    if not isinstance(user_message, str) or not user_message.strip():
        return JSONResponse({"error": "Das Feld 'message' muss Text enthalten."}, status_code=400)
    if len(user_message) > 2000:
        return JSONResponse(
            {"error": "Die Anfrage darf höchstens 2000 Zeichen lang sein."}, status_code=400
        )

    try:
        naive_result = await run_naive_mode(user_message)
        progressive_result = await run_progressive_mode(user_message)
    except httpx.HTTPError as exc:
        return JSONResponse(
            {"error": f"LLM-Endpoint nicht erreichbar oder Timeout: {exc}"},
            status_code=504,
        )

    return JSONResponse({"normal": naive_result, "progressiv": progressive_result})


routes = [
    Route("/", index),
    Route("/api/demo", run_demo, methods=["POST"]),
    Mount("/", app=StaticFiles(directory=str(FRONTEND_DIR))),
]


app = Starlette(routes=routes)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8080)
