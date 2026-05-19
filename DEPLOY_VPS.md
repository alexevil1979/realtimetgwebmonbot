# Деплой на VPS (Ubuntu 22.04)

Репозиторий: https://github.com/alexevil1979/realtimetgwebmonbot

## 1. Подготовка сервера

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git curl

# Docker
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER
newgrp docker
```

## 2. Клонирование и настройка

```bash
cd ~
git clone https://github.com/alexevil1979/realtimetgwebmonbot.git
cd realtimetgwebmonbot

cp .env.example .env
nano .env
```

Обязательно измените в `.env`:

```env
SECRET_KEY=длинная-случайная-строка
ADMIN_USERNAME=admin
ADMIN_PASSWORD=надёжный-пароль
```

## 3. Запуск (Docker, рекомендуется)

```bash
docker compose up -d --build
```

- Веб-интерфейс: `http://IP_СЕРВЕРА:8000`
- `web` — UI, `worker` — проверки серверов

Только один контейнер (UI + планировщик):

```bash
docker compose up -d --build web
```

Логи:

```bash
docker compose logs -f
```

## 4. Запуск без Docker (Python)

```bash
sudo apt install -y python3.11 python3.11-venv
cd ~/realtimetgwebmonbot
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env && nano .env
mkdir -p data

# systemd (фон)
sudo tee /etc/systemd/system/uptime-monitor.service << 'EOF'
[Unit]
Description=Uptime Monitor
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/realtimetgwebmonbot
Environment=PATH=/home/ubuntu/realtimetgwebmonbot/.venv/bin
ExecStart=/home/ubuntu/realtimetgwebmonbot/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now uptime-monitor
```

## 5. Firewall и Nginx (опционально)

```bash
sudo ufw allow OpenSSH
sudo ufw allow 8000/tcp
sudo ufw enable
```

За reverse-proxy (HTTPS):

```bash
sudo apt install -y nginx certbot python3-certbot-nginx
sudo nano /etc/nginx/sites-available/uptime
```

```nginx
server {
    listen 80;
    server_name monitor.example.com;
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/uptime /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
sudo certbot --nginx -d monitor.example.com
```

## 6. Обновление

```bash
cd ~/realtimetgwebmonbot
git pull
docker compose up -d --build
```
