# Incident Rehberi — Land of Airdrop Bot

Bu doküman, prod ortamında sorun yaşandığında hızlı teşhis ve kontrollü müdahale için kısa reçeteler içerir.

## 0) Altın Kural
Önce etkiyi durdur, sonra kök nedeni çöz.  
“Fix + deploy” refleksi yerine: hız düşür / özelliği kapat / kuyruğu durdur.

## 1) Spam / Abuse Dalgası
**Belirtiler**
- CPU/RAM artışı, loglarda handler spam’i
- DB’de submission sayısı patlıyor
- Telegram’da “bot cevap vermiyor” şikayetleri

**İlk 5 dakika**
- Rate-limit’i sıkılaştır
- `BROADCAST_PER_SECOND` düşür (örn. 10 → 3)
- En çok abuse edilen komutu geçici kapat (`/verify` gibi)
- Admin allowlist’i doğrula

**Kalıcı çözüm**
- `/verify` için kullanıcı başına cooldown (örn. 30s)
- Aynı task için kısa sürede tekrar proof engeli
- Çok fail üreten user_id’leri audit log’dan tespit et ve banla

## 2) Telegram Flood / Ban
**Belirtiler**
- Worker loglarında `send_message` hataları artar
- Broadcast yarıda kalır

**İlk 5 dakika**
- Broadcast hızını düşür (`BROADCAST_PER_SECOND=3`)
- Worker’ı geçici durdur (queue büyür ama flood kesilir)

**Kalıcı çözüm**
- Broadcast segmentasyonu kullan (all yerine wallet/pending)
- Büyük broadcast’ı batch’lere böl
- Flood hataları için exponential backoff ekle

## 3) DB / Disk Dolması
**Belirtiler**
- Postgres write işlemleri fail
- Disk kullanımında ani artış

**İlk 5 dakika**
- Disk kullanımını kontrol et (`df -h`)
- Eski logları temizle/rotate
- Gereksiz dump/backup dosyalarını arşivle

**Kalıcı çözüm**
- Günlük backup + 7/14 günlük retention
- Logrotate
- `audit_logs` için retention politikası (örn. 30 gün)

## 4) Webhook Kırıldı / Bot Güncelleme Almıyor
**Belirtiler**
- Bot “sessiz”
- Health endpoint çalışıyor ama Telegram update gelmiyor

**İlk 5 dakika**
- Health endpoint’i kontrol et
- SSL geçerli mi kontrol et
- `getWebhookInfo` ile webhook durumunu doğrula

**Geçici çözüm**
- Acil durumda kısa süreli long polling

**Kalıcı çözüm**
- Webhook URL secret path kullan
- Reverse proxy loglarını kaydet
- SSL otomatik yenileme (Caddy genelde otomatik)

## 5) Redis / Queue Tıkandı
**Belirtiler**
- Broadcast “queued” kalıyor
- Worker çalışıyor ama mesaj gitmiyor

**İlk 5 dakika**
- Worker çalışıyor mu kontrol et
- Redis ping (`redis-cli ping`)
- Queue uzunluğunu kontrol et

**Kalıcı çözüm**
- Worker exception loglarını görünür yap
- Poison message yakala: hatalı payload’ı drop et
- Dead-letter queue (MVP+)

## 6) Migration Hatası
**Belirtiler**
- “column not found” gibi DB hataları
- Bot açılıyor ama query’ler fail

**İlk 5 dakika**
- `alembic current` / `alembic heads` kontrol
- Eksik migration varsa `alembic upgrade head`
- Migration bozuksa rollback deploy (önceki commit/image)

**Kalıcı çözüm**
- CI’da migration + test zaten var: prod öncesi aynı adımlar
- Kritik migration’larda downgrade yaz

## 7) Phishing / “Seed istiyor musunuz?” Panikleri
**Aksiyon**
- Duyuru kanalı/pinned: “Bot asla seed/private key istemez”
- `/help` ve `/start` metnini doğrula
- Phishing link paylaşanları banla/ignore list

## 8) Hazır “Panik Switch” Önerileri
**ENV ile hızlı kapatma (isteğe bağlı)**
- `MAINTENANCE_MODE=1` → `/verify` kapalı
- `DISABLE_BROADCAST=1` → enqueue reddet
- `MAX_PROOF_PER_HOUR=...` → abuse kıs

## 9) Incident Sonrası Log Toplama
**Sorular**
- Hangi endpoint/handler patladı?
- Hangi user_id’ler spam yaptı?
- En sık görülen exception?

**Mini rapor şablonu**
- Tarih/Saat
- Etki
- Kök neden
- Alınan aksiyon
- Kalıcı önlem
