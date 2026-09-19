# Skuter Arenda Bot

Telegram bot va Web App bilan skuter arenda boshqaruv tizimi.

## Deploy qilish

### 1. GitHub'ga yuklash

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/repo.git
git branch -M main
git push -u origin main
```

### 2. Render.com'da Web App

- Environment: Docker
- Dockerfile Path: Dockerfile
- Environment Variables:
  - PORT=5000
  - ADMIN_PASSWORD=admin123
  - SECRET_KEY=secret

### 3. Render.com'da Bot Worker

- Environment: Docker
- Dockerfile Path: Dockerfile.bot
- Environment Variables:
  - BOT_TOKEN=your_token
  - ADMIN_IDS=123456789
  - WEB_APP_URL=https://your-app.onrender.com

Tayyor!
