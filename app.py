"""
TYPE!POW! — Single-file Flask app (API + frontend bundled)
Deploy to Render as a single Python web service — no separate static site needed.
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)

app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

CORS(app, resources={r"/api/*": {"origins": "*"}})

LOG_FILE = Path(os.environ.get("LOG_FILE", "/tmp/sessions.jsonl"))
ADMIN_USER = os.environ.get("ADMIN_USER", "admin")
ADMIN_PASS = os.environ.get("ADMIN_PASS", "H@cker123")


def client_ip() -> str:
    fwd = request.headers.get("X-Forwarded-For", "")
    if fwd:
        return fwd.split(",")[0].strip()
    return request.remote_addr or "unknown"


@app.get("/api/health")
def health():
    return jsonify(status="ok")


@app.post("/api/log")
def log_session():
    body = request.get_json(silent=True) or {}
    username = (body.get("username") or "").strip()[:40] or "anonymous"
    record = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "username": username,
        "ip": client_ip(),
        "user_agent": request.headers.get("User-Agent", ""),
        "accept_language": request.headers.get("Accept-Language", ""),
        "referer": request.headers.get("Referer", ""),
        "wpm": body.get("wpm"),
        "accuracy": body.get("accuracy"),
        "duration_s": body.get("duration_s"),
        "consent": bool(body.get("consent")),
    }
    if not record["consent"]:
        return jsonify(ok=False, reason="consent_required"), 403
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
    return jsonify(ok=True, ip=record["ip"])


@app.get("/api/logs")
def view_logs():
    if request.args.get("user") != ADMIN_USER or request.args.get("pass") != ADMIN_PASS:
        return jsonify(ok=False, reason="unauthorized"), 401
    if not LOG_FILE.exists():
        return jsonify(ok=True, count=0, sessions=[])
    rows = [
        json.loads(line)
        for line in LOG_FILE.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    return jsonify(ok=True, count=len(rows), sessions=rows[-200:])


HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Bangers&family=Nunito:wght@700;900&display=swap" rel="stylesheet" />
  <script src="https://unpkg.com/react@18.3.1/umd/react.production.min.js"></script>
  <script src="https://unpkg.com/react-dom@18.3.1/umd/react-dom.production.min.js"></script>
  <title>TYPE!POW! — WPM Showdown</title>
  <style>
:root{--ink:#1a1a1a;--paper:#fff7e6;--pop:#ffd23f;--hero:#2d6cdf;--villain:#ff5e5b}
*{box-sizing:border-box}
html,body,#root{height:100%;margin:0}
body{font-family:"Nunito",system-ui,sans-serif;color:var(--ink);background:var(--villain)}
.stage{position:relative;min-height:100%;display:grid;place-items:center;padding:24px 16px;overflow:hidden}
.backdrop{position:fixed;inset:0;width:100%;height:100%;z-index:0}
.panel{position:relative;z-index:1;width:min(640px,100%);background:var(--paper);border:6px solid var(--ink);border-radius:10px;box-shadow:12px 12px 0 var(--ink);padding:22px 24px 16px}
.panel--consent{text-align:center}
.hud{display:flex;align-items:center;justify-content:space-between;gap:12px}
.title{font-family:"Bangers",cursive;font-size:clamp(34px,7vw,56px);letter-spacing:2px;margin:0;line-height:.9;text-shadow:3px 3px 0 var(--pop),5px 5px 0 var(--ink);-webkit-text-stroke:1.5px var(--ink);color:var(--hero)}
.title span{color:var(--villain)}
.timer{font-family:"Bangers",cursive;font-size:clamp(26px,5vw,40px);background:var(--pop);border:4px solid var(--ink);border-radius:8px;padding:2px 12px;box-shadow:4px 4px 0 var(--ink)}
.timer[data-low="true"]{background:var(--villain);color:var(--ink);animation:pulse .5s infinite alternate}
@keyframes pulse{to{transform:scale(1.12) rotate(-2deg)}}
.character-row{position:relative;display:grid;place-items:center;margin:6px 0 4px}
.typist{width:180px;height:180px}
.typist--typing .speedlines line{animation:dash .3s linear infinite alternate}
@keyframes dash{to{opacity:.2;transform:translateX(-3px)}}
.typist--typing .hand{animation:tap .18s infinite alternate}
.typist--typing .handR{animation-delay:.09s}
@keyframes tap{to{transform:translateY(4px)}}
.typist--win{animation:bounce .4s ease}
@keyframes bounce{0%,100%{transform:translateY(0)}40%{transform:translateY(-14px) rotate(-3deg)}}
.burst-wrap{position:absolute;top:-6px;right:8px;width:120px;height:120px;transform:rotate(8deg)}
.burst-wrap--pop{animation:popin .45s cubic-bezier(.2,1.6,.4,1) both}
@keyframes popin{from{transform:rotate(8deg) scale(0)}to{transform:rotate(8deg) scale(1)}}
.burst{width:100%;height:100%}
.burst__word{font-family:"Bangers",cursive;font-size:34px;fill:var(--ink)}
.prompt,.prompt-preview{font-size:22px;line-height:1.6;font-weight:700;background:#fff;border:3px dashed var(--ink);border-radius:8px;padding:14px 16px;margin:10px 0;word-break:break-word}
.char{transition:color .05s}
.char--ok{color:var(--hero)}
.char--bad{color:var(--ink);background:#f7c1c1;border-radius:3px}
.char--cursor{background:var(--pop);border-radius:3px;animation:blink .8s step-end infinite}
@keyframes blink{50%{background:transparent}}
.hidden-input{position:absolute;opacity:0;pointer-events:none;height:1px;width:1px}
.hint{text-align:center;font-style:italic;opacity:.7;margin:4px 0 0}
.center{text-align:center}
.btn{font-family:"Bangers",cursive;font-size:clamp(20px,4vw,28px);letter-spacing:1px;color:#fff;background:var(--hero);border:4px solid var(--ink);border-radius:10px;padding:10px 22px;box-shadow:6px 6px 0 var(--ink);cursor:pointer;transition:transform .08s,box-shadow .08s}
.btn:hover{transform:translate(-2px,-2px);box-shadow:8px 8px 0 var(--ink)}
.btn:active{transform:translate(4px,4px);box-shadow:2px 2px 0 var(--ink)}
.btn:focus-visible{outline:4px solid var(--pop);outline-offset:3px}
.btn:disabled{opacity:.5;cursor:not-allowed;transform:none}
.scoreline{display:flex;align-items:baseline;justify-content:center;gap:8px}
.big{font-family:"Bangers",cursive;font-size:clamp(64px,16vw,120px);color:var(--villain);line-height:1;text-shadow:4px 4px 0 var(--ink)}
.unit{font-family:"Bangers",cursive;font-size:28px}
.subscore{font-weight:900;font-size:18px;margin:4px 0 16px}
.consent-copy{font-size:17px;line-height:1.6;margin:8px 0 20px}
.foot{margin-top:14px;text-align:center;font-size:12px;letter-spacing:.5px;text-transform:uppercase;opacity:.6}
.text-input{font-family:"Nunito",sans-serif;font-weight:900;font-size:18px;border:4px solid var(--ink);border-radius:8px;padding:10px 14px;background:#fff;outline:none}
.text-input:focus-visible{box-shadow:0 0 0 4px var(--pop)}
.text-input--big{display:block;width:100%;margin:0 auto 18px;text-align:center}
.who{text-align:center;font-weight:900;text-transform:uppercase;letter-spacing:1px;font-size:13px;margin:2px 0 0;opacity:.8}
.panel--admin{width:min(820px,100%)}
.admin-sub{text-align:center;font-weight:700;margin:2px 0 16px}
.admin-auth{display:flex;gap:10px;justify-content:center;flex-wrap:wrap}
.btn--sm{font-size:20px;padding:8px 16px;box-shadow:4px 4px 0 var(--ink)}
.admin-error{text-align:center;color:var(--villain);font-weight:900;margin-top:12px}
.admin-count{text-align:center;font-weight:900;margin:16px 0 8px}
.table-wrap{overflow-x:auto;border:4px solid var(--ink);border-radius:8px}
.cases{width:100%;border-collapse:collapse;font-weight:700;font-size:14px;background:#fff}
.cases th{background:var(--ink);color:var(--pop);font-family:"Bangers",cursive;letter-spacing:1px;font-size:16px;padding:8px 10px;text-align:left}
.cases td{padding:8px 10px;border-top:2px solid #eee}
.cases tr:nth-child(even) td{background:#fffaf0}
.cell-user{color:var(--hero);font-weight:900}
.cell-ip{font-family:monospace;color:var(--villain)}
.cell-time{font-family:monospace;font-size:12px;opacity:.7}
.empty{text-align:center;font-style:italic;opacity:.6}
.back-link{display:inline-block;margin-top:16px;font-weight:900;color:var(--hero);text-decoration:none}
.back-link:hover{text-decoration:underline}
/* tap-to-focus overlay when playing — covers whole panel so any tap refocuses */
.focus-overlay{position:absolute;inset:0;z-index:2;cursor:text}
@media(prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}}
  </style>
</head>
<body>
  <div id="root"></div>
  <script>
var h          = React.createElement;
var useState   = React.useState;
var useEffect  = React.useEffect;
var useRef     = React.useRef;
var useMemo    = React.useMemo;
var Fragment   = React.Fragment;

// ── API ───────────────────────────────────────────────────────────────────
async function logSession(payload) {
  try {
    var res = await fetch('/api/log', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    return await res.json();
  } catch(e) { return { ok: false }; }
}

async function fetchLogs(user, pass) {
  try {
    var res = await fetch('/api/logs?user=' + encodeURIComponent(user) + '&pass=' + encodeURIComponent(pass));
    return await res.json();
  } catch(e) { return { ok: false, reason: 'network_error' }; }
}

// ── SVG art ───────────────────────────────────────────────────────────────
function HalftoneBackdrop() {
  return h('svg', { className: 'backdrop', viewBox: '0 0 400 400', preserveAspectRatio: 'xMidYMid slice', 'aria-hidden': 'true' },
    h('defs', null,
      h('pattern', { id: 'dots', width: '14', height: '14', patternUnits: 'userSpaceOnUse' },
        h('circle', { cx: '3', cy: '3', r: '3', fill: '#ffd23f' })
      ),
      h('radialGradient', { id: 'vign', cx: '50%', cy: '40%', r: '75%' },
        h('stop', { offset: '0%', stopColor: '#ff5e5b' }),
        h('stop', { offset: '100%', stopColor: '#e23b3b' })
      )
    ),
    h('rect', { width: '400', height: '400', fill: 'url(#vign)' }),
    h('rect', { width: '400', height: '400', fill: 'url(#dots)', opacity: '0.35' })
  );
}

function Typist(props) {
  var mood = props.mood || 'idle';
  var browY = mood === 'win' ? 30 : mood === 'typing' ? 34 : 36;
  var mouth = mood === 'win'
    ? 'M78 78 Q100 102 122 78 Q100 88 78 78 Z'
    : mood === 'typing' ? 'M84 80 Q100 90 116 80'
    : 'M84 82 Q100 86 116 82';
  return h('svg', { className: 'typist typist--' + mood, viewBox: '0 0 200 200', role: 'img', 'aria-label': 'Comic typist' },
    mood === 'typing' && h('g', { className: 'speedlines', stroke: '#1a1a1a', strokeWidth: '4', strokeLinecap: 'round' },
      h('line', { x1:'10', y1:'60',  x2:'40',  y2:'60' }),
      h('line', { x1:'6',  y1:'100', x2:'42',  y2:'100' }),
      h('line', { x1:'10', y1:'140', x2:'40',  y2:'140' }),
      h('line', { x1:'160',y1:'60',  x2:'190', y2:'60' }),
      h('line', { x1:'158',y1:'100', x2:'194', y2:'100' }),
      h('line', { x1:'160',y1:'140', x2:'190', y2:'140' })
    ),
    h('circle', { cx:'100', cy:'70', r:'46', fill:'#ffe0bd', stroke:'#1a1a1a', strokeWidth:'5' }),
    h('path', { d:'M54 60 Q60 18 100 20 Q140 18 146 60 Q120 40 100 44 Q80 40 54 60 Z', fill:'#2b2b2b', stroke:'#1a1a1a', strokeWidth:'5', strokeLinejoin:'round' }),
    h('circle', { cx:'84', cy:'64', r:'6', fill:'#1a1a1a' }),
    h('circle', { cx:'116', cy:'64', r:'6', fill:'#1a1a1a' }),
    h('line', { x1:'74', y1:String(browY), x2:'94', y2:String(browY+6), stroke:'#1a1a1a', strokeWidth:'4', strokeLinecap:'round' }),
    h('line', { x1:'126', y1:String(browY), x2:'106', y2:String(browY+6), stroke:'#1a1a1a', strokeWidth:'4', strokeLinecap:'round' }),
    h('path', { d:mouth, fill: mood==='win' ? '#e23b3b' : 'none', stroke:'#1a1a1a', strokeWidth:'4', strokeLinecap:'round', strokeLinejoin:'round' }),
    h('path', { d:'M40 200 Q40 140 100 140 Q160 140 160 200 Z', fill:'#2d6cdf', stroke:'#1a1a1a', strokeWidth:'5' }),
    h('rect', { x:'62', y:'168', width:'76', height:'20', rx:'6', fill:'#1a1a1a' }),
    h('circle', { cx:'74', cy:'166', r:'9', fill:'#ffe0bd', stroke:'#1a1a1a', strokeWidth:'4', className:'hand handL' }),
    h('circle', { cx:'126', cy:'166', r:'9', fill:'#ffe0bd', stroke:'#1a1a1a', strokeWidth:'4', className:'hand handR' })
  );
}

function ActionBurst(props) {
  var word = props.word || 'POW!';
  var color = props.color || '#ffd23f';
  var points = [];
  for (var i = 0; i < 28; i++) {
    var r = i % 2 === 0 ? 100 : 72;
    var a = (Math.PI / 14) * i - Math.PI / 2;
    points.push((100 + r * Math.cos(a)).toFixed(2) + ',' + (100 + r * Math.sin(a)).toFixed(2));
  }
  return h('svg', { className:'burst', viewBox:'0 0 200 200', 'aria-hidden':'true' },
    h('polygon', { points:points.join(' '), fill:color, stroke:'#1a1a1a', strokeWidth:'6', strokeLinejoin:'round' }),
    h('text', { x:'100', y:'100', textAnchor:'middle', dominantBaseline:'central', className:'burst__word' }, word)
  );
}

// ── Admin Panel ───────────────────────────────────────────────────────────
function AdminPanel() {
  var _u = useState(''), user = _u[0], setUser = _u[1];
  var _p = useState(''), pass = _p[0], setPass = _p[1];
  var _d = useState(null), data = _d[0], setData = _d[1];
  var _e = useState(''), error = _e[0], setError = _e[1];
  var _l = useState(false), loading = _l[0], setLoading = _l[1];

  async function load() {
    setLoading(true); setError('');
    var res = await fetchLogs(user, pass);
    setLoading(false);
    if (res.ok) { setData(res); }
    else { setData(null); setError(res.reason === 'unauthorized' ? 'Wrong username or password.' : "Couldn't reach the API."); }
  }

  function onKey(e) { if (e.key === 'Enter') load(); }

  return h('main', { className:'stage' },
    h(HalftoneBackdrop),
    h('section', { className:'panel panel--admin' },
      h('h1', { className:'title' }, 'HQ', h('span', null, ':'), ' CASE FILES'),
      h('p', { className:'admin-sub' }, 'Stored visitor sessions (IP + username + score).'),
      h('div', { className:'admin-auth' },
        h('input', { className:'text-input', type:'text', placeholder:'username', autoComplete:'username', value:user, onChange:function(e){ setUser(e.target.value); }, onKeyDown:onKey }),
        h('input', { className:'text-input', type:'password', placeholder:'password', autoComplete:'current-password', value:pass, onChange:function(e){ setPass(e.target.value); }, onKeyDown:onKey }),
        h('button', { className:'btn btn--sm', onClick:load, disabled:loading }, loading ? 'LOADING…' : 'UNLOCK')
      ),
      error && h('p', { className:'admin-error' }, error),
      data && h(Fragment, null,
        h('p', { className:'admin-count' }, data.count + ' session(s) logged'),
        h('div', { className:'table-wrap' },
          h('table', { className:'cases' },
            h('thead', null, h('tr', null,
              h('th',null,'#'), h('th',null,'User'), h('th',null,'IP'),
              h('th',null,'WPM'), h('th',null,'Acc'), h('th',null,'When (UTC)')
            )),
            h('tbody', null,
              data.sessions.length === 0
                ? h('tr', null, h('td', { colSpan:'6', className:'empty' }, 'No one has played yet.'))
                : data.sessions.slice().reverse().map(function(s, i) {
                    return h('tr', { key:i },
                      h('td',null, data.sessions.length - i),
                      h('td',{ className:'cell-user' }, s.username || 'anonymous'),
                      h('td',{ className:'cell-ip' }, s.ip),
                      h('td',null, s.wpm != null ? s.wpm : '—'),
                      h('td',null, s.accuracy != null ? s.accuracy + '%' : '—'),
                      h('td',{ className:'cell-time' }, (s.ts||'').replace('T',' ').slice(0,19))
                    );
                  })
            )
          )
        )
      ),
      h('a', { className:'back-link', href:'#' }, '← back to the game')
    )
  );
}

// ── Game ──────────────────────────────────────────────────────────────────
var PROMPTS = [
  'The quick brown fox jumps over the lazy dog while the city sleeps.',
  'Heroes are made in the panels between the punches and the silence.',
  'Type fast type true and let the halftone dots fall where they may.',
  'Every keystroke is a tiny thunderclap echoing across the page.'
];
var DURATION = 30;
function pickPrompt() { return PROMPTS[Math.floor(Math.random() * PROMPTS.length)]; }

function useHashRoute() {
  var _h = useState(window.location.hash), hash = _h[0], setHash = _h[1];
  useEffect(function() {
    function on() { setHash(window.location.hash); }
    window.addEventListener('hashchange', on);
    return function() { window.removeEventListener('hashchange', on); };
  }, []);
  return hash;
}

function Game() {
  var _s  = useState('name'),      step     = _s[0],  setStep     = _s[1];
  var _un = useState(''),          username = _un[0], setUsername = _un[1];
  var _pr = useState(pickPrompt),  prompt   = _pr[0], setPrompt   = _pr[1];
  var _ty = useState(''),          typed    = _ty[0], setTyped    = _ty[1];
  var _tl = useState(DURATION),    timeLeft = _tl[0], setTimeLeft = _tl[1];
  var _re = useState(null),        result   = _re[0], setResult   = _re[1];

  var inputRef   = useRef(null);
  var startRef   = useRef(null);
  var finishedRef = useRef(false);   // ← prevents double-finish from timer + typing

  // ── focus helper — works on desktop AND mobile ──────────────────────────
  function focusInput() {
    var el = inputRef.current;
    if (!el) return;
    el.removeAttribute('disabled');
    el.focus();
    // On iOS, focus() alone sometimes isn't enough after a re-render.
    // A tiny rAF loop gives the DOM time to settle.
    requestAnimationFrame(function() { el.focus(); });
  }

  // ── countdown ────────────────────────────────────────────────────────────
  useEffect(function() {
    if (step !== 'playing') return;
    if (timeLeft <= 0) { finish(); return; }
    var t = setTimeout(function() { setTimeLeft(function(s) { return s - 1; }); }, 1000);
    return function() { clearTimeout(t); };
  }, [step, timeLeft]);

  // ── re-focus whenever step becomes 'playing' ────────────────────────────
  useEffect(function() {
    if (step === 'playing') { focusInput(); }
  }, [step]);

  var correctChars = useMemo(function() {
    var n = 0;
    for (var i = 0; i < typed.length; i++) if (typed[i] === prompt[i]) n++;
    return n;
  }, [typed, prompt]);

  function start() {
    finishedRef.current = false;          // reset guard
    setTyped('');
    setPrompt(pickPrompt());
    setTimeLeft(DURATION);
    setResult(null);
    setStep('playing');                   // useEffect above will call focusInput()
    startRef.current = Date.now();
  }

  function finish() {
    if (finishedRef.current) return;      // guard: only finish once per round
    finishedRef.current = true;
    var elapsed = Math.max(1, (Date.now() - startRef.current) / 1000);
    var wpm = Math.round((correctChars / 5 / elapsed) * 60);
    var accuracy = typed.length ? Math.round((correctChars / typed.length) * 100) : 0;
    var res = { wpm: wpm, accuracy: accuracy, duration_s: Math.round(elapsed) };
    setResult(res);
    setStep('done');
    logSession(Object.assign({}, res, { username: username, consent: true }));
  }

  var mood = step === 'playing' ? 'typing'
           : step === 'done' ? (result && result.wpm >= 40 ? 'win' : 'meh')
           : 'idle';
  var burstWord = !result ? 'POW!'
                : result.wpm >= 60 ? 'KAPOW!'
                : result.wpm >= 40 ? 'BAM!' : 'OOF!';

  // Step 1 – name
  if (step === 'name') {
    return h('main', { className:'stage' },
      h(HalftoneBackdrop),
      h('section', { className:'panel panel--consent' },
        h('h1', { className:'title' }, 'TYPE', h('span',null,'!'), 'POW', h('span',null,'!')),
        h('p', { className:'consent-copy' }, 'Enter your hero name to step into the ring.'),
        h('input', {
          className:'text-input text-input--big', placeholder:'your username',
          value:username, maxLength:40,
          onChange:function(e){ setUsername(e.target.value); },
          onKeyDown:function(e){ if(e.key==='Enter' && username.trim()) setStep('consent'); },
          autoFocus:true
        }),
        h('button', { className:'btn', disabled:!username.trim(), onClick:function(){ setStep('consent'); } }, 'ENTER THE RING')
      )
    );
  }

  // Step 2 – consent
  if (step === 'consent') {
    return h('main', { className:'stage' },
      h(HalftoneBackdrop),
      h('section', { className:'panel panel--consent' },
        h('h1', { className:'title' }, 'HEADS UP', h('span',null,'!')),
        h('p', { className:'consent-copy' },
          'Hey ', h('strong', null, username), '! 🕸️ ',
          'With great typing speed comes great responsibility. ',
          'Only the quickest heroes survive this challenge. ',
          'Ready to swing your fingers into action?'
        ),
        h('button', { className:'btn', onClick:function(){ setStep('ready'); } }, 'I UNDERSTAND — PLAY')
      )
    );
  }

  // Steps 3-5 – game
  return h('main', { className:'stage' },
    h(HalftoneBackdrop),
    h('section', { className:'panel' },
      h('header', { className:'hud' },
        h('h1', { className:'title' }, 'TYPE', h('span',null,'!'), 'POW', h('span',null,'!')),
        h('div', { className:'timer', 'data-low': timeLeft <= 5 ? 'true' : 'false' }, timeLeft + 's')
      ),
      h('p', { className:'who' }, 'PLAYER: ', h('strong',null,username)),
      h('div', { className:'character-row' },
        h(Typist, { mood:mood }),
        (step==='playing'||step==='done') && h('div', { className:'burst-wrap'+(step==='done'?' burst-wrap--pop':'') },
          h(ActionBurst, { word:burstWord, color: result&&result.wpm<40 ? '#ff5e5b' : '#ffd23f' })
        )
      ),

      step === 'ready' && h('div', { className:'center' },
        h('p', { className:'prompt-preview' }, prompt),
        h('button', { className:'btn', onClick:start }, 'START THE SHOWDOWN')
      ),

      step === 'playing' && h(Fragment, null,
        // invisible overlay: tapping anywhere on the panel re-focuses the input
        h('div', { className:'focus-overlay', onClick:focusInput, 'aria-hidden':'true' }),
        h('p', { className:'prompt', onClick:focusInput },
          prompt.split('').map(function(ch, i) {
            var cls = 'char';
            if (i < typed.length) cls += typed[i]===ch ? ' char--ok' : ' char--bad';
            if (i === typed.length) cls += ' char--cursor';
            return h('span', { key:i, className:cls }, ch);
          })
        ),
        h('input', {
          ref:inputRef,
          className:'hidden-input',
          value:typed,
          onChange:function(e){ setTyped(e.target.value.slice(0, prompt.length)); },
          autoComplete:'off', autoCapitalize:'off', spellCheck:'false',
          'aria-label':'Type the prompt here'
        }),
        h('p', { className:'hint' }, 'Tap the text above if keyboard disappears.')
      ),

      step === 'done' && result && h('div', { className:'center result' },
        h('div', { className:'scoreline' },
          h('span', { className:'big' }, result.wpm),
          h('span', { className:'unit' }, 'WPM')
        ),
        h('p', { className:'subscore' }, result.accuracy + '% accuracy · ' + result.duration_s + 's'),
        h('button', { className:'btn', onClick:start }, 'RUN IT BACK')
      ),

      h('footer', { className:'foot' }, 'Demo logs username + IP on finish · ethical-use project')
    )
  );
}

// ── Root ──────────────────────────────────────────────────────────────────
function App() {
  var hash = useHashRoute();
  if (hash === '#admin') return h(AdminPanel);
  return h(Game);
}

ReactDOM.createRoot(document.getElementById('root')).render(h(App));
  </script>
</body>
</html>"""


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_frontend(path):
    return render_template_string(HTML)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
