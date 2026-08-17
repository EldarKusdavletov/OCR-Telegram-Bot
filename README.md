![aiogram](https://img.shields.io/badge/aiogram-3-blue.svg?logo=telegram)
![Upstage](https://img.shields.io/badge/Upstage-AI-purple.svg)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.x-gray.svg?logo=sqlalchemy)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-supported-gray.svg?logo=postgresql)
![SQLite](https://img.shields.io/badge/SQLite-supported-gray.svg?logo=sqlite)

# OCR Telegram Bot

Telegram bot that extracts text from any photo you send.

This project receives photos in Telegram, runs OCR via Upstage Document Digitization API, returns extracted text to the user, and stores usage statistics in a relational database.

## What this project does

- Accepts images from Telegram chats
- Sends image bytes to Upstage OCR API
- Returns recognized text, confidence score, billed pages, and processing time
- Logs command usage and OCR outcomes to a database
- Provides user-specific usage stats through `/stats`

## Tech stack

- **Python 3 + aiogram 3** for async Telegram bot handling
- **Upstage OCR API** for text extraction from images
- **SQLAlchemy (async)** for persistence
- **SQLite** for local development (via async SQLite drivers)
- **PostgreSQL + asyncpg** for production deployment

Built with:
- `aiogram` — Async Telegram bot framework
- `Upstage AI` — Optical Character Recognition (OCR)
- `SQLite` — Local development database
- `PostgreSQL` — Production database
- `SQLAlchemy` — Object–Relational Mapping (ORM)

## Repository structure

```text
.
├── main.py                 # Bot bootstrap, router registration, polling startup
├── config.py               # Environment loading and required settings validation
├── requirements.txt        # Python dependencies
├── Procfile                # Process command for Procfile-based platforms
└── bot/
    ├── handlers/
    │   ├── common.py       # /start, /help, /info
    │   ├── stats.py        # /stats from DB logs
    │   ├── ocr.py          # Photo handling and OCR response logic
    │   └── echo.py         # Fallback text/sticker handlers
    ├── services/
    │   └── ocr_client.py   # Upstage OCR API client
    └── db/
        ├── models.py       # User, CommandLog, OCRLog schemas
        └── session.py      # Async engine/session and logging helpers
```

## Runtime flow

1. `main.py` loads configuration and initializes DB schema (`create_all`).
2. Routers are registered in order: common → stats → OCR → echo fallback.
3. Bot runs in long polling mode (`start_polling`) and drops pending updates on startup.
4. On photo messages:
   - bot downloads the highest-resolution Telegram photo
   - photo bytes are sent to Upstage OCR
   - OCR result is returned to user and logged in `ocr_logs`
5. Command usage and user activity are logged continuously.

## Database model summary

- **users**
  - identity and profile snapshot (`user_id`, username, first/last name)
  - activity timestamps (`first_seen`, `last_seen`)
- **command_logs**
  - one row per command execution (`/start`, `/help`, `/stats`, etc.)
- **ocr_logs**
  - OCR request metadata and result diagnostics
  - includes success flag, confidence, processing time, error text

## Configuration

Create `.env` in project root:

```env
BOT_TOKEN=your_telegram_bot_token
UPSTAGE_API_KEY=your_upstage_api_key
DATABASE_URL=your_async_database_url
```

Required environment variables are validated at startup in `config.py`; app exits early if any value is missing.

### Database URL examples

- SQLite (local):
  - `DATABASE_URL=sqlite+aiosqlite:///./bot.db`
- PostgreSQL (production):
  - `DATABASE_URL=postgresql+asyncpg://localhost:5432/dbname`

## Local development

1. Create and activate virtual environment
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure `.env`
4. Start bot:
   ```bash
   python main.py
   ```

## Available commands

- `/start` — greeting and command overview
- `/help` — usage instructions
- `/info` — user Telegram profile details
- `/stats` — per-user command/OCR statistics
- Send a **photo** — OCR processing entry point

## Deployment status and available deployment options

Current status:

- ✅ Bot is deployed and running on **Railway service**
- ✅ Database is deployed on **Railway PostgreSQL**
- ✅ Application process is defined via `Procfile`

Deployment-related assets and setup available in this repository:

1. **Procfile-based worker deployment**
   - `Procfile` contains: `worker: python main.py`
   - Suitable for platforms that support Procfile workers (for example Railway/Heroku-style process runtimes).

2. **Railway PostgreSQL integration guidance**
   - Existing project convention supports Railway-managed PostgreSQL.
   - Use `postgresql+asyncpg://` driver format in `DATABASE_URL`.
   - If Railway provides `DATABASE_PUBLIC_URL` in `postgresql://...` format, convert it to `postgresql+asyncpg://...` for SQLAlchemy async engine compatibility.

### Important operational note

This bot currently runs with **long polling**, not webhook serving. No web server entrypoint, Dockerfile, or Kubernetes manifests are present in the repository, so those deployment targets are not preconfigured yet.

## Reliability and observability notes

- OCR API errors are caught and logged; failure details are saved in `ocr_logs.error`.
- Startup logs include bot launch and DB initialization events.
- `/stats` is useful for basic product telemetry per user.

## Known limitations

- OCR API request is synchronous (`requests`), which can block handler execution under high load.
- `/stats` currently computes counts in Python after selecting all matching rows; this is less efficient on large datasets.
- No built-in admin dashboard, quotas, or rate limiting.

## License

No license file is currently present in this repository.