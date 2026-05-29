# GostChecker: backend + VK Mini App

Проект состоит из двух частей:

- `server.py` - FastAPI backend для классификации, валидации и исправления DOCX.
- `mini-app/` - VK Mini Apps frontend на React + VKUI.

Секреты и `.env`-файлы не нужно пересоздавать при обновлении кода. Держи реальные значения в `mini-app/.env.production` и серверных env-файлах на машине, а в git коммить только примерные шаблоны.

## Локальный запуск

Backend:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn server:app --host 127.0.0.1 --port 8000
```

Frontend:

```bash
cd mini-app
npm ci
npm run dev -- --port 5173
```

В dev-режиме frontend сам ходит на `http://127.0.0.1:8000`, если `VITE_API_BASE_URL` не задан.

## API-сценарий frontend

1. Пользователь загружает `.docx`.
2. Frontend вызывает `POST /api/classify`.
3. Backend возвращает тип документа и рекомендуемый профиль `LIGHT`, `MEDIUM` или `HARD`.
4. Кнопка `ВАЛИДАЦИЯ ДОКУМЕНТА` вызывает `POST /api/run?mode=validate&scope_id=validate_all_key`.
5. Дашборд показывает процент корректности и список нарушений.
6. Фиксированная кнопка `ЗАПУСТИТЬ ИСПРАВЛЕНИЕ` вызывает `POST /api/run?mode=correct&scope_id=correct_all`.
7. Backend возвращает `fixed_file` с `base64`, именем файла и текстовым preview исправленного DOCX.

## Деплой backend на TimeWeb Ubuntu 24

Подключись к серверу по SSH и поставь системные пакеты:

```bash
apt update
apt install -y python3-venv python3-pip git nginx
```

Размести проект, например в `/opt/gostchecker`:

```bash
mkdir -p /opt/gostchecker
cd /opt/gostchecker
git clone <URL_ТВОЕГО_РЕПОЗИТОРИЯ> .
python3 -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Создай отдельный env-файл, который не будет затираться при `git pull`:

```bash
mkdir -p /etc/gostchecker
nano /etc/gostchecker/backend.env
```

Пока backend не требует обязательных переменных. Файл можно оставить почти пустым и позже добавить туда настройки БД, домена или лимитов.

Systemd-сервис `/etc/systemd/system/gost-api.service`:

```ini
[Unit]
Description=GostChecker FastAPI
After=network.target

[Service]
WorkingDirectory=/opt/gostchecker
EnvironmentFile=-/etc/gostchecker/backend.env
ExecStart=/opt/gostchecker/.venv/bin/python -m uvicorn server:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

Запусти сервис:

```bash
systemctl daemon-reload
systemctl enable --now gost-api
systemctl status gost-api
```

Если в статусе видно `active (running)`, backend уже работает внутри сервера на `127.0.0.1:8000`. Проверь это прямо на сервере:

```bash
curl http://127.0.0.1:8000/api/health
```

Ожидаемый смысл ответа: `status` должен быть `ok`. Если ответа нет, сначала смотри backend-логи:

```bash
journalctl -u gost-api -n 100 --no-pager
```

## Настройка Nginx reverse proxy

Backend слушает только внутренний адрес `127.0.0.1:8000`. Это правильно: наружу его должен отдавать Nginx. Nginx будет принимать запросы на публичном домене, например `api.example.ru`, и прокидывать их в FastAPI.

Перед настройкой проверь две вещи:

1. У тебя есть домен или поддомен для API, например `api.example.ru`.
2. В DNS у этого домена создана `A`-запись на IPv4 твоего сервера.

Проверить, куда сейчас указывает домен, можно так:

```bash
dig +short api.example.ru
```

Если `dig` не установлен:

```bash
apt install -y dnsutils
dig +short api.example.ru
```

В ответе должен появиться IP твоего сервера. Если ответа нет или IP другой, сначала поправь DNS у регистратора/в панели домена и подожди обновления.

### 1. Создай конфиг Nginx

Открой новый файл:

```bash
nano /etc/nginx/sites-available/gost-api
```

Вставь конфиг. Замени `api.example.ru` на свой реальный домен:

```nginx
server {
    listen 80;
    server_name api.example.ru;

    client_max_body_size 32m;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300;
    }
}
```

Сохрани файл:

- `Ctrl + O`
- `Enter`
- `Ctrl + X`

### 2. Включи сайт в Nginx

Создай символическую ссылку из `sites-available` в `sites-enabled`:

```bash
ln -s /etc/nginx/sites-available/gost-api /etc/nginx/sites-enabled/gost-api
```

Если команда скажет, что файл уже существует, это не страшно. Значит сайт уже включен. Можно проверить так:

```bash
ls -l /etc/nginx/sites-enabled/
```

Если в Nginx включен дефолтный сайт и он мешает, его можно отключить:

```bash
rm -f /etc/nginx/sites-enabled/default
```

### 3. Проверь конфиг и перезагрузи Nginx

```bash
nginx -t
systemctl reload nginx
systemctl status nginx
```

`nginx -t` должен написать примерно:

```text
syntax is ok
test is successful
```

Если там ошибка, Nginx не перезагружай, сначала исправь строку, которую он покажет.

### 4. Проверь API через Nginx

Сначала проверка backend напрямую:

```bash
curl http://127.0.0.1:8000/api/health
```

Потом проверка через домен:

```bash
curl http://api.example.ru/api/health
```

Если первый `curl` работает, а второй нет, проблема почти точно в Nginx, DNS или открытых портах.

Что проверить:

```bash
systemctl status nginx
journalctl -u nginx -n 100 --no-pager
nginx -T | grep -A 30 "server_name api.example.ru"
```

Также проверь, слушает ли Nginx порт `80`:

```bash
ss -tulpn | grep ':80'
```

Если используешь `ufw`, открой HTTP/HTTPS:

```bash
ufw allow 80/tcp
ufw allow 443/tcp
ufw status
```

На TimeWeb также проверь, что порты `80` и `443` не закрыты в панели firewall/security groups.

## HTTPS через Certbot

VK Mini Apps лучше подключать сразу к HTTPS API. После того как `http://api.example.ru/api/health` начал отвечать, ставь сертификат.

Установи certbot:

```bash
apt install -y certbot python3-certbot-nginx
```

Выпусти сертификат. Замени домен на свой:

```bash
certbot --nginx -d api.example.ru
```

Certbot спросит email и согласие с условиями. Если предложит включить redirect с HTTP на HTTPS, выбирай redirect. После успешного выпуска он сам допишет SSL-настройки в Nginx.

Проверь:

```bash
nginx -t
systemctl reload nginx
curl https://api.example.ru/api/health
```

Проверить автообновление сертификата:

```bash
certbot renew --dry-run
```

После этого в `mini-app/.env.production` указывай именно HTTPS-адрес:

```env
VITE_API_BASE_URL=https://api.example.ru
```

Затем пересобери и задеплой frontend:

```bash
cd /opt/gostchecker/mini-app
npm ci
npm run build
npm run deploy
```

В кабинете VK Mini Apps добавь домен `https://api.example.ru` в разрешенные домены, иначе запросы из приложения могут блокироваться.

## Быстрый чек-лист после настройки сервера

```bash
systemctl status gost-api
systemctl status nginx
curl http://127.0.0.1:8000/api/health
curl https://api.example.ru/api/health
```

Если все четыре пункта в порядке, backend опубликован корректно.

## Обновление backend без потери конфигов

```bash
cd /opt/gostchecker
git pull
. .venv/bin/activate
pip install -r requirements.txt
systemctl restart gost-api
journalctl -u gost-api -n 100 --no-pager
```

Env-файл лежит в `/etc/gostchecker/backend.env`, поэтому обновление репозитория его не трогает.

## Деплой VK Mini App

В `mini-app/.env.production` укажи публичный backend:

```env
VITE_API_BASE_URL=https://api.example.ru
```

Сборка и публикация:

```bash
cd mini-app
npm ci
npm run build
npm run deploy
```

В кабинете VK Mini Apps проверь:

- `app_id` в `vk-hosting-config.json` соответствует приложению.
- Домен backend добавлен в разрешенные домены приложения.
- Frontend опубликован в VK Hosting или на выбранном статическом хостинге.

## Будущая история проверок

Историю лучше добавить отдельным слоем, не ломая текущий API:

- таблица `checks`: `id`, `vk_user_id`, `filename`, `profile`, `score_before`, `score_after`, `created_at`;
- таблица `files`: путь к original/fixed DOCX и TTL для очистки;
- эндпоинты `GET /api/history` и `GET /api/history/{id}`.

Пока это только архитектурная заглушка: текущая версия не пишет историю в БД и не хранит пользовательские файлы после ответа.
