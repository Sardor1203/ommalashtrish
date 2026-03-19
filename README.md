# Telegram murojaat-bot

Ushbu bot quyidagicha ishlaydi:

1. Foydalanuvchi botga **private** chatda murojaat yuboradi.
2. Bot murojaatni belgilangan **Telegram guruhiga** yuboradi.
3. Guruh a'zolaridan istalgani shu xabarga **reply** qiladi.
4. Bot reply qilingan javobni aynan murojaat egasiga qaytarib yuboradi.

## Asosiy imkoniyatlar

- private chatdan kelgan murojaatlarni guruhga uzatadi
- guruh a'zolari reply orqali javob beradi
- javob avtomatik ravishda asl foydalanuvchiga yuboriladi
- matn, rasm, video, audio, voice, sticker, hujjatlarni qo'llab-quvvatlaydi
- SQLite bazada xabar bog'lanishlarini saqlaydi

## Muhim cheklov

Foydalanuvchi **albatta bot bilan private chatni kamida bir marta ochgan bo'lishi kerak**. Telegram botlari foydalanuvchiga o'zlari birinchi bo'lib yozolmaydi; foydalanuvchi avval `/start` bosishi kerak. Bu Telegram Bot API cheklovidir.

## O'rnatish

### 1) Bot yaratish

- Telegram'da **@BotFather** ga kiring
- `/newbot` buyrug'i orqali bot yarating
- sizga berilgan tokenni saqlang

### 2) Guruh tayyorlash

- botni kerakli guruhga qo'shing
- botni **admin** qilish tavsiya etiladi
- **BotFather -> /setprivacy -> Disable** qilib, privacy mode'ni o'chiring

Aks holda bot guruhdagi reply xabarlarini ko'rmasligi mumkin.

### 3) Serverga joylash

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

`.env` ichiga quyidagini yozing:

```env
BOT_TOKEN=BotFather bergan token
TARGET_GROUP_ID=-100xxxxxxxxxx
```

### 4) Ishga tushirish

Linux/macOS:

```bash
export $(grep -v '^#' .env | xargs)
python bot.py
```

Windows PowerShell:

```powershell
Get-Content .env | ForEach-Object {
  if ($_ -match '^(.*?)=(.*)$') {
    [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process')
  }
}
python bot.py
```

## Guruh ID sini olish

Eng oson yo'l:

- botni guruhga qo'shing
- `python bot.py` ni ishga tushiring
- guruhga biror test xabar yozing
- log yoki update ichidan `chat.id` ni ko'ring

Supergroup ID odatda `-100...` ko'rinishida bo'ladi.

## Ishlash mantig'i

- foydalanuvchi yuborgan har bir murojaat uchun bot guruhga ikki xabar yuboradi:
  - kim yuborganini ko'rsatadigan servis xabari
  - asl murojaatning nusxasi
- ikkala group message ID ham foydalanuvchi chat ID si bilan SQLite bazaga yoziladi
- guruh a'zosi shu ikki xabardan biriga reply qilsa, bot reply xabarni foydalanuvchiga `copy_message` orqali yuboradi

## Tavsiya etiladigan deploy

- VPS yoki serverda `systemd` orqali
- yoki Docker konteynerda
- yoki webhook orqali public serverga

Hozirgi loyiha **long polling** bilan ishlaydi, test va kichik/orta loyihalar uchun juda qulay.

## Xavfsizlik bo'yicha tavsiya

- tokenni GitHub'ga yuklamang
- `.env` faylini repo'ga qo'shmang
- guruhga faqat ishonchli operatorlarni qo'shing

## Kelajakda qo'shish mumkin bo'lgan funksiyalar

- operator nomidan foydalanuvchiga javob berilgani haqida log
- murojaat raqami (ticket ID)
- statuslar: ochiq / yopildi
- admin panel
- PostgreSQL
- webhook + Nginx deploy
