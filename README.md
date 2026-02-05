# Land of Airdrop Bot
Status: Production-ready · Docker Compose deploy · CI + tests + lint aktif

Placeholder-based MVP skeleton for a Telegram airdrop bot.

## Quick Start

1. Copy `.env.example` to `.env` and fill in real values.
2. Start services with Docker Compose.
3. Run migrations.
4. Seed tasks.
5. Run bot in polling mode locally.

### Commands

```bash
# 1) Services
docker compose up -d

# 2) Migration
alembic upgrade head

# 3) Seed
python scripts/seed_tasks.py
```

## Production & Operations Docs

This bot is designed to run in production. The documents below cover deploy,
operations, and incident handling:

- Deployment Guide (Docker Compose): `docs/DEPLOY.md`
- Production Checklist: `docs/PROD_CHECKLIST.md`
- Incident Response Playbook: `docs/INCIDENTS.md`
