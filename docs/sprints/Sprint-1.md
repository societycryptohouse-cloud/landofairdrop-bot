# Sprint 1 — Abuse Kalkanı + Staging

## Sprint Hedefi
Bu sprint, botu **güvenli ve kontrollü** şekilde dışarı açmak için gerekli
koruma katmanlarını ve staging ayrımını kurar. Amaç: spam/abuse riskini azaltmak,
staging/prod karışmasını engellemek ve minimum operasyonel görünürlük sağlamak.

---

## Issue Listesi

- [ ] **feat: rate limiting for commands and messages**  
  **Goal:** Spam / brute-force / flood’ı kesmek  
  **Acceptance Criteria:**  
  - Kullanıcı başına örn. `10 komut / 60 sn` (konfig ile)  
  - `/link` ve doğrulama akışlarında daha sıkı limit (örn. `3 deneme / 10 dk`)  
  - Limit aşımında kullanıcıya sakin mesaj + cooldown süresi  
  - `rate_limited_count` log/metric  
  **Notes:** Redis varsa sliding window / token bucket önerilir.

- [ ] **feat: basic abuse analytics counters**  
  **Goal:** Ne oluyor, kim zorluyor, neresi kırılıyor?  
  **Acceptance Criteria:**  
  - Şu metrikler toplanır (DB veya Redis + günlük flush):  
    `start_count`, `daily_open_count`, `link_attempt_count`,  
    `link_fail_count`, `rate_limited_count`  
  - Admin komutuyla özet alınır (örn. `/admin_stats`)  
  - Günlük rapor formatı hazır

- [ ] **chore: enforce staging/prod bot token separation**  
  **Goal:** Prod token’ı staging’de yanlışlıkla çalıştırmayı engellemek  
  **Acceptance Criteria:**  
  - `APP_ENV=staging` iken prod token’a eşitse bot çalışmayı reddeder  
  - Basit çözüm: token fingerprint allowlist veya `BOT_MODE=staging|prod`  
  - Startup log’da ortam net yazar: `ENV=staging` / `ENV=prod`

- [ ] **chore: support BOT_MODE=webhook|polling**  
  **Goal:** Local dev kolay, staging/prod stabil  
  **Acceptance Criteria:**  
  - `BOT_MODE=polling` localde çalışır  
  - `BOT_MODE=webhook` prod’da çalışır  
  - `WEBHOOK_URL=...` env ile gelir  
  - Başlangıçta mod loglanır

- [ ] **feat: parent-child linking with one-time code + TTL**  
  **Goal:** Eşleştirmede güvenlik ve UX  
  **Acceptance Criteria:**  
  - Ebeveyn `/link` → 6 haneli kod üret  
  - Kod 10 dakika geçerli (TTL)  
  - Kod tek kullanımlık  
  - Çocuk “Kodu gir” akışıyla bağlanır  
  - Başarılı eşleşmede ebeveyne ve çocuğa onay mesajı

- [ ] **feat: admin allowlist and basic admin commands**  
  **Goal:** Telegram içinden kontrol paneli hissi  
  **Acceptance Criteria:**  
  - `ADMIN_USER_IDS` env’den çekilir  
  - Admin olmayan /admin_* denemeleri reddedilir  
  - Minimum komutlar: `/admin_stats`, `/admin_broadcast`

- [ ] **chore: structured logs without PII**  
  **Goal:** Çocuk güvenliği + uyumluluk  
  **Acceptance Criteria:**  
  - Loglarda isim/telefon/mesaj içeriği yok  
  - Sadece `user_id`, `event type`, `timestamp`  
  - Rate limit ve link fail sebepleri kodlu (enum gibi)

- [ ] **docs: add Sprint 1 runbook (staging ops)**  
  **Goal:** Operasyon tek kişinin kafasında kalmasın  
  **Acceptance Criteria:**  
  - `DEPLOY.md` ekleri: staging token, log bakma, restart  
  - Staging DB reset adımları  
  - Acil durumda bot disable prosedürü

- [ ] **ops: add /health endpoint for bot service**  
  **Goal:** Basit healthcheck ile gözlenebilirlik  
  **Acceptance Criteria:**  
  - `200 OK` döner  
  - DB/Redis kontrolü opsiyonel flag ile

---

## Done Definition
- Tüm issue’lar “Done”  
- Staging token/prod token karışması engellenmiş  
- Rate-limit + analytics minimum seviye hazır  
- `/health` ve admin özet komutu çalışır  
