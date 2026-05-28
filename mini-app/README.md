# VK Mini App Frontend

React + VKUI frontend для GOST-Checker. Текущая настройка рассчитана на production-размещение в VK Hosting.

```bash
copy .env.production.example .env.production
```

Укажите API backend:

```env
VITE_API_BASE_URL=https://gostchecker.ru/
```

Проверьте `vk-hosting-config.json`, особенно `app_id`. Без `VITE_API_BASE_URL` приложение не сможет обращаться к backend.

Сборка и загрузка:

```bash
npm run build
npm run deploy
```

Полная инструкция по TimeWeb и VK Mini Apps находится в корневом `README.md`.
