# Skuter Arenda Bot - To'liq Python

Telegram bot va Web App - ikkisi ham Python'da yozilgan.

## 📦 Tuzilma

```
├── bot.py                    # Telegram bot (Python)
├── webapp/app.py             # Flask web app
├── requirements.txt          # Bot dependencies
├── webapp/requirements.txt   # Web app dependencies
├── Dockerfile                # Web app uchun
└── Dockerfile.bot            # Bot uchun
```

## 🚀 Deploy - Render.com

### 1. GitHub'ga yuklash

```bash
git add -A
git commit -m "Toliq Python bot va webapp"
git push origin main
```

### 2. Web App (Flask)

- **Environment:** Docker
- **Dockerfile Path:** `Dockerfile`
- **Environment Variables:**
  - `PORT=5000`
  - `ADMIN_PASSWORD=admin123`
  - `SECRET_KEY=secret`

### 3. Bot Worker (Python)

- **Environment:** Docker
- **Dockerfile Path:** `Dockerfile.bot`
- **Environment Variables:**
  - `BOT_TOKEN=<token>`
  - `ADMIN_IDS=<id>`
  - `WEB_APP_URL=<url>`

## ✅ Test

1. Web App: `https://your-app.onrender.com`
2. Telegram bot: `/start`

Tayyor!
