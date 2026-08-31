"""
Visualisierung: Was passiert technisch beim Klick auf "Play"?

Eigenstaendiges, isoliertes Modul. Es aendert nichts an Backend oder
Services, sondern rendert nur eine kleine, didaktische Animation des
Play-Ablaufs als eingebettetes HTML/CSS/JavaScript.

Streamlit kann bewegte Pfeile / Datenpakete nicht mit Bordmitteln
darstellen, deshalb wird die Animation ueber ein isoliertes Iframe
(`st.components.v1.html`) eingebunden - ohne zusaetzliche Bibliotheken.

Verwendung im Frontend:

    from playback_animation import render_playback_animation
    render_playback_animation()
"""

import streamlit.components.v1 as components

# Die neun Schritte des Ablaufs. Jeder Schritt bewegt ein Datenpaket
# zwischen zwei Stationen ("from" -> "to"), hebt Stationen hervor und
# zeigt eine kurze Beschriftung.
#
#   from/to : ID einer Station (player | auth | playback | cdn | buffer)
#   packet  : Text auf dem bewegten Datenpaket
#   caption : ausfuehrliche Beschreibung des Schritts
#   active  : Stationen, die in diesem Schritt hervorgehoben werden
#   buffer  : Fuellstand des Buffers in Prozent (optional)
#   playing : True -> Wiedergabe-Symbol pulsiert (optional)
_STEPS = [
    {
        "from": "player", "to": "playback",
        "packet": "GET /api/tracks/1",
        "caption": "Player sendet einen Request an das Backend.",
        "active": ["player"],
    },
    {
        "from": "player", "to": "playback",
        "packet": "Authorization: Bearer demo-token",
        "caption": "Der Request traegt den Authorization-Header mit dem Token.",
        "active": ["player"],
    },
    {
        "from": "playback", "to": "auth",
        "packet": "Token pruefen",
        "caption": "Der Auth-Service prueft das Token – gueltig.",
        "active": ["auth"],
    },
    {
        "from": "auth", "to": "playback",
        "packet": "song.mp3",
        "caption": "Der Playback-Service ermittelt die Audioquelle.",
        "active": ["playback"],
    },
    {
        "from": "player", "to": "cdn",
        "packet": "Range: bytes=0-262143",
        "caption": "Player fordert einen Byte-Bereich an (Range Request).",
        "active": ["player", "cdn"],
    },
    {
        "from": "cdn", "to": "player",
        "packet": "HTTP 206 Partial Content",
        "caption": "Das CDN antwortet mit HTTP 206 Partial Content – nur der angefragte Ausschnitt.",
        "active": ["cdn"],
    },
    {
        "from": "player", "to": "buffer",
        "packet": "Audio-Chunk",
        "caption": "Die Audio-Daten werden in den Buffer geladen.",
        "active": ["buffer"],
        "buffer": 25,
    },
    {
        "from": "buffer", "to": "buffer",
        "packet": "▶",
        "caption": "Genug Daten im Buffer – die Wiedergabe startet.",
        "active": ["buffer"],
        "buffer": 25,
        "playing": True,
    },
    {
        "from": "cdn", "to": "buffer",
        "packet": "Audio-Chunk",
        "caption": "Weitere Audio-Chunks werden waehrend der Wiedergabe nachgeladen.",
        "active": ["cdn", "buffer"],
        "buffer": 100,
        "playing": True,
    },
]

# Iframe-Hoehe: Diagramm + Beschreibung + Schrittliste + Button.
_COMPONENT_HEIGHT = 620


def _build_html() -> str:
    """Baut das eigenstaendige HTML-Dokument fuer die Animation."""
    import json

    steps_json = json.dumps(_STEPS)

    return """
<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<style>
  :root {
    --accent: #1DB954;
    --ink: #1a1a1a;
    --muted: #6b7280;
    --line: #d1d5db;
    --bg: #ffffff;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    color: var(--ink);
    background: var(--bg);
  }
  .wrap { padding: 4px 2px 12px; }

  /* --- Diagramm --------------------------------------------------- */
  .stage {
    position: relative;
    height: 200px;
    margin-bottom: 8px;
  }
  .nodes {
    position: absolute;
    inset: 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  .node {
    width: 18%;
    text-align: center;
    padding: 12px 4px;
    border: 1.5px solid var(--line);
    border-radius: 10px;
    background: #fff;
    font-size: 12px;
    line-height: 1.3;
    color: var(--muted);
    transition: border-color .25s, color .25s, box-shadow .25s, transform .25s;
  }
  .node .title { font-weight: 600; display: block; font-size: 13px; }
  .node.active {
    border-color: var(--accent);
    color: var(--ink);
    box-shadow: 0 0 0 3px rgba(29,185,84,.15);
    transform: translateY(-2px);
  }
  .node .buffer-bar {
    margin-top: 8px;
    height: 6px;
    border-radius: 3px;
    background: #e5e7eb;
    overflow: hidden;
  }
  .node .buffer-fill {
    height: 100%;
    width: 0%;
    background: var(--accent);
    transition: width .7s ease;
  }
  .node .play-icon {
    margin-top: 6px;
    font-size: 14px;
    color: var(--accent);
    opacity: 0;
    transition: opacity .25s;
  }
  .node.playing .play-icon { opacity: 1; animation: pulse 1s infinite; }
  @keyframes pulse { 50% { opacity: .35; } }

  /* --- bewegtes Datenpaket -------------------------------------- */
  .packet {
    position: absolute;
    top: 0; left: 0;
    padding: 4px 9px;
    border-radius: 6px;
    background: var(--accent);
    color: #fff;
    font-size: 11px;
    font-weight: 600;
    white-space: nowrap;
    opacity: 0;
    transform: translate(-50%, -50%);
    transition: left .9s cubic-bezier(.45,.05,.35,1),
                top .9s cubic-bezier(.45,.05,.35,1),
                opacity .2s;
    pointer-events: none;
    box-shadow: 0 2px 6px rgba(0,0,0,.18);
  }
  .packet::after {
    content: "";
    position: absolute;
    left: 50%; bottom: -5px;
    width: 8px; height: 8px;
    background: var(--accent);
    transform: translateX(-50%) rotate(45deg);
  }

  /* --- Beschreibung + Schrittliste ----------------------------- */
  .caption {
    min-height: 40px;
    padding: 10px 12px;
    border-left: 3px solid var(--accent);
    background: #f6faf7;
    border-radius: 4px;
    font-size: 14px;
    margin-bottom: 12px;
  }
  .steps { list-style: none; margin: 0; padding: 0; }
  .steps li {
    display: flex;
    gap: 8px;
    align-items: baseline;
    padding: 4px 6px;
    font-size: 12.5px;
    color: var(--muted);
    border-radius: 4px;
    transition: background .2s, color .2s;
  }
  .steps li .num {
    flex: 0 0 20px;
    height: 20px;
    line-height: 20px;
    text-align: center;
    border-radius: 50%;
    background: #e5e7eb;
    font-size: 11px;
    font-weight: 600;
    color: var(--muted);
  }
  .steps li.done { color: var(--ink); }
  .steps li.done .num { background: var(--accent); color: #fff; }
  .steps li.current {
    background: #f6faf7;
    color: var(--ink);
    font-weight: 600;
  }
  .steps li.current .num {
    background: var(--accent);
    color: #fff;
    box-shadow: 0 0 0 3px rgba(29,185,84,.2);
  }

  /* --- Steuerung ---------------------------------------------- */
  .controls { margin-bottom: 10px; }
  .controls button + button { margin-left: 8px; }
  button {
    font: inherit;
    font-weight: 600;
    font-size: 13px;
    padding: 8px 18px;
    border: none;
    border-radius: 999px;
    background: var(--accent);
    color: #fff;
    cursor: pointer;
  }
  #pause { background: #6b7280; }
  button:disabled { opacity: .45; cursor: default; }
</style>
</head>
<body>
<div class="wrap">
  <div class="controls">
    <button id="play">▶︎  Play</button>
    <button id="pause" disabled>⏸  Pause</button>
  </div>

  <div class="stage">
    <div class="nodes">
      <div class="node" data-node="player"><span class="title">Player</span>Browser / App</div>
      <div class="node" data-node="auth"><span class="title">Auth-Service</span>Token-Pruefung</div>
      <div class="node" data-node="playback"><span class="title">Playback-Service</span>Koordination</div>
      <div class="node" data-node="cdn"><span class="title">CDN</span>Audio-Auslieferung</div>
      <div class="node" data-node="buffer">
        <span class="title">Buffer</span>Wiedergabe
        <div class="buffer-bar"><div class="buffer-fill"></div></div>
        <div class="play-icon">▶ spielt</div>
      </div>
    </div>
    <div class="packet" id="packet"></div>
  </div>

  <div class="caption" id="caption">Klick auf <strong>Play</strong>, um den technischen Ablauf Schritt fuer Schritt zu sehen.</div>

  <ol class="steps" id="steps"></ol>
</div>

<script>
  const STEPS = __STEPS_JSON__;
  const STEP_MS = 1900;

  const stage    = document.querySelector('.stage');
  const packet   = document.getElementById('packet');
  const caption  = document.getElementById('caption');
  const playBtn  = document.getElementById('play');
  const pauseBtn = document.getElementById('pause');
  const nodes    = {};
  document.querySelectorAll('.node').forEach(n => nodes[n.dataset.node] = n);

  // Schrittliste aufbauen
  const stepsEl = document.getElementById('steps');
  STEPS.forEach((s, i) => {
    const li = document.createElement('li');
    li.innerHTML = '<span class="num">' + (i + 1) + '</span><span>' + s.caption + '</span>';
    li.id = 'step-' + i;
    stepsEl.appendChild(li);
  });

  function centerOf(node) {
    const r = node.getBoundingClientRect();
    const s = stage.getBoundingClientRect();
    return { x: r.left - s.left + r.width / 2, y: r.top - s.top + r.height / 2 };
  }

  function resetVisuals() {
    Object.values(nodes).forEach(n => n.classList.remove('active', 'playing'));
    nodes.buffer.querySelector('.buffer-fill').style.width = '0%';
    packet.style.opacity = '0';
    STEPS.forEach((_, i) => {
      document.getElementById('step-' + i).classList.remove('done', 'current');
    });
  }

  function applyStep(i) {
    const step = STEPS[i];

    // Schrittliste hervorheben
    STEPS.forEach((_, k) => {
      const li = document.getElementById('step-' + k);
      li.classList.toggle('current', k === i);
      li.classList.toggle('done', k < i);
    });

    caption.innerHTML = '<strong>Schritt ' + (i + 1) + ':</strong> ' + step.caption;

    // Stationen hervorheben
    Object.entries(nodes).forEach(([id, n]) => {
      n.classList.toggle('active', step.active.includes(id));
      n.classList.toggle('playing', !!step.playing && id === 'buffer');
    });

    if (typeof step.buffer === 'number') {
      nodes.buffer.querySelector('.buffer-fill').style.width = step.buffer + '%';
    }

    // Datenpaket von "from" nach "to" bewegen
    const a = centerOf(nodes[step.from]);
    const b = centerOf(nodes[step.to]);
    packet.textContent = step.packet;

    // Startposition ohne Animation setzen ...
    packet.style.transition = 'none';
    packet.style.left = a.x + 'px';
    packet.style.top  = a.y + 'px';
    packet.style.opacity = '0';

    // ... dann zum Ziel animieren
    requestAnimationFrame(() => {
      packet.style.transition = '';
      packet.style.opacity = '1';
      packet.style.left = b.x + 'px';
      packet.style.top  = b.y + 'px';
    });
  }

  let timer = null;   // aktiver setInterval-Handle (null => pausiert / gestoppt)
  let i = 0;          // aktueller Schritt-Index
  let started = false;

  function startTimer() {
    stopTimer();
    timer = setInterval(tick, STEP_MS);
  }

  function stopTimer() {
    if (timer) { clearInterval(timer); timer = null; }
  }

  function tick() {
    i++;
    if (i >= STEPS.length) {
      stopTimer();
      started = false;
      packet.style.opacity = '0';
      document.getElementById('step-' + (STEPS.length - 1)).classList.add('done');
      playBtn.disabled = false;
      playBtn.textContent = '↻  Wiederholen';
      pauseBtn.disabled = true;
      pauseBtn.textContent = '⏸  Pause';
      return;
    }
    applyStep(i);
  }

  function run() {
    started = true;
    resetVisuals();
    i = 0;
    applyStep(i);
    playBtn.disabled = true;
    playBtn.textContent = '▶︎  Play';
    pauseBtn.disabled = false;
    pauseBtn.textContent = '⏸  Pause';
    startTimer();
  }

  function togglePause() {
    if (!started) return;
    if (timer) {
      stopTimer();
      pauseBtn.textContent = '▶︎  Weiter';
    } else {
      startTimer();
      pauseBtn.textContent = '⏸  Pause';
    }
  }

  playBtn.addEventListener('click', run);
  pauseBtn.addEventListener('click', togglePause);
</script>
</body>
</html>
""".replace("__STEPS_JSON__", steps_json)


def render_playback_animation() -> None:
    """Rendert die Play-Ablauf-Animation im Streamlit-Frontend."""
    components.html(_build_html(), height=_COMPONENT_HEIGHT, scrolling=False)
