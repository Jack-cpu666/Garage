# Metropolis Parking Management System - Web Application

## 🚀 Overview

This is a comprehensive web-based parking management system for Metropolis parking garages. The system features **persistent background monitoring** that continues to work even when you close your browser.

### Key Features

- ✅ **Auto Token Refresh** - Automatically refreshes authentication tokens every 3 minutes
- ✅ **Member Auto-Gate** - Automatically opens gates for registered members
- ✅ **Blacklist Management** - Blocks specific vehicles from entry
- ✅ **Member Directory** - View all members with subscriptions
- ✅ **Real-time Activity** - Live vehicle entry/exit monitoring with camera images
- ✅ **Multi-Site Support** - Manages multiple parking sites (555 Capitol Mall & Bank of America)
- ✅ **Background Processing** - All monitoring continues in the background server-side

---

## 🔧 What Was Fixed

### The Problem

The previous web version had a critical issue: **background tasks would stop when the browser was closed**. This is because:

1. Web browsers only run JavaScript while the page is open
2. If the server goes to sleep (common on free hosting like Render.com), all background threads stop
3. The token auto-refresh and member monitoring were not persistent

### The Solution

The updated version now includes:

1. **Server-Side Background Threads**
   - Token monitoring runs server-side (not in browser)
   - Member auto-gate monitoring runs server-side
   - Keep-alive mechanism prevents server sleep

2. **Persistent Monitoring**
   - Token check: Every 3 minutes
   - Member auto-gate check: Every 3 seconds
   - Keep-alive ping: Every 60 seconds

3. **Automatic Token Management**
   - Detects token expiration (5-minute buffer)
   - Automatically logs in via headless browser
   - Captures fresh token via JavaScript injection
   - Updates all API calls with new token

4. **Member Auto-Gate System**
   - Continuously monitors active visits
   - Checks member plates against registered list
   - Checks blacklist first (takes priority)
   - Opens appropriate gate automatically
   - Prevents duplicate gate operations

---

## 📋 Requirements

### Python Packages
```bash
pip install flask requests selenium
```

### Browser Driver (for auto token refresh)
Choose ONE of the following:

- **Chrome/Chromium** (recommended for Linux servers)
  ```bash
  # Install Chrome and ChromeDriver
  wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
  sudo apt-get install ./google-chrome-stable_current_amd64.deb
  ```

- **Edge** (recommended for Windows)
  - Install Microsoft Edge browser
  - Edge WebDriver is usually included

- **Firefox**
  - Install Firefox browser
  - Download geckodriver

---

## 🚀 Quick Start

### 1. Clone and Setup

```bash
cd /path/to/Garage-main
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file or set these environment variables:

```bash
# Required
AUTH_KEY="your-jwt-token-here"
EMAIL="your-metropolis-email@example.com"
PASSWORD="your-metropolis-password"
ADMIN_PASSWORD="your-dashboard-password"

# Optional
BASE_URL="https://specialist.api.metropolis.io"
SITE_ID="4005"
PORT="10000"
AUTO_TOKEN_REFRESH="true"
```

### 3. Run the Application

**Development:**
```bash
python app.py
```

**Production (Recommended):**
```bash
gunicorn app:app --bind 0.0.0.0:10000 --workers 1 --timeout 120
```

> ⚠️ **IMPORTANT**: Use `--workers 1` to ensure background threads persist. Multiple workers will create duplicate monitoring threads.

### 4. Access the Dashboard

Open your browser to:
```
http://localhost:10000
```

Login with your `ADMIN_PASSWORD`.

---

## 🌐 Deployment

### Render.com Deployment

1. **Create `render.yaml`** (already included):
```yaml
services:
  - type: web
    name: metropolis-parking
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "python app.py"
    envVars:
      - key: AUTH_KEY
        sync: false
      - key: EMAIL
        sync: false
      - key: PASSWORD
        sync: false
      - key: ADMIN_PASSWORD
        sync: false
      - key: AUTO_TOKEN_REFRESH
        value: "true"
```

2. **Push to GitHub**
3. **Connect to Render.com**
4. **Set Environment Variables** in Render dashboard
5. **Deploy**

### Important for Production

- ✅ Set `AUTO_TOKEN_REFRESH=true` to enable automatic token refresh
- ✅ Install Chrome/ChromeDriver for headless browser token capture
- ✅ Use a persistent hosting service (not free tiers that sleep)
- ✅ Monitor logs to ensure background services start correctly

---

## 📱 Features Explained

### 1. Dashboard
- **Token Status** - Shows current API token validity and auto-refresh status
- **Member Monitor Status** - Shows if auto-gate monitoring is active
- **Live Stats** - Current occupancy, waiting cars, member count
- **Quick Actions** - Fast access to common operations

### 2. Gate Controls
- Manual gate control for all locations:
  - 555 Capitol Mall (6th Street Exit, L Street Exit)
  - Bank of America (Main Exit)

### 3. Transactions
- Live vehicle activity with camera images
- Entry/Exit events with timestamps
- License plate recognition
- Filter by plate, site, or type

### 4. Members Management
- **Members Tab**:
  - Add/remove member plates
  - Auto-gate opens for registered members
- **Blacklist Tab**:
  - Add/remove blocked vehicles
  - Blacklist takes priority over members

### 5. Visitor Pass
- Create temporary access passes
- Set duration (1-24 hours)
- Site-specific passes

### 6. Member Directory
- View all members with active subscriptions
- See vehicle details (make, model, color, plate)
- Phone numbers and last visit times
- Auto-refreshes every 30 seconds

---

## 🔍 Background Services Explained

### Token Monitor (Every 3 minutes)
```python
while monitoring_active:
    1. Check if token is expired (or expires within 5 minutes)
    2. If expired:
       - Launch headless browser
       - Auto-login to Metropolis
       - Inject JavaScript to capture token
       - Update AUTH_KEY globally
       - Save to file for persistence
    3. Sleep for 3 minutes
```

### Member Auto-Gate Monitor (Every 3 seconds)
```python
while member_monitoring_active:
    For each site (4005, 4007):
        1. Get active visits (cars at gates)
        2. Extract license plate
        3. Check blacklist FIRST:
           - If blacklisted: LOG and DENY
        4. Check member list:
           - If member: AUTO-OPEN gate
        5. Track opened gates (prevent duplicates)
    Sleep for 3 seconds
```

### Keep-Alive Monitor (Every 60 seconds)
```python
while True:
    1. Update activity timestamp
    2. Log status of all monitors
    3. Sleep for 60 seconds
```

---

## 🛠️ Troubleshooting

### Token Refresh Not Working

**Symptom:** Token expires and doesn't auto-refresh

**Solutions:**
1. Check Selenium is installed: `pip install selenium`
2. Verify browser driver is installed (Chrome/Edge/Firefox)
3. Check logs for token refresh errors
4. Verify `AUTO_TOKEN_REFRESH=true` in environment
5. Manually test with "Get New Token" button

### Member Auto-Gate Not Working

**Symptom:** Gates don't open for members

**Solutions:**
1. Check member plates are added correctly (all uppercase)
2. Verify member monitoring status on dashboard (should show ✅ ACTIVE)
3. Check server logs for "[AUTO-OPEN]" messages
4. Ensure members are at the EXIT gate (not entry)
5. Verify member vehicles have active transactions

### Server Goes to Sleep

**Symptom:** Everything stops working after inactivity

**Solutions:**
1. **Use paid hosting** - Free tiers often sleep after 15 minutes
2. Set up external monitoring (UptimeRobot, etc.)
3. Use a cron job to ping your server every 5 minutes
4. Consider using a VPS or dedicated server

### Background Services Stop

**Symptom:** Monitoring shows ❌ STOPPED on dashboard

**Solutions:**
1. Check server logs for errors
2. Restart the application
3. Verify `--workers 1` in production (not multiple workers)
4. Check for exceptions in monitoring loops

---

## 📊 API Endpoints

### Gate Control
- `POST /api/open-gate` - Open a specific gate
- `GET /api/occupancy/<site_id>` - Get current occupancy
- `GET /api/waiting-count` - Get cars waiting at exit

### Member Management
- `POST /api/members/add` - Add member plate
- `POST /api/members/remove` - Remove member plate
- `POST /api/blacklist/add` - Add to blacklist
- `POST /api/blacklist/remove` - Remove from blacklist

### Monitoring
- `GET /api/monitoring-status` - Get status of all monitors
- `POST /api/toggle-member-monitoring` - Start/stop member monitoring
- `GET /api/token-status` - Get current token status
- `POST /api/refresh-token` - Manually refresh token

### Data
- `GET /api/member-directory` - Get all members
- `POST /api/recent-activity` - Get recent vehicle activity
- `GET /api/recent-transactions` - Get recent transactions

---

## 🔒 Security Notes

- ✅ Password-protected admin dashboard
- ✅ Session-based authentication
- ✅ Tokens stored securely in environment variables
- ⚠️ Use HTTPS in production
- ⚠️ Keep credentials in `.env` file (not in code)
- ⚠️ Don't commit `.env` to Git

---

## 📝 File Structure

```
Garage-main/
├── app.py                     # Main Flask application
├── WORKING_GATE_OPENER.py     # Original desktop version (reference)
├── memberships.json           # Member plates storage
├── blacklist.json             # Blacklisted plates storage
├── auth_token.txt             # Current auth token (auto-created)
├── utils/
│   ├── token_manager.py       # Token refresh functions
│   ├── token_monitor.py       # Token monitoring thread
│   ├── gate_control.py        # Gate API functions
│   └── monitoring.py          # Member monitoring functions
├── requirements.txt           # Python dependencies
├── render.yaml                # Render.com deployment config
└── README.md                  # This file
```

---

## 🎯 Differences from Desktop Version

| Feature | Desktop (Tkinter) | Web Version |
|---------|-------------------|-------------|
| **Interface** | Desktop GUI | Web Browser |
| **Accessibility** | Local machine only | Accessible from anywhere |
| **Background Tasks** | Works as long as app runs | Works as long as server runs |
| **Multi-User** | Single user | Multiple users (login required) |
| **Platform** | Windows/Mac/Linux | Any device with browser |
| **Updates** | Requires restart | Hot reload in browser |

---

## 💡 Best Practices

1. **Always use production server** (not free tier that sleeps)
2. **Monitor logs regularly** for "[AUTO-OPEN]" and "[TOKEN CHECK]" messages
3. **Keep member list updated** - add/remove as needed
4. **Check dashboard daily** to ensure monitors are active
5. **Use blacklist carefully** - it overrides member access
6. **Backup `memberships.json` and `blacklist.json` regularly**

---

## 🆘 Support

If you encounter issues:

1. Check the **Troubleshooting** section above
2. Review server logs for error messages
3. Test manually with "Get New Token" button
4. Verify environment variables are set correctly
5. Ensure Selenium and browser driver are installed

---

## 📜 License

This software is for authorized use only. Ensure you have proper authorization to access Metropolis API and control parking gates.

---

## ✅ Changelog

### v2.0 (Current) - Background Services Update
- ✅ Added persistent server-side token monitoring
- ✅ Added member auto-gate monitoring
- ✅ Added keep-alive mechanism
- ✅ Fixed browser closing issue
- ✅ Improved dashboard with monitoring status
- ✅ Renamed "Cameras" to "Member Directory"
- ✅ Added blacklist priority check
- ✅ Enhanced logging and error handling

### v1.0 - Initial Web Version
- Basic web interface
- Manual gate controls
- Token management
- Member list management

---

**Made with ❤️ for 555 Capitol Mall & Bank of America Parking**
