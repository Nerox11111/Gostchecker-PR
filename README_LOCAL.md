# Локальное тестирование backend + временный frontend

## 1) Установка
```powershell
python -m pip install -r requirements.txt
```

## 2) Запуск сервера
```powershell
python -m uvicorn server:app --reload --port 8000
```

## 3) Запуск фронтенда (отдельно)
Фронтенд сейчас — статический (раздаётся простым сервером).

Запусти:
```powershell
python -m http.server 3000 --directory frontend\static
```

Откройте:
- `http://127.0.0.1:3000/`

Примечание: если бэкенд на другом порту/хосте, укажи его в поле `API URL backend` (на странице).
Если удобнее — можно также передать параметр `?api=`:
- `http://127.0.0.1:3000/?api=http://127.0.0.1:8000`

## 4) API (для отладки)
- `GET /api/modules` — список доступных scopes и ключевых слов титульного листа
- `POST /api/run` — прогон документа:
  - параметры: `mode` (`validate|correct|analyze`), `scope_id`
  - multipart/form-data: `file` (.docx)

