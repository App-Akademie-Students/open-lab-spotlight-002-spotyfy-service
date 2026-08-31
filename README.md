# Spotify-Streaming-Demo

Ein minimalistischer, aber echt funktionierender Prototyp, der zeigt,
was technisch passiert, wenn man bei einem Musik-Streamingdienst auf
"Play" drueckt: REST-API, einfache Authentifizierung, Metadaten und
echtes HTTP-Streaming mit Range Requests.

> Dieser Prototyp bildet nicht Spotify selbst nach. Er demonstriert lediglich
> einige grundlegende Architekturprinzipien eines Streamingdienstes: REST API,
> Authentifizierung, Metadaten, HTTP Range Requests, Streaming und
> clientseitiges Buffering.

## Architektur

```text
Streamlit Frontend
        |
        | HTTP / REST
        v
FastAPI Backend
        |
        +-- Authentication   (services/auth_service.py)
        +-- Playback         (services/playback_service.py)
        +-- Metadata         (services/metadata_service.py)
        +-- Streaming        (services/streaming_service.py)
```

Es handelt sich um einen **modularen Monolithen**: Die vier Komponenten
sind im Code klar getrennt, laufen aber gemeinsam in einer Anwendung.
In einer grossen Plattform wie Spotify koennten solche Verantwortlichkeiten
auf eigenstaendige Services verteilt werden.

- **Authentication** – prueft das Demo-Token (Header oder Query-Parameter).
- **Playback** – koordiniert die anderen drei Komponenten bei jedem Play-Klick.
- **Metadata** – kennt Titel, Kuenstler, Dauer und Dateinamen des Tracks.
- **Streaming** – liest die Audiodatei und liefert sie per HTTP Range Requests aus.

`backend.py` ist nur die REST-Schicht und reicht die Anfragen an diese
Komponenten weiter.

## Setup

1. Virtuelle Umgebung erstellen:

   ```bash
   python -m venv .venv
   .venv\Scripts\activate   # Windows
   source .venv/bin/activate  # macOS/Linux
   ```

2. Dependencies installieren:

   ```bash
   pip install -r requirements.txt
   ```

3. MP3-Datei nach `audio/song.mp3` kopieren (eigene Datei, beliebiger Song).

4. Backend und Frontend zusammen starten:

   ```bash
   python start_all.py
   ```

   `start_all.py` startet zuerst das Backend, wartet bis es erreichbar ist,
   und startet danach automatisch das Frontend. Mit `Strg+C` werden beide
   Prozesse wieder beendet.

   Alternativ lassen sich beide Teile auch manuell in zwei Terminals starten:

   ```bash
   # Terminal 1
   uvicorn backend:app --reload --port 8000

   # Terminal 2
   streamlit run frontend.py
   ```

5. Browser oeffnet sich automatisch unter `http://localhost:8501`.
   Auf "Play" im Player klicken und im Terminal des Backends beobachten,
   wie die MP3-Datei in Teilstuecken (Range Requests) angefordert wird.

## Was zeigt die Demo?

- **`GET /api/tracks/1`** liefert Track-Metadaten. Der Request muss einen
  gueltigen `Authorization: Bearer demo-token`-Header enthalten, sonst
  antwortet das Backend mit `401 Unauthorized`.
- **`GET /api/tracks/1/stream`** liefert die Audiodatei. Der Browser sendet
  beim Abspielen automatisch `Range`-Header (z. B. `bytes=0-262143`), damit
  er die Datei nicht komplett auf einmal laden muss. Das Backend antwortet
  darauf mit `206 Partial Content` und den Headern `Accept-Ranges`,
  `Content-Range` und `Content-Length`.
- Die Konsole des Backends zeigt live, welche Byte-Bereiche angefordert
  und ausgeliefert werden - gut sichtbar im Webinar.

## Einschraenkung der Authentifizierung

Das HTML5-`<audio>`-Element kann beim Nachladen der Datei keine eigenen
HTTP-Header setzen. Deshalb akzeptiert der Streaming-Endpoint das Demo-Token
zusaetzlich als Query-Parameter (`?token=demo-token`), den das Backend in der
`stream_url` der Metadaten-Antwort mitliefert. Das ist die einfachste Loesung,
die das Prinzip "Anfrage wird authentifiziert" fuer diese Demo korrekt zeigt -
fuer eine echte Anwendung waere z. B. ein kurzlebiger, signierter Stream-Link
notwendig.
