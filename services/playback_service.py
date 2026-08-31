"""
Komponente: Playback

Verantwortung: Koordiniert die drei anderen Komponenten. Ein Klick auf
"Play" loest hier zwei Ablaeufe aus:

    1. start_playback() -> Track-Metadaten holen (Authentication + Metadata)
    2. stream()         -> Audiodaten ausliefern (Authentication + Metadata + Streaming)

Playback selbst enthaelt keine eigene Logik fuer Token-Pruefung, Metadaten
oder Dateizugriff - es ruft die zustaendigen Komponenten in der richtigen
Reihenfolge auf.
"""

from fastapi.responses import Response

from services import auth_service, metadata_service, streaming_service


def start_playback(track_id: int, authorization: str | None) -> dict:
    """Schritt 1: Anfrage authentifizieren, dann Metadaten zurueckgeben."""
    auth_service.check_auth(authorization)
    return metadata_service.get_track_metadata(track_id)


def stream(
    track_id: int,
    authorization: str | None,
    token: str | None,
    range_header: str | None,
) -> Response:
    """Schritt 2: Anfrage authentifizieren, Dateinamen holen, Audio streamen."""
    auth_service.check_auth(authorization, token)
    filename = metadata_service.get_track_filename(track_id)
    return streaming_service.build_stream_response(filename, range_header)
