# UX Copy — Telegram Bot (Draft)

Bu doküman bot içi metinler için **başlangıç kopyasıdır**. İstersen dil tonu ve terimleri birlikte ince ayarlarız.

## /start — Rol Seçimi
**Mesaj**
```
Hoş geldin! 👋
Land of Airdrop deneyimine başlamak için rolünü seç:
```

**Butonlar**
- `🧒 Çocuk (Maceracı)`
- `👪 Ebeveyn (Gözlemci)`
- `ℹ️ Yardım`

---

## Çocuk Akışı — Pasaport
**Mesaj**
```
Ada Pasaportu oluşturuyoruz.
Bu pasaport sadece oyun içi ilerlemeni ve güvenliği takip etmek için kullanılır.
Kişisel bilgi istemiyoruz.
```
**Buton**
- `✅ Pasaport Oluştur`

**Başarılı**
```
Pasaportun hazır ✅
Şimdi günlük görev menüsüne geçebilirsin.
```

---

## Ebeveyn Akışı — Çocuk Bağlama
**/link komutu**
```
Çocuğun için tek kullanımlık bir bağlama kodu oluşturalım.
Bu kod 10 dakika geçerli olacak.
```
**Buton**
- `🔗 Kod Oluştur`

**Kod üretildi**
```
Kodun hazır: {CODE}
Bu kodu çocuğunla paylaş.
```

**Çocuk tarafı**
```
Ebeveyn kodunu gir:
```

**Başarılı**
```
Bağlantı tamamlandı ✅
Ebeveynin artık ilerlemeni takip edebilir.
```

---

## /daily — Günlük Menü
**Mesaj**
```
Bugünün görevleri:
```

**Butonlar**
- `🎙 Günlük Niyet (Ses)`
- `📚 Günlük Eğitim`
- `⭐ Durumum`

---

## /intent — Günlük Niyet
**Mesaj**
```
Bugünün niyetini sesli mesaj olarak gönder.
Kısa ve net olması yeterli.
```

**Başarılı**
```
Sesin alındı ✅
Bugünün söz mührü güçlendi.
```

---

## /learn — Günlük Eğitim
**Mesaj**
```
Bugünün mini içeriği:
{VIDEO_OR_LINK}

Şimdi 3 kısa soruya geçelim.
```

---

## /status — İlerleme ve Çarpan
**Mesaj**
```
Durumun:
• Streak: {STREAK}
• Mühür Seviyesi: {SEAL_LEVEL}
• Bugünün Çarpanı: x{MULTIPLIER}
```

---

## /help — Güvenlik
**Mesaj**
```
Bu bot asla senden seed phrase / private key / şifre istemez.
Resmi duyurular yalnızca burada paylaşılır.
```

---

## Sistem Mesajları
**Rate limit**
```
Biraz hızlısın. Lütfen {SECONDS} saniye bekle.
```

**Bakım modu**
```
Şu an kısa bir bakım var. Lütfen biraz sonra tekrar dene.
```
