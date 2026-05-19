# Uptime Monitor · Мониторинг серверов с Telegram

[🇬🇧 English version](README.md)

Лёгкий **HTTP uptime-мониторинг** с веб-панелью и **уведомлениями в Telegram**. Рассчитан на слабый VPS, Raspberry Pi и серверы с уже установленным **[Hiddify Manager](https://hiddify.com/manager/)** (порт **9080**, без захвата 80/443).

**Репозиторий:** https://github.com/alexevil1979/realtimetgwebmonbot

---

## ☕ Поддержать проект

Если сервис помогает следить за сайтами и вовремя ловить падения — **угостите автора кофе:**

[![Buy Me a Coffee](https://img.shields.io/badge/Угостить%20кофе-поддержать-yellow?style=for-the-badge&logo=buy-me-a-coffee)](https://buymeacoffee.com/alexevil1979)

Любая сумма мотивирует развивать проект. Спасибо!

---

## Возможности

| Раздел | Описание |
|--------|----------|
| **Мониторинг** | HTTP GET, коды **200–399 = OK**, время ответа |
| **Расписание** | Свой интервал проверки на каждый сервер (APScheduler) |
| **История** | До 60 последних проверок на сервер |
| **Дашборд** | Статус, uptime % за 24ч и 7д, ручная проверка |
| **Telegram** | DOWN после **непрерывного** простоя (по умолчанию 15 мин), опционально UP, защита от спама |
| **Вход** | Один администратор, bcrypt, cookie-сессия |
| **Интерфейс** | Bootstrap 5, тёмная/светлая тема, **русский / английский** |
| **Деплой** | Docker, docker-compose, worker, SQLite |

---

## Доступ

- Веб: `http://ВАШ_IP:9080/` (например `http://203.161.39.40:9080/`)
- Health без авторизации: `GET /health`
- Логин по умолчанию (смените в `.env`): `admin` / `admin`

---

## Быстрый старт (Docker)

```bash
git clone https://github.com/alexevil1979/realtimetgwebmonbot.git
cd realtimetgwebmonbot
cp .env.example .env
# SECRET_KEY, ADMIN_PASSWORD — обязательно сменить
docker compose -f docker-compose.single.yml up -d --build
sudo ufw allow 9080/tcp   # если включён firewall
```

Подробно с **Hiddify**: [DEPLOY_VPS.md](DEPLOY_VPS.md).

---

## Быстрый старт (Python)

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --host 0.0.0.0 --port 9080
```

---

## Настройка Telegram

1. Бот в [@BotFather](https://t.me/BotFather) → **Bot Token**
2. Откройте бота → **Start**
3. **Chat ID** в [@userinfobot](https://t.me/userinfobot) (например `640075202`)
4. В панели: **Настройки** → токен и Chat ID → **Тест Telegram** → **Сохранить**

**DOWN** приходит только если сервер **подряд недоступен** заданное время (по умолчанию **15 минут**), а не с первой же ошибки.

---

## Переменные окружения

| Переменная | По умолчанию | Описание |
|------------|--------------|----------|
| `SECRET_KEY` | — | Ключ сессии |
| `DATABASE_URL` | `./data/uptime.db` | Путь к SQLite |
| `ADMIN_USERNAME` | `admin` | Первый админ |
| `ADMIN_PASSWORD` | `admin` | Пароль |
| `DEFAULT_LANG` | `ru` | Язык UI (`ru` / `en`) |
| `UPTIME_BIND` | `0.0.0.0` | Адрес привязки Docker |
| `UPTIME_PORT` | `9080` | Порт |
| `SCHEDULER_ENABLED` | `true` | Планировщик в контейнере web |

Токен Telegram, Chat ID и пороги алертов — в **базе** (страница «Настройки»).

---

## Структура проекта

```
app/
  main.py
  worker.py
  i18n/           # переводы ru / en
  models/
  routers/
  services/
  templates/
  static/
```

---

## Язык интерфейса

Переключатель **RU / EN** в шапке. Язык сохраняется в cookie и используется для текстов Telegram-уведомлений.

---

## Обновление на сервере

```bash
cd ~/realtimetgwebmonbot
git pull
docker compose -f docker-compose.single.yml up -d --build
```

---

## Обратная связь

Баги и предложения — в [Issues](https://github.com/alexevil1979/realtimetgwebmonbot/issues) на GitHub.

**Нравится проект?** [☕ Угостить кофе](https://buymeacoffee.com/alexevil1979)
