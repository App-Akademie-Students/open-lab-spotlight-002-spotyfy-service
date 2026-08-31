"""
Startet Backend und Frontend des Streaming-Prototyps mit einem Befehl.

Reihenfolge:
    1. Backend (FastAPI/uvicorn) starten
    2. Warten, bis das Backend erreichbar ist
    3. Frontend (Streamlit) starten

Start:
    python start_all.py
"""

import subprocess
import sys
import time

import requests

BACKEND_URL = "http://127.0.0.1:8000/api/tracks/1"
BACKEND_READY_TIMEOUT = 15  # Sekunden


def wait_for_backend(timeout: float) -> bool:
    """Wartet, bis das Backend auf HTTP-Requests antwortet."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            requests.get(BACKEND_URL, timeout=1)
            return True
        except requests.exceptions.ConnectionError:
            time.sleep(0.3)
    return False


def main() -> None:
    print("Starte Backend...")
    backend = subprocess.Popen([sys.executable, "backend.py"])

    try:
        if not wait_for_backend(BACKEND_READY_TIMEOUT):
            print("Backend ist nach Timeout nicht erreichbar. Breche ab.")
            backend.terminate()
            backend.wait()
            return

        print("Backend laeuft. Starte Frontend...")
        frontend = subprocess.Popen(
            [sys.executable, "-m", "streamlit", "run", "frontend.py"]
        )

        try:
            frontend.wait()
        except KeyboardInterrupt:
            pass
        finally:
            frontend.terminate()
            frontend.wait()
    except KeyboardInterrupt:
        pass
    finally:
        print("Beende Backend...")
        backend.terminate()
        backend.wait()


if __name__ == "__main__":
    main()
