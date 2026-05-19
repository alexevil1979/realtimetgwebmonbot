# Деплой на VPS (Ubuntu 22.04)

Репозиторий: https://github.com/alexevil1979/realtimetgwebmonbot

---

## Уже стоит Hiddify Manager

Hiddify обычно занимает **80**, **443** и свой nginx/Caddy. Монитор **не трогает** эти порты.

| Что | Hiddify | Uptime Monitor |
|-----|---------|----------------|
| 80 / 443 | Панель, прокси | **Не используем** |
| Docker | Уже установлен | Тот же Docker, отдельный `docker compose` |
| Доступ к UI | Домен в панели | `http://IP:9080/` (порт 9080, не 80/443) |

### Быстрый старт (рядом с Hiddify)

```bash
cd ~
git clone https://github.com/alexevil1979/realtimetgwebmonbot.git
cd realtimetgwebmonbot
cp .env.example .env
nano .env   # SECRET_KEY, ADMIN_PASSWORD

# Один контейнер — меньше нагрузка на VPS
docker compose -f docker-compose.single.yml up -d --build
```

Проверка:

```bash
curl -s http://127.0.0.1:9080/health
# {"status":"ok"}
```

Откройте в браузере: **http://203.161.39.40:9080/** (подставьте IP вашего VPS).

Firewall (если включён ufw):

```bash
sudo ufw allow 9080/tcp
sudo ufw status
```

В `.env` уже по умолчанию:

```env
UPTIME_BIND=0.0.0.0
UPTIME_PORT=9080
```

### Опционально: HTTPS через поддомен Hiddify

1. DNS: `monitor.ваш-домен.ru` → IP VPS  
2. В [Hiddify](https://hiddify.com/manager/configuration-and-advanced-settings/How-to-configure-Hiddify-panel-properly/) — прокси на `http://127.0.0.1:9080`  
3. Тогда снаружи будет HTTPS, а `:9080` можно не открывать в ufw

### Чего не делать на VPS с Hiddify

- Не ставить второй системный **nginx** / не занимать **80/443**
- Не запускать `curl get.docker.com`, если Docker уже есть
- Не менять конфиги Hiddify вручную без необходимости
- Не открывать в ufw порты, которые уже обслуживает Hiddify

### Логи и обновление

```bash
cd ~/realtimetgwebmonbot
docker compose -f docker-compose.single.yml logs -f
git pull
docker compose -f docker-compose.single.yml up -d --build
```

Два контейнера (web + worker), если нужна разгрузка:

```bash
docker compose up -d --build
```

---

## Чистый VPS (без Hiddify)

### 1. Подготовка

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git curl
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER
newgrp docker
```

### 2. Клонирование

```bash
git clone https://github.com/alexevil1979/realtimetgwebmonbot.git
cd realtimetgwebmonbot
cp .env.example .env
nano .env
```

### 3. Запуск

```bash
docker compose up -d --build
```

По умолчанию UI: `http://127.0.0.1:9080` (или задайте `UPTIME_BIND=0.0.0.0` в `.env`).

### 4. Python без Docker

```bash
sudo apt install -y python3.11 python3.11-venv
python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 127.0.0.1 --port 9080
```

---

## Переменные Docker

| Переменная | По умолчанию | Описание |
|------------|--------------|----------|
| `UPTIME_BIND` | `0.0.0.0` | Слушать на всех интерфейсах (`http://IP:9080/`) |
| `UPTIME_PORT` | `9080` | Внешний порт хоста |

Задаются в `.env` в корне проекта или в shell перед `docker compose`.
