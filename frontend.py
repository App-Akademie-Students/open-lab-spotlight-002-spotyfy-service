"""
Frontend fuer den Streaming-Prototyp.

Ruft die Track-Metadaten ueber die REST-API ab und spielt den Song
anschliessend ueber ein natives HTML5 <audio>-Element ab, das den
FastAPI-Streaming-Endpoint direkt anspricht.

Start:
    python frontend.py
"""

import sys
from pathlib import Path

import requests
import streamlit as st
from streamlit.runtime.scriptrunner import get_script_run_ctx
from streamlit.web import cli as stcli

from playback_animation import render_playback_animation

API_BASE_URL = "http://localhost:8000"
DEMO_TOKEN = "demo-token"


def render_app() -> None:
    """Rendert die Streamlit-Oberflaeche."""
    st.set_page_config(page_title="Was passiert, wenn du auf Play drueckst?")

    st.title("Was passiert, wenn du auf Play drueckst?")

    # --- 1. Track-Metadaten ueber die REST API abrufen -------------------
    # Der Authorization-Header zeigt den Authentifizierungs-Schritt der
    # Architektur: das Backend prueft das Token, bevor es Daten herausgibt.
    response = requests.get(
        f"{API_BASE_URL}/api/tracks/1",
        headers={"Authorization": f"Bearer {DEMO_TOKEN}"},
    )
    response.raise_for_status()
    track = response.json()

    st.subheader(track["title"])
    st.write(track["artist"])
    st.caption(f"Dauer: {track['duration']}")

    # --- 2. Player: direkter Aufruf des Streaming-Endpoints --------------
    stream_url = f"{API_BASE_URL}{track['stream_url']}"
    st.audio(stream_url, format="audio/mpeg")

    # --- 3. Play-Ablauf als Animation ----------------------------------
    # Zeigt Schritt fuer Schritt, was technisch passiert, wenn man auf
    # "Play" drueckt. Die Animation laeuft in einem isolierten Iframe
    # (`st.components.v1.html`), weil bewegte Pfeile / Datenpakete sich
    # mit Streamlit-Bordmitteln nicht darstellen lassen.
    st.divider()
    st.subheader("Play-Ablauf – Schritt fuer Schritt")
    render_playback_animation()

    # --- 4. Technischer Ablauf fuer das Webinar --------------------------
    st.divider()
    st.subheader("Technischer Ablauf")
    st.markdown(
        """
        Das Backend besteht intern aus vier getrennten Komponenten:
        **Authentication**, **Playback**, **Metadata**, **Streaming**
        (Paket `services/`). Sie laufen gemeinsam in einer Anwendung.

        1. Frontend laedt Track-Metadaten (`render_app()` -> `requests.get()`)
        2. `GET /api/tracks/1` (Backend-Route `get_track()`)
        3. **Playback** koordiniert: ruft **Authentication** (`check_auth()`) auf, das den Authorization-Header prueft
        4. **Playback** ruft **Metadata** (`get_track_metadata()`) auf; die Route gibt das JSON zurueck
        5. Player fordert Audiodaten an (`st.audio()` rendert `<audio>`-Element, das die `stream_url` abruft)
        6. `GET /api/tracks/1/stream` (Backend-Route `stream_track()`)
        7. **Playback** ruft erneut **Authentication** (Token als Query-Parameter) und **Metadata** (`get_track_filename()`) auf
        8. Browser sendet Range Request (`Range: bytes=...`); **Streaming** (`build_stream_response()`) liest den Byte-Bereich
        9. **Streaming** liefert `206 Partial Content` (`Response(status_code=206, ...)`)
        10. Browser puffert Audiodaten und die Wiedergabe startet (`<audio>`-Element im Browser)
        """
    )


def main() -> None:
    """Startet Streamlit oder rendert die App im Streamlit-Prozess."""
    if get_script_run_ctx(suppress_warning=True) is None:
        sys.argv = ["streamlit", "run", str(Path(__file__).resolve())]
        stcli.main()
        return

    render_app()


if __name__ == "__main__":
    main()
