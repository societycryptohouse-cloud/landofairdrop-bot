# Prod Checklist — Land of Airdrop Bot

## 1) Secrets ve Yapılandırma
- `BOT_TOKEN` sadece sunucuda `.env` içinde
- `.env` dosya izinleri sadece deploy user okuyabilir
- `ADMIN_USER_IDS` doğru ve minimum kişi
- `ENV=prod`
- `REFERRAL_BONUS_POINTS`, `BROADCAST_PER_SECOND` prod değerleri net
- `TG_JOIN_CHANNEL` / `TG_JOIN_CHANNEL_ID` doğru (private ise ID şart)

## 2) Domain, SSL ve Webhook
- Sunucuda domain hazır (örn. `bot.domain.com`)
- SSL aktif (Caddy/Nginx + Let’s Encrypt)
- Webhook URL ve route net (örn. `/telegram/webhook/<secret>`)
- Webhook secret path kullan (tahmin edilmesin)
- Telegram webhook set edildi (token ile)
- Webhook endpoint `200` dönüyor (health check)

## 3) Runtime (Bot + Worker)
- Bot process yönetimi: systemd veya docker compose restart policy
- Worker process ayrı çalışıyor (queue tüketiyor)
- Loglar yazıyor ve dönüyor (logrotate veya container logging)
- Broadcast worker rate-limit prod’da mantıklı (10/s genelde güvenli)

## 4) Database ve Migrations
- Postgres prod’da kalıcı disk (volume)
- `alembic upgrade head` prod’da koştu
- DB bağlantı limiti/timeout ayarlı
- Günlük otomatik backup planı var (en az 7 gün sakla)

## 5) Redis / Queue
- Redis dış dünyaya açık değil (sadece localhost/internal network)
- Queue key çakışmıyor (tek environment)
- Worker “poison message” durumunda kilitlenmiyor (exception yakalanıyor)

## 6) Güvenlik / Abuse Kontrolü
- Admin komutları allowlist’te ve komut listesinde gereksiz görünmüyor
- Rate-limit middleware aktif (özellikle `/verify`, `/broadcast`)
- Input validation: wallet format / link format
- “Seed/private key istemeyiz” mesajı `/help` ve `/start`’ta net
- Kanal üyelik kontrolü için bot kanalda admin

## 7) Monitoring ve Alarmlar
- Health endpoint var (`/health`) ve dışarıdan kontrol ediliyor
- Kritik hatalar için alarm kanalı (Telegram/Discord) veya e-posta
- Disk doluluk ve DB disk alarmı (backup büyür)

## 8) Deploy Akışı (Pratik)
- Deploy tek komut/tek script: pull → install → migrate → restart
- Rollback planı: önceki image/commit’e dön (migrate geri gerekmeyecek şekilde)
- Prod’da `debug` kapalı

## 5 Dakikalık Smoke Test (Çıkmadan Önce)
- `/start` açılıyor, butonlar çalışıyor
- `/wallet` kaydediyor (değişim kilidi çalışıyor)
- `/tasks` listesi dolu, TG check çalışıyor
- `/verify` pending yazıyor, `/admin` onaylıyor
- Referral: ref link → wallet + 1 task → bonus yazıyor + DM gidiyor
- `/broadcast` küçük hedefle test (kendine göndererek)
