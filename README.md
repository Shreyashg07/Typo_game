# TYPE!POW! — Single Flask App

The original project was split into a React/Vite frontend + Flask backend.
This is the merged version: **one Flask app, zero build steps**, ready to
deploy on Render in minutes.

## What changed

- The React frontend is embedded directly in `app.py` as a raw HTML string.
- JSX is compiled in-browser via `@babel/standalone` (loaded from unpkg.com).
- React and ReactDOM are loaded from unpkg CDN — no `npm install` needed.
- The Flask app serves both the API (`/api/*`) and the SPA (`/*`).
- `VITE_API_BASE` is gone — API calls go to `/api/...` on the same origin.

## Project layout

```
flask-app/
├── app.py            ← everything: Flask routes + full HTML/CSS/JS frontend
├── requirements.txt
├── Procfile
└── render.yaml
```

## Deploy to Render

1. Push this folder to a GitHub/GitLab repo.
2. In Render → **New Web Service** → connect your repo.
3. Render will auto-detect the `render.yaml` and configure the service.
   - Build: `pip install -r requirements.txt`
   - Start: `gunicorn app:app`
4. Set env vars in Render dashboard (or edit `render.yaml`):
   - `ADMIN_USER` — admin panel username (default: `admin`)
   - `ADMIN_PASS` — admin panel password (default: `H@cker123`) ← **change this!**
   - `LOG_FILE`   — path to session log (default: `/tmp/sessions.jsonl`)

> **Note:** Render's free tier has an ephemeral filesystem — `/tmp/sessions.jsonl`
> resets on every deploy/restart. Attach a **Render Disk** or use a database
> (e.g. Render Postgres) for persistent storage.

## Local dev

```bash
pip install -r requirements.txt
python app.py
# visit http://localhost:5000
# admin panel: http://localhost:5000/#admin
```

## Routes

| Route | Description |
|---|---|
| `GET /` | The typing game (SPA) |
| `GET /#admin` | Admin panel (hash route, same page) |
| `GET /api/health` | Health check |
| `POST /api/log` | Log a session (called by the game on finish) |
| `GET /api/logs?user=&pass=` | View stored sessions (admin only) |
