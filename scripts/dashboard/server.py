"""FastAPI ダッシュボードサーバー (port 3940).

Run:
    uv run uvicorn scripts.dashboard.server:app --port 3940 --reload
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .insights import build_insights
from .loader import REPO_ROOT, load_all
from .summary import build_scatter, build_summary

STATIC_DIR = Path(__file__).resolve().parent / "static"

app = FastAPI(title="Trello Task Dashboard", version="0.1.0")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/summary")
def api_summary() -> JSONResponse:
    cards = load_all()
    return JSONResponse(build_summary(cards))


@app.get("/api/cards")
def api_cards() -> JSONResponse:
    cards = load_all()
    return JSONResponse([c.to_dict() for c in cards])


@app.get("/api/scatter")
def api_scatter() -> JSONResponse:
    cards = load_all()
    return JSONResponse(build_scatter(cards))


@app.get("/api/insights")
def api_insights() -> JSONResponse:
    cards = load_all()
    return JSONResponse(build_insights(cards))


@app.post("/api/refresh")
def api_refresh() -> JSONResponse:
    """Trello から再同期."""
    script = REPO_ROOT / "scripts" / "trello_sync.py"
    try:
        result = subprocess.run(
            [sys.executable, str(script)],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=600,
        )
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="sync timed out")
    return JSONResponse(
        {
            "ok": result.returncode == 0,
            "returncode": result.returncode,
            "stdout_tail": result.stdout.splitlines()[-10:],
            "stderr_tail": result.stderr.splitlines()[-5:],
        }
    )
