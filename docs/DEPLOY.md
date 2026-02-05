# Deploy Rehberi — Docker Compose

Bu doküman, Land of Airdrop botunu Docker Compose ile prod’a almak için **net ve uygulanabilir** bir yol sunar.

## 1) Klasör Yapısı (Önerilen)
```
/opt/landofairdrop-bot
  ├─ .env
  ├─ docker-compose.prod.yml
  ├─ landofairdrop-bot/   (repo)
```

## 2) .env (Sunucuda)
Örnek:
```
BOT_TOKEN=xxxx
DATABASE_URL=postgresql+asyncpg://land:land@postgres:5432/landofairdrop
REDIS_URL=redis://redis:6379/0
ADMIN_USER_IDS=12345,67890
ENV=prod

TG_JOIN_CHANNEL=@YourChannel
TG_JOIN_CHANNEL_ID=-1001234567890

REFERRAL_BONUS_POINTS=10
BROADCAST_PER_SECOND=10

BOT_NAME=Land of Airdrop
BOT_USERNAME=@Landofairdropbot
```

## 3) docker-compose.prod.yml
```
version: "3.9"
services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_USER: land
      POSTGRES_PASSWORD: land
      POSTGRES_DB: landofairdrop
    volumes:
      - pg_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7
    restart: unless-stopped

  bot:
    image: python:3.12-slim
    working_dir: /app
    volumes:
      - ./landofairdrop-bot:/app
    env_file:
      - .env
    command: >
      sh -c "pip install -r requirements.txt &&
             alembic upgrade head &&
             python apps/bot/main.py"
    depends_on:
      - postgres
      - redis
    restart: unless-stopped

  worker:
    image: python:3.12-slim
    working_dir: /app
    volumes:
      - ./landofairdrop-bot:/app
    env_file:
      - .env
    command: >
      sh -c "pip install -r requirements.txt &&
             python worker/main.py"
    depends_on:
      - redis
    restart: unless-stopped

volumes:
  pg_data:
```

## 4) Deploy Komutları
```
# ilk kurulum
docker compose -f docker-compose.prod.yml up -d

# loglar
docker compose -f docker-compose.prod.yml logs -f bot
docker compose -f docker-compose.prod.yml logs -f worker

# güncelleme
cd /opt/landofairdrop-bot/landofairdrop-bot
git pull
docker compose -f ../docker-compose.prod.yml up -d --build
```

## 5) Prod Kontrol Listesi (Kısa)
- `.env` sadece sunucuda ve erişim limitli
- `BOT_TOKEN` repoya girmedi
- `TG_JOIN_CHANNEL` / `TG_JOIN_CHANNEL_ID` doğru
- `ADMIN_USER_IDS` minimum kişi
- `alembic upgrade head` sorunsuz
- `bot` + `worker` aynı anda çalışıyor

## 6) Sorun Giderme (Hızlı)
- Bot sessiz → `docker logs bot`
- Broadcast gitmiyor → `docker logs worker`
- DB hatası → `docker logs postgres`
- Redis → `docker logs redis`

## 7) Notlar
- Prod’da `debug` kapalı (`ENV=prod`)
- Compose ile bot/worker aynı image üzerinden koşar
- Gerektiğinde tek servis restart edebilirsin:
  ```
  docker compose -f docker-compose.prod.yml restart bot
  docker compose -f docker-compose.prod.yml restart worker
  ```
