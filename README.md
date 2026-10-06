<div align="center">

<a href="https://github.com/Shreyashg07/Typo_game">

<img src="./Typo_%20Comic%20Honeypot%20Typing%20Adventure.png" alt="TYPE!POW! - Comic Honeypot Typing Adventure" width="100%">

</a>

<br>

# 💥 [TYPE!POW! — Honeypot Typing Adventure](https://github.com/Shreyashg07/Typo_game)

### A comic-style WPM showdown built as a single Flask app

**Type fast. Hit hard. Watch the logs.**

<br>

[![🌐 Live Game](https://img.shields.io/badge/🌐_LIVE_GAME-Play_Now-FF3B30?style=for-the-badge)](https://typo-game-4p3v.onrender.com)
[![💻 Source Code](https://img.shields.io/badge/💻_SOURCE_CODE-GitHub-181717?style=for-the-badge&logo=github)](https://github.com/Shreyashg07/Typo_game)
[![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-000000?style=flat-square&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![React](https://img.shields.io/badge/React-61DAFB?style=flat-square&logo=react&logoColor=black)](https://react.dev/)
[![Render](https://img.shields.io/badge/Render-46E3B7?style=flat-square&logo=render&logoColor=black)](https://render.com/)

</div>

---

# 🎯 About the Project

**TYPE!POW!** is a comic-book-styled typing speed game (WPM showdown) with a hidden twist: every finished session is logged by the backend, and an admin panel lets you review the collected data.

The project was originally built as a **React/Vite frontend + Flask backend**.. This repository contains the **merged version**: one Flask app, zero build steps, deployable to Render in minutes.

---

# ✨ Features

- ⌨️ Fast-paced typing game with WPM tracking
- 💥 Comic-style "POW!" visual theme
- 🍯 Honeypot-style session logging on game completion
- 🔐 Admin panel to view stored sessions
- 🩺 Health-check endpoint for uptime monitoring
- 📦 Single-file app — frontend and backend in `app.py`
- 🚫 No npm, no build step, no database required

---

# 🔄 What Changed in the Merged Version

| Before | After |
|---|---|
| React/Vite frontend + separate Flask backend | One Flask app |
| `npm install` and build step | No build step |
| `VITE_API_BASE` environment variable | Removed — API calls go to `/api/...` on the same origin |
| Two deployments | One deployment |

How it works now:

- The React frontend is embedded directly in `app.py` as a raw HTML string.
- JSX is compiled in the browser via `@babel/standalone` (loaded from `unpkg.com`).
- React and ReactDOM are loaded from the unpkg CDN.
- Flask serves both the API (`/api/*`) and the SPA (`/*`).

---

# 🏗️ Architecture

```text
                     ┌───────────────────────┐
                     │      Web Browser      │
                     │  React SPA (in-browser│
                     │   Babel compilation)  │
                     └───────────┬───────────┘
                                 │
                                 ▼
                     ┌───────────────────────┐
                     │      Flask App        │
                     │       (app.py)        │
                     └───────────┬───────────┘
                                 │
        ┌────────────────┬───────┴────────┬─────────────────┐
        ▼                ▼                ▼                 ▼
 ┌─────────────┐  ┌─────────────┐  ┌──────────────┐  ┌─────────────┐
 │     GET /   │  │ /api/health │  │  /api/log    │  │  /api/logs  │
 │  Game SPA   │  │ Health check│  │ Save session │  │ Admin view  │
 └─────────────┘  └─────────────┘  └──────┬───────┘  └──────┬──────┘
                                          │                 │
                                          ▼                 ▼
                                   ┌──────────────────────────────┐
                                   │   sessions.jsonl (log file)  │
                                   └──────────────────────────────┘
```

---

# 🛠️ Technology Stack

| Component | Technology |
|---|---|
| Backend | Python |
| Web Framework | Flask |
| Production Server | Gunicorn |
| Frontend | React (via CDN) |
| JSX Compilation | `@babel/standalone` (in-browser) |
| Styling | CSS3 |
| Storage | JSON Lines file (`sessions.jsonl`) |
| Deployment | Render |

---

# 📁 Project Structure

```text
flask-app/
│
├── app.py             # Flask routes + full HTML/CSS/JS frontend
├── requirements.txt   # Python dependencies
├── Procfile           # Process definition (gunicorn app:app)
└── render.yaml        # Render service configuration
```

---

# ⚙️ Local Development

## 1. Clone the Repository

```bash
git clone https://github.com/Shreyashg07/Typo_game.git

cd Typo_game
```

## 2. Install Dependencies

```bash
pip install -r requirements.txt
```

## 3. Start the App

```bash
python app.py
```

## 4. Open in Browser

| Page | URL |
|---|---|
| Typing game | `http://localhost:5000` |
| Admin panel | `http://localhost:5000/#admin` |

---

# 🌐 Deploy to Render

1. Push this folder to a GitHub/GitLab repository.
2. In Render, choose **New → Web Service** and connect your repository.
3. Render auto-detects `render.yaml` and configures the service:
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `gunicorn app:app`
4. Set environment variables in the Render dashboard (or edit `render.yaml`).

## 🔧 Environment Variables

| Variable | Description | Default |
|---|---|---|
| `ADMIN_USER` | Admin panel username | `admin` |
| `ADMIN_PASS` | Admin panel password | `H@cker123` ⚠️ **change this!** |
| `LOG_FILE` | Path to the session log file | `/tmp/sessions.jsonl` |

> **Note:** Render's free tier uses an **ephemeral filesystem**. `/tmp/sessions.jsonl` is wiped on every deploy or restart. Attach a **Render Disk** or use a database (e.g. **Render Postgres**) for persistent storage.

---

# 🔌 API Routes

| Method | Route | Description |
|---|---|---|
| `GET` | `/` | The typing game (SPA) |
| `GET` | `/#admin` | Admin panel (hash route, same page) |
| `GET` | `/api/health` | Health check |
| `POST` | `/api/log` | Log a session (called by the game on finish) |
| `GET` | `/api/logs?user=&pass=` | View stored sessions (admin only) |

---

# 🍯 The Honeypot Angle

TYPE!POW! looks like a harmless typing game, but it quietly records session data whenever a round finishes. This makes it a handy sandbox for exploring:

- How applications collect and store client-side telemetry
- How exposed admin routes attract probing and brute-force attempts
- Why default credentials are dangerous
- How lightweight logging (JSONL) can support basic monitoring and analysis

---

# 🛡️ Security Notes

This project is a lightweight demo. Before running it anywhere public, consider the following:

- **Change `ADMIN_PASS` immediately.** The default is publicly documented.
- **Avoid credentials in query strings.** `/api/logs?user=&pass=` can leak secrets into server logs, browser history and proxies. Prefer an `Authorization` header or a proper login/session flow.
- **Add rate limiting** to the admin endpoint to slow brute-force attempts.
- **Use HTTPS only** (Render provides this by default).
- **Persist logs safely** with a Render Disk or database, and avoid logging more personal data than necessary.
- **Pin CDN versions** (React, ReactDOM, Babel) and consider Subresource Integrity (SRI) hashes.

---

# ⚠️ Educational Use Only

This project is intended for learning and demonstration. Only deploy and test it on systems you own or have explicit permission to use. Do not use it to collect data from people without their knowledge and consent.

---

# 👨‍💻 Author

<div align="center">

### Shreyash Ghare

Cybersecurity Researcher • Bug Hunter • VAPT • DFIR

[GitHub](https://github.com/Shreyashg07)

</div>

---

# ⭐ Support

If you enjoyed TYPE!POW!, consider giving the repository a ⭐.

<div align="center">

**Type → Score → Log → Learn**

### 💥 TYPE!POW! — Comic Honeypot Typing Adventure

</div>
