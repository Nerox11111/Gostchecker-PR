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

Запуск:

```bash
systemctl daemon-reload
systemctl enable --now gost-api
systemctl status gost-api
```

Nginx reverse proxy. Подставь свой домен вместо `api.example.ru`:

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

Проверка:

```bash
nginx -t
systemctl reload nginx
curl http://127.0.0.1:8000/api/health
curl http://api.example.ru/api/health
```

Для HTTPS поставь `certbot` и выпусти сертификат на домен. VK Mini Apps лучше сразу подключать к HTTPS API.

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
