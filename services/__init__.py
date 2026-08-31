"""
Die vier Komponenten des Backends.

In dieser Demo laufen alle vier gemeinsam in einer Anwendung (modularer
Monolith). In einer grossen Plattform wie Spotify koennten diese
Verantwortlichkeiten auf eigenstaendige Services verteilt werden.

    Authentication -> prueft, wer die Anfrage stellt
    Metadata       -> kennt die Track-Informationen
    Streaming      -> liefert die Audiodaten in Teilstuecken
    Playback       -> koordiniert die drei anderen Komponenten
"""
