# 📚 Fikrxona Bot — Ishga Tushirish

## 1. O'rnatish

```bash
pip install -r requirements.txt
```

## 2. Token sozlash

`config.py` faylini oching va quyidagilarni to'ldiring:

```python
BOT_TOKEN = "sizning_tokeningiz"   # @BotFather dan oling
ADMIN_IDS = [sizning_telegram_id]  # @userinfobot orqali ID ni biling
```

## 3. Botni ishga tushirish

```bash
python bot.py
```

---

## Foydalanuvchi imkoniyatlari

| Tugma | Funksiya |
|-------|----------|
| 🔍 Kitob qidirish | Nom yoki muallif bo'yicha qidirish |
| 📚 Kategoriyalar | Janr bo'yicha ko'rish |
| ⭐ Top kitoblar | Eng mashhur kitoblar |
| 🎯 Tavsiya | Tasodifiy tavsiya |
| 📥 Yuklab olganlarim | Tarix |

## Admin imkoniyatlari

| Tugma | Funksiya |
|-------|----------|
| ➕ Kitob qo'shish | PDF + muqova + tavsif qo'shish |
| 🗂 Kategoriya qo'shish | Yangi janr yaratish |
| 🗑 Kitob o'chirish | Kitobni o'chirish |
| 📊 Statistika | Foydalanuvchi va yuklab olish soni |

## Fayl tuzilmasi

```
fikrxona_bot/
├── bot.py           # Asosiy fayl
├── config.py        # Token va sozlamalar
├── database.py      # SQLite
├── keyboards.py     # Tugmalar
├── requirements.txt
└── handlers/
    ├── start.py
    ├── search.py
    ├── categories.py
    ├── recommend.py
    └── admin.py
```
