"""
Komponente: Streaming

Verantwortung: Liest die Audiodatei von der Platte und liefert sie aus -
ganz oder, wenn der Browser einen Range-Header sendet, nur den
angefragten Ausschnitt (HTTP 206 Partial Content).
"""

from pathlib import Path

from fastapi import HTTPException
from fastapi.responses import Response

# audio/ liegt im Projektwurzelverzeichnis, eine Ebene ueber services/.
AUDIO_DIR = Path(__file__).parent.parent / "audio"

CHUNK_SIZE = 1024 * 256  # 256 KB, falls der Client keinen Range-Header sendet


def build_stream_response(filename: str, range_header: str | None) -> Response:
    """Baut die HTTP-Antwort fuer den Audio-Stream.

    Ohne Range-Header wird die komplette Datei ausgeliefert (200 OK),
    mit Range-Header nur der angefragte Byte-Bereich (206 Partial Content).
    """
    file_path = AUDIO_DIR / filename
    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="Audio file not found")

    file_size = file_path.stat().st_size

    # Der Browser (bzw. das <audio>-Element) fordert nicht immer die ganze
    # Datei an, sondern nur einen Ausschnitt, z. B.:
    #   Range: bytes=100000-200000
    print(f"Range: {range_header}")

    if range_header is None:
        # Kein Range-Header -> komplette Datei ausliefern (200 OK).
        with open(file_path, "rb") as f:
            data = f.read()
        print(f"Sending bytes 0-{file_size - 1}")
        return Response(
            content=data,
            media_type="audio/mpeg",
            headers={
                "Accept-Ranges": "bytes",
                "Content-Length": str(file_size),
            },
        )

    # Range-Header hat das Format "bytes=START-END", wobei END optional ist.
    range_value = range_header.replace("bytes=", "")
    start_str, _, end_str = range_value.partition("-")

    start = int(start_str) if start_str else 0
    end = int(end_str) if end_str else min(start + CHUNK_SIZE - 1, file_size - 1)
    end = min(end, file_size - 1)  # nie ueber das Dateiende hinaus lesen

    bytes_to_read = end - start + 1

    # Nur den angefragten Ausschnitt der Datei von der Platte lesen,
    # nicht die komplette Datei.
    with open(file_path, "rb") as f:
        f.seek(start)
        data = f.read(bytes_to_read)

    print(f"Sending bytes {start}-{end}")

    # HTTP 206 Partial Content: wir liefern nur einen Teil der Ressource.
    return Response(
        content=data,
        status_code=206,
        media_type="audio/mpeg",
        headers={
            "Accept-Ranges": "bytes",
            "Content-Range": f"bytes {start}-{end}/{file_size}",
            "Content-Length": str(bytes_to_read),
        },
    )
