# Instagram bot for comments "1864"

Готовый минимальный проект на Python для Instagram-бота под сценарий:

- человек пишет `1864` в комментариях
- бот получает webhook от Meta
- бот отправляет первое сообщение в Direct
- дальше при каждом ответе пользователя отправляет следующий блок сценария

## Что внутри

- `app/main.py` — FastAPI webhook
- `app/instagram.py` — отправка сообщений через Meta Graph API
- `app/scenario.py` — весь сценарий сообщений
- `app/state.py` — хранение шага диалога и дедупликация событий
- `.env.example` — переменные окружения
- `render.yaml` — деплой на Render

## Важно перед запуском

Чтобы это работало через **официальный Meta API**, обычно нужны:

1. **Instagram Professional account** (Business или Creator)
2. Аккаунт должен быть **подключён к Facebook Page**
3. Приложение в **Meta for Developers**
4. Настроенный **Webhook**
5. Разрешения/доступы для Instagram Messaging API и подписка на нужные webhook fields

Meta Business / professional accounts and connections are part of the official setup flow. Meta says professional Instagram accounts unlock business features, and Facebook/Instagram connections are managed through Meta Business tooling. citeturn679186search11turn710495search2

## Быстрый локальный запуск

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Проверка:

- health: `http://localhost:8000/health`
- webhook verify endpoint: `GET /webhook`

## Как работает сценарий

### 1. Комментарий
Если пользователь оставил комментарий `1864`, бот отправит:

> Привет 👀  
> Ты написал “1864” — значит тебе зашёл этот проект  
>  
> Это на самом деле одно из самых странных и недооценённых мест у Кремля

### 2. Дальше бот идёт по шагам
Каждый следующий ответ пользователя двигает сценарий на следующий блок.

Если человек пишет:

- `стоп`
- `stop`
- `/start`
- `сначала`
- `заново`
- `1864`

сценарий сбрасывается и начинается заново.

## Настройка Meta webhook

Тебе нужно будет в Meta App указать:

- Callback URL: `https://твой-домен.onrender.com/webhook`
- Verify token: значение `VERIFY_TOKEN` из `.env`

Webhook verification — стандартный flow у Meta: платформа присылает `hub.challenge`, а сервер должен вернуть его обратно при совпадении verify token.

## Что может прийти в webhook

У Meta структура событий зависит от подписанных полей и конкретной конфигурации приложения. В этом шаблоне уже заложена обработка:

- comment-like events (`changes` → `comments` / `feed`)
- direct messages (`messaging`)

При интеграции может понадобиться слегка подправить `handle_change()` под фактический payload твоего приложения.

## Деплой на Render

Render по состоянию на сейчас даёт бесплатные web services. Free web services засыпают после 15 минут без трафика, а при следующем запросе могут просыпаться до минуты. citeturn406698search2turn406698search12turn406698search18

### Шаги

1. Залей проект в GitHub
2. Зайди в Render
3. `New +` → `Web Service`
4. Подключи GitHub-репозиторий
5. Render сам подхватит `render.yaml`
6. В environment variables укажи:
   - `VERIFY_TOKEN`
   - `META_ACCESS_TOKEN`
   - `INSTAGRAM_BUSINESS_ACCOUNT_ID`

### Что важно знать про бесплатный хостинг

- **Render free** подходит для теста и MVP. citeturn406698search6turn406698search18
- **Railway** сейчас не даёт постоянный бесплатный тариф как раньше: у новых пользователей есть trial credits, а дальше обычно нужен платный план/usage. citeturn406698search7turn406698search13turn406698search16
- Поэтому для полностью бесплатного старта **Render сейчас удобнее Railway**. citeturn406698search2turn406698search6turn406698search7

## Ограничения этого стартера

1. Здесь нет панели админа
2. Нет очередей и retry-логики
3. Нет Postgres/Redis
4. SQLite на бесплатном инстансе годится для MVP, но не для серьёзной нагрузки
5. Для production лучше вынести состояние в Postgres

## Что я бы сделал следующим шагом

1. Добавил бы несколько сценариев под разные Reels
2. Сделал бы keyword routing (`1864`, `остров`, `кремль`, и т.д.)
3. Добавил бы логирование входящих диалогов
4. Подключил бы PostgreSQL
5. Сделал бы mini-admin через Telegram или вебку

## Отправка сообщений через Meta Graph API

В файле `app/instagram.py` уже есть метод `send_text_message()`. Если у тебя будет другой формат запроса под текущую конфигурацию Meta, ты просто поправишь один файл, а сценарий и webhook останутся теми же.

## Пример структуры проекта

```text
insta_1864_bot/
├── app/
│   ├── config.py
│   ├── instagram.py
│   ├── main.py
│   ├── scenario.py
│   └── state.py
├── .env.example
├── README.md
├── render.yaml
└── requirements.txt
```
