"""
Komponente: Authentication

Verantwortung: Prueft, ob eine Anfrage berechtigt ist.

Extrem vereinfacht: ein einziges, fest verdrahtetes Token. Kein OAuth,
keine Benutzerverwaltung - es geht nur darum, den Architektur-Schritt
"Anfrage wird authentifiziert" sichtbar zu machen.
"""

from fastapi import HTTPException

DEMO_TOKEN = "demo-token"


def check_auth(authorization: str | None, token: str | None = None) -> None:
    """Prueft das Demo-Token und wirft 401, wenn es fehlt oder falsch ist.

    Normalerweise steckt das Token im Authorization-Header
    ("Authorization: Bearer demo-token"). Das HTML5 <audio>-Element kann
    beim Nachladen der Datei aber keine eigenen Header setzen, deshalb
    akzeptiert der Streaming-Endpoint das Token alternativ als
    Query-Parameter (?token=demo-token). Fuer diese Demo ist das
    ausreichend; in einer echten Anwendung waere dafuer z. B. ein
    kurzlebiger, signierter Stream-Link noetig.
    """
    if authorization == f"Bearer {DEMO_TOKEN}":
        return
    if token == DEMO_TOKEN:
        return
    raise HTTPException(status_code=401, detail="Unauthorized")
