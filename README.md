# Uptime Monitor

Лёгкий сервис мониторинга доступности HTTP-серверов. FastAPI + Jinja2 + SQLite (Tortoise ORM) + APScheduler.

## Возможности

- Авторизация (один администратор, пароль с bcrypt, cookie-сессия)
- CRUD серверов с индивидуальным интервалом проверки
- HTTP GET, статусы 200–399 = OK, сохранение response time
- История до 60 проверок на сервер
- Uptime % за 24 часа и 7 дней
- Telegram-уведомления при Down/Up с настраиваемым cooldown
- Тёмная/светлая тема, responsive UI (Bootstrap 5)

## Быстрый старт

```bash
cd testservers
python -m venv .venv
.venv\Scripts\activate   # Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env   # Linux: cp .env.example .env
# Отредактируйте SECRET_KEY и ADMIN_PASSWORD в .env
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Откройте http://localhost:8000 — логин по умолчанию `admin` / `admin` (смените после первого входа через БД или пересоздайте пользователя).

## Docker

```bash
cp .env.example .env
docker compose up -d --build
```

По умолчанию UI на **http://127.0.0.1:9080** (не занимает 80/443 — совместимо с [Hiddify Manager](https://hiddify.com/manager/)). См. [DEPLOY_VPS.md](DEPLOY_VPS.md).

**Рядом с Hiddify (один контейнер, мало RAM):**

```bash
docker compose -f docker-compose.single.yml up -d --build
```

- `web` + `worker` — два контейнера; `docker-compose.single.yml` — всё в одном

Для одного контейнера через основной compose:

```bash
docker compose up -d web
```

## Структура

```
app/
  main.py          # FastAPI + lifespan + scheduler
  worker.py        # Отдельный worker
  config.py
  database.py
  bootstrap.py
  models/
  routers/
  services/        # checker, telegram, scheduler, auth
  templates/
  static/
```

## Переменные окружения

| Переменная | Описание |
|------------|----------|
| `SECRET_KEY` | Ключ подписи сессии |
| `DATABASE_URL` | SQLite URL (по умолчанию `./data/uptime.db`) |
| `ADMIN_USERNAME` | Логин при первом запуске |
| `ADMIN_PASSWORD` | Пароль при первом запуске |
| `LOG_LEVEL` | INFO, DEBUG, … |

Настройки Telegram хранятся в БД (страница /settings).

## Healthcheck

`GET /health` — публичный endpoint без авторизации.
