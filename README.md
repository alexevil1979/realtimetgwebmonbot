# Uptime Monitor · Realtime TG Web Mon Bot

[🇷🇺 Русская версия](README.ru.md)

Lightweight **HTTP uptime monitoring** with a web dashboard and **Telegram alerts**. Built for weak VPS, Raspberry Pi, and servers that already run **[Hiddify Manager](https://hiddify.com/manager/)** (uses port **9080**, not 80/443).

**Repository:** https://github.com/alexevil1979/realtimetgwebmonbot

---

## ☕ Support the project

If this tool saves you time or alerts — **buy the author a coffee:**

[![Buy Me a Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-support-yellow?style=for-the-badge&logo=buy-me-a-coffee)](https://buymeacoffee.com/alexevil1979)

Your support helps keep the project maintained and improved. Thank you!

---

## Features

| Area | Details |
|------|---------|
| **Monitoring** | HTTP GET checks, status **200–399 = OK**, response time stored |
| **Scheduling** | Per-server check interval (APScheduler), independent timers |
| **History** | Last 60 checks per server |
| **Dashboard** | Status, uptime % (24h / 7d), manual “check now” |
| **Telegram** | DOWN after **continuous** downtime (default 15 min), optional UP alerts, anti-spam cooldown |
| **Auth** | Single admin, bcrypt password, signed cookie session |
| **UI** | Bootstrap 5, dark/light theme, **Russian / English** |
| **Deploy** | Docker, docker-compose, optional worker, SQLite |

---

## Screenshots & access

- Web UI: `http://YOUR_IP:9080/`
- Health (no auth): `GET /health`
- Default login (change in `.env` on first deploy): `admin` / `admin`

---

## Quick start (Docker)

```bash
git clone https://github.com/alexevil1979/realtimetgwebmonbot.git
cd realtimetgwebmonbot
cp .env.example .env
# Edit SECRET_KEY, ADMIN_PASSWORD
docker compose -f docker-compose.single.yml up -d --build
```

With **Hiddify** on the same host, see [DEPLOY_VPS.md](DEPLOY_VPS.md).

---

## Quick start (local Python)

```bash
python3.11 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --host 0.0.0.0 --port 9080
```

---

## Telegram setup

1. Create a bot via [@BotFather](https://t.me/BotFather) → copy **Bot Token**
2. Open your bot in Telegram → press **Start**
3. Get **Chat ID** from [@userinfobot](https://t.me/userinfobot) (e.g. `640075202`)
4. In the web UI: **Settings** → paste token & chat ID → **Test Telegram** → **Save**

**DOWN alerts** are sent only if the server stays unreachable for the configured duration (default **15 minutes** in a row), not on the first failed ping.

---

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | — | Session signing key (required in production) |
| `DATABASE_URL` | `./data/uptime.db` | SQLite path |
| `ADMIN_USERNAME` | `admin` | Initial admin (created once) |
| `ADMIN_PASSWORD` | `admin` | Initial password |
| `DEFAULT_LANG` | `ru` | Default UI language (`ru` / `en`) |
| `UPTIME_BIND` | `0.0.0.0` | Docker host bind |
| `UPTIME_PORT` | `9080` | Docker host port |
| `SCHEDULER_ENABLED` | `true` | Set `false` on web container if using separate worker |

Telegram token, chat ID, alert thresholds are stored in the **database** (Settings page).

---

## Project structure

```
app/
  main.py              # FastAPI app + scheduler lifecycle
  worker.py            # Scheduler-only process
  i18n/                # ru / en translations
  models/              # User, Server, Check, AppSetting
  routers/             # auth, dashboard, servers, settings, i18n
  services/            # checker, telegram, scheduler, auth
  templates/           # Jinja2 HTML
  static/              # CSS, JS (theme)
```

---

## Docker services

| Command | Description |
|---------|-------------|
| `docker compose up -d --build` | Web (no scheduler) + worker |
| `docker compose -f docker-compose.single.yml up -d --build` | Single container (recommended on small VPS) |

---

## Language / UI

Switch **RU / EN** in the top bar on any page. Language is stored in a cookie and used for Telegram alert text.

---

## License & contributions

Issues and pull requests are welcome on GitHub.

**Enjoying the project?** [☕ Buy me a coffee](https://buymeacoffee.com/alexevil1979)
