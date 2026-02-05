# Deployment Guide (Staging & Prod)

This repo supports Docker-based deployment using a base compose file plus
environment-specific overrides.

## Prerequisites
- Docker + Docker Compose v2
- A Telegram Bot Token (staging and prod should use different tokens)
- Recommended: a VPS running Ubuntu 22.04+

---

## Environment Files

We keep `.env.example` in the repo and **do not** commit `.env.staging` or
`.env.prod`.

Create staging env:
```bash
cp .env.example .env.staging
```

Create prod env:
```bash
cp .env.example .env.prod
```

Fill in:
- `APP_ENV` (staging or prod)
- `TELEGRAM_BOT_TOKEN`
- `API_BASE_URL` / `API_KEY`
- `DATABASE_URL` (or `POSTGRES_*` if you compose DSN yourself)
- `REDIS_URL`

---

## Staging

Start:
```bash
docker compose -f docker-compose.yml -f docker-compose.staging.yml up -d --build
```

Logs:
```bash
docker compose -f docker-compose.yml -f docker-compose.staging.yml logs -f bot
```

Stop:
```bash
docker compose -f docker-compose.yml -f docker-compose.staging.yml down
```

---

## Production

Production should use a separate token, separate DB, and ideally a separate
server.

If you use the provided `docker-compose.prod.yml`:
```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

---

## Operational Notes

### Secrets
- Never commit `.env*` (except `.env.example`)
- Never commit Telegram bot tokens
- Use GitHub Actions Secrets for CI

### Backups
- Postgres volume should be backed up daily
- Keep at least 7 days retention

### Security
- Restrict inbound ports (only 80/443 for webhook if used)
- Use a reverse proxy (Caddy/Nginx) for HTTPS webhooks
- Keep branch protection + tag checklist workflow enabled

---

## Release Flow
1. Update `CHANGELOG.md`
2. Create/Push tag: `vX.Y.Z`
3. CI runs `release-checklist`
4. Draft GitHub Release with:
```bash
python scripts/release_notes.py vX.Y.Z
```

---

## Optional: Convenience Commands
Consider a `Makefile` for:
- `make up-staging`
- `make logs-staging`
- `make down-staging`
