# UX Copy — Telegram Bot (Minimal/Profesyonel · Siz · Orta Emoji)

Bu doküman bot içi metinler için **başlangıç kopyasıdır**. İstersen dil tonu ve terimleri birlikte ince ayarlarız.

## /start — Rol Seçimi
**Mesaj**
```
Hoş geldiniz. 👋
Land of Airdrop deneyimine başlamak için rolünüzü seçin:
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
Bu pasaport yalnızca oyun içi ilerleme ve güvenlik takibi için kullanılır.
Kişisel bilgi istemiyoruz.
```
**Buton**
- `✅ Pasaport Oluştur`

**Başarılı**
```
Pasaportunuz hazır ✅
Şimdi günlük görev menüsüne geçebilirsiniz.
```

---

## Ebeveyn Akışı — Çocuk Bağlama
**/link komutu**
```
Çocuğunuz için tek kullanımlık bir bağlama kodu oluşturalım.
Bu kod 10 dakika geçerli olacak.
```
**Buton**
- `🔗 Kod Oluştur`

**Kod üretildi**
```
Kodunuz hazır: {CODE}
Bu kodu çocuğunuzla paylaşın.
```

**Çocuk tarafı**
```
Ebeveyn kodunu girin:
```

**Başarılı**
```
Bağlantı tamamlandı ✅
Ebeveyniniz artık ilerlemenizi takip edebilir.
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
Bugünün niyetini sesli mesaj olarak gönderin.
Kısa ve net olması yeterlidir.
```

**Başarılı**
```
Sesiniz alındı ✅
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
Durumunuz:
• Streak: {STREAK}
• Mühür Seviyesi: {SEAL_LEVEL}
• Bugünün Çarpanı: x{MULTIPLIER}
```

---

## /help — Güvenlik
**Mesaj**
```
Bu bot asla sizden seed phrase / private key / şifre istemez.
Resmi duyurular yalnızca burada paylaşılır.
```

---

## Sistem Mesajları
**Rate limit**
```
Biraz hızlısınız. Lütfen {SECONDS} saniye bekleyin.
```

**Bakım modu**
```
Şu an kısa bir bakım var. Lütfen biraz sonra tekrar deneyin.
```
