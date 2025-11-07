![Technologies](https://img.shields.io/badge/aiogram-3.x-blue.svg?logo=telegram)
![Technologies](https://img.shields.io/badge/Upstage-AI-purple.svg)
![Technologies](https://img.shields.io/badge/SQLAlchemy-2.0-red.svg?logo=sqlalchemy)
![Technologies](https://img.shields.io/badge/SQLite-3-blue.svg?logo=sqlite)

#### Telegram bot that extracts text from any photo you send.

Built with:  
`aiogram` — Async Telegram bot framework  
`Upstage AI` — Optical Character Recognition (OCR)  
`SQLite` — Local development database / `PostgreSQL` — Production database (Railway deployment)  
`SQLAlchemy` — Object–Relational Mapping (ORM)

#### Configuration

Create a `.env` file in the root of the project:

```
BOT_TOKEN=
UPSTAGE_API_KEY=
DATABASE_URL=
```

#### Database deployment on Railway

Create a PostgreSQL instance in Railway and change its value of `DATABASE_PUBLIC_URL` from
`postgresql://` to `postgresql+asyncpg://`. Set the environment variable in your service:
`DATABASE_URL="${{Postgres.DATABASE_PUBLIC_URL}}"`