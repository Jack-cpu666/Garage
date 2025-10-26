# Quick Deployment Guide for Render.com

## 🚀 5-Minute Deployment

### Step 1: Push to GitHub

```bash
cd render.com
git init
git add .
git commit -m "Initial deployment"

# Create repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/metropolis-gate-control.git
git push -u origin main
```

### Step 2: Deploy on Render

1. Go to https://dashboard.render.com/
2. Click **"New"** → **"Blueprint"**
3. Connect your GitHub account
4. Select the repository you just created
5. Render will detect `render.yaml` automatically
6. Click **"Apply"**

### Step 3: Set Environment Variables

In the Render dashboard:

1. Click on your service name
2. Go to **"Environment"** tab
3. Add these variables:

```
DASHBOARD_PASSWORD = your-secure-password-here
METROPOLIS_EMAIL = security@555capitolmall.com
METROPOLIS_PASSWORD = 555_Security
AUTH_KEY = (leave empty initially)
```

4. Click **"Save Changes"**

### Step 4: Wait for Deployment

- Build takes ~5-10 minutes (installs Chrome for Selenium)
- Watch the logs for progress
- Once you see "Starting gunicorn...", it's ready!

### Step 5: Access Your App

1. Your app will be at: `https://your-app-name.onrender.com`
2. Login with the password you set in `DASHBOARD_PASSWORD`
3. Go to "Token Mgmt" tab and click "Start Auto-Monitor"
4. Done! 🎉

## Important Notes

### ⚠️ Render Free Tier Limitations

- **Spins down after 15 min of inactivity**
- **Slow first load** (30-60 sec to wake up)
- **Solution**: Use a service like UptimeRobot to ping your app every 10 minutes

### 🔒 Security

1. **Change default password immediately**
2. **Use HTTPS only** (Render provides this automatically)
3. **Never commit `.env` to Git**
4. **Restrict access to authorized personnel only**

### 📱 Keeping App Awake (Optional)

Use cron-job.org or UptimeRobot:

1. Sign up at https://uptimerobot.com (free)
2. Add HTTP(S) monitor
3. URL: `https://your-app.onrender.com/`
4. Interval: 10 minutes
5. This keeps your app from spinning down

### 🔄 Updates

To deploy updates:

```bash
git add .
git commit -m "Update description"
git push
```

Render auto-deploys on every push to `main` branch.

### 🐛 Troubleshooting

**App won't start?**
- Check Render logs for errors
- Verify all environment variables are set
- Make sure Chrome installed successfully (check build logs)

**Token refresh not working?**
- Chrome installation issue - check build logs
- Verify METROPOLIS_EMAIL and METROPOLIS_PASSWORD are correct

**Can't login?**
- Check DASHBOARD_PASSWORD environment variable is set
- Try clearing browser cache

### 📊 Monitoring

View logs in real-time:
1. Go to Render dashboard
2. Click your service
3. Click "Logs" tab
4. See all gate openings, monitoring events, and errors

## Alternative: Docker Deployment (Advanced)

If you prefer Docker:

```dockerfile
# Create Dockerfile
FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable chromium-chromedriver \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "--worker-class", "eventlet", "-w", "1", "--bind", "0.0.0.0:5000", "app:app"]
```

Then deploy using Render's Docker option.

## Questions?

Check the main README.md for full documentation.

Happy deploying! 🚀
