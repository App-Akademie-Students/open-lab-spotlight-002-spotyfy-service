"""
Backend fuer den Streaming-Prototyp (modularer Monolith).

Diese Datei ist nur die REST-Schicht: sie nimmt HTTP-Anfragen entgegen
und reicht sie an die vier Backend-Komponenten weiter, die im Paket
`services/` liegen:

    Authentication  -> services/auth_service.py
    Playback        -> services/playback_service.py
    Metadata        -> services/metadata_service.py
    Streaming       -> services/streaming_service.py

Die Komponenten laufen gemeinsam in dieser einen Anwendung. In einer
grossen Plattform wie Spotify koennten solche Verantwortlichkeiten auf
eigenstaendige Services verteilt werden.

Start:
    python backend.py
"""

from fastapi import FastAPI, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
import uvicorn

from services import playback_service

app = FastAPI(title="Spotify-Streaming-Demo Backend")

# --- CORS -------------------------------------------------------------
# Streamlit (8501) und FastAPI (8000) laufen auf unterschiedlichen Ports.
# Der Browser blockiert Cross-Origin-Requests deshalb standardmaessig.
# Wir erlauben hier ausschliesslich die Streamlit-Origin der Demo.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


# --- Route: Track-Metadaten --------------------------------------------
@app.get("/api/tracks/{track_id}")
def get_track(track_id: int, authorization: str | None = Header(default=None)):
    print(f"GET /api/tracks/{track_id}")
    return playback_service.start_playback(track_id, authorization)


# --- Route: Audio-Streaming mit HTTP Range Requests -------------------
@app.get("/api/tracks/{track_id}/stream")
def stream_track(
    track_id: int,
    request: Request,
    authorization: str | None = Header(default=None),
    token: str | None = None,
) -> Response:
    print(f"GET /api/tracks/{track_id}/stream")
    return playback_service.stream(
        track_id,
        authorization,
        token,
        request.headers.get("range"),
    )


def main() -> None:
    """Startet den FastAPI-Entwicklungsserver."""
    uvicorn.run("backend:app", host="127.0.0.1", port=8000, reload=True)


if __name__ == "__main__":
    main()
