"""
Komponente: Metadata

Verantwortung: Kennt die Track-Informationen (Titel, Kuenstler, Dauer,
Dateiname) und stellt sie fuer andere Komponenten bereit.

Keine echte Datenbank noetig: fuer die Demo reicht ein einzelner,
fest verdrahteter Track.
"""

from fastapi import HTTPException

from services.auth_service import DEMO_TOKEN

TRACK = {
    "id": 1,
    "title": "Midnight Code",
    "artist": "The Developers",
    "duration": "3:42",
    "filename": "song.mp3",
}


def get_track_metadata(track_id: int) -> dict:
    """Liefert die oeffentlichen Metadaten eines Tracks inkl. Stream-URL."""
    if track_id != TRACK["id"]:
        raise HTTPException(status_code=404, detail="Track not found")

    return {
        "id": TRACK["id"],
        "title": TRACK["title"],
        "artist": TRACK["artist"],
        "duration": TRACK["duration"],
        "stream_url": f"/api/tracks/{TRACK['id']}/stream?token={DEMO_TOKEN}",
    }


def get_track_filename(track_id: int) -> str:
    """Liefert den Dateinamen der Audiodatei eines Tracks."""
    if track_id != TRACK["id"]:
        raise HTTPException(status_code=404, detail="Track not found")

    return TRACK["filename"]
