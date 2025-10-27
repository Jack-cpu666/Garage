# Troubleshooting Guide

## Token Shows "Invalid" with "Last Check: Never"

### What This Means

This indicates the token verification hasn't run yet or failed. This should **NEVER** happen in normal operation.

### What Was Fixed

1. **Initial Token Check** - Now runs BEFORE Flask app starts
2. **Immediate Refresh** - If token is invalid on startup, it refreshes immediately
3. **Monitoring Thread** - Checks token immediately on start, then every 3 minutes
4. **Better Logging** - Shows exactly what's happening

### Expected Startup Sequence

When you run `python app.py`, you should see:

```
============================================================
METROPOLIS PARKING MANAGEMENT SYSTEM - WEB APP
============================================================
📁 Loading member and blacklist data...
✅ Loaded X members and Y blacklisted plates
🔍 Verifying initial token...
✅ Initial token is VALID (or will refresh if invalid)
🔄 Starting automatic token monitoring (checks every 3 minutes)...
🚗 Starting member auto-gate monitoring...
💓 Starting keep-alive monitor...
============================================================
🎉 ALL BACKGROUND SERVICES STARTED
   - Token Monitor: ✅ ACTIVE
   - Member Auto-Gate: ✅ ACTIVE
   - Keep-Alive: ✅ ACTIVE
   - Initial Token Status: ✅ VALID
============================================================
🚀 Starting Flask app on port 10000...
```

### If Token Still Shows Invalid

1. **Check Environment Variables**
   ```bash
   # Make sure these are set
   echo $AUTH_KEY
   echo $EMAIL
   echo $PASSWORD
   echo $AUTO_TOKEN_REFRESH
   ```

2. **Check Logs** - Look for:
   ```
   [TOKEN CHECK] Token expires in Xh Ym
   ✅ Token is still valid
   ```
   OR
   ```
   ⚠️ Token expired, attempting refresh...
   ✅ New token obtained!
   ```

3. **Check Selenium**
   ```bash
   pip install selenium
   # Make sure Chrome/Edge browser is installed
   ```

4. **Manual Token Refresh**
   - Click "Get New Token" button on dashboard
   - Should launch headless browser and capture new token
   - Check console for logs

---

## Member Auto-Gate Not Opening

### How It Works (Every 3 Seconds)

```
For each site (4005, 4007):
  1. Check for active visits (cars waiting at gates)
  2. Extract license plate
  3. Check BLACKLIST first:
     - If found → LOG and DENY (gate stays closed)
  4. Check MEMBER list:
     - If found → AUTO-OPEN the specific gate they're at
  5. Track opened gates (prevent opening same gate twice)
```

### Expected Log Messages

When a member arrives:
```
[AUTO-OPEN] Member detected: ABC1234 (John Doe) at site 4005
   Transaction ID: 12345 - Lane: 5568
✅ Gate Auto Lane 5568 opened successfully
```

When a blacklisted vehicle arrives:
```
[BLOCKED] Blacklisted plate detected: XYZ999 - NOT opening gate
```

### Troubleshooting Steps

1. **Verify Member is Added**
   - Go to Members tab
   - Check license plate is in the list (all uppercase)
   - Dashboard shows: "Monitoring: X member plates"

2. **Check Monitoring is Active**
   - Dashboard should show: "Member Auto-Gate Monitor: ✅ ACTIVE"
   - If not, click "Start Monitoring"

3. **Check Member is at EXIT Gate**
   - System only detects cars at EXIT gates (not entry)
   - Member must have an active "closed visit" (ready to exit)

4. **Check Logs**
   ```bash
   # Should see this every 3 seconds when checking
   Found X active visits at site 4005
   ```

5. **Verify Blacklist Doesn't Block Member**
   - Blacklist takes priority over member list
   - Check Blacklist tab to ensure plate isn't there

---

## Token Monitor Not Running Every 3 Minutes

### Expected Behavior

```
🔄 Token monitor started - will check immediately then every 3 minutes
Running first token check...
🔍 Checking token status...
✅ Token is still valid
Next token check in 3 minutes...

(3 minutes later)

🔍 Checking token status...
✅ Token is still valid
Next token check in 3 minutes...
```

### If Not Running

1. **Check AUTO_TOKEN_REFRESH**
   ```bash
   # Must be set to "true" (string)
   export AUTO_TOKEN_REFRESH="true"
   ```

2. **Check Dashboard**
   - Should show: "Auto-Refresh: ✓ Enabled (every 3 min)"
   - Last Check time should update every 3 minutes

3. **Check Logs for Errors**
   ```bash
   # Look for:
   Token monitor error: ...
   ```

4. **Verify Thread Started**
   ```bash
   # Look for:
   ✅ Token monitor started
   ```

---

## Keep-Alive Not Preventing Server Sleep

### Expected Behavior

```
(Every 60 seconds)
Keep-alive ping - Active monitors: Token=True, Members=True
```

### If Server Still Sleeps

1. **Use Paid Hosting**
   - Free tiers (Render, Heroku) sleep after 15 min inactivity
   - Paid tiers stay awake 24/7

2. **External Monitoring**
   - Set up UptimeRobot to ping your server every 5 minutes
   - Or use cron job: `curl https://your-app.com/api/monitoring-status`

3. **Check Logs**
   - Should see keep-alive messages every 60 seconds
   - If not, thread may have crashed

---

## Dashboard Shows Wrong Member Count

### Issue

Dashboard shows "Monitoring: 0 member plates" but you've added members.

### Solution

1. **Restart Application**
   - Member list loads from `memberships.json` on startup
   - Changes in dashboard update the file immediately

2. **Check File Exists**
   ```bash
   ls -la memberships.json
   cat memberships.json
   ```

3. **Verify JSON Format**
   ```json
   [
     "ABC1234",
     "XYZ5678"
   ]
   ```

---

## Environment Variables Not Loading

### Issue

Dashboard shows "Selenium not installed" or token refresh fails.

### Check Environment

```bash
# Print all relevant env vars
echo "AUTH_KEY length: ${#AUTH_KEY}"
echo "EMAIL: $EMAIL"
echo "AUTO_TOKEN_REFRESH: $AUTO_TOKEN_REFRESH"
echo "ADMIN_PASSWORD: $ADMIN_PASSWORD"
```

### Set Environment Variables

**Linux/Mac:**
```bash
export AUTH_KEY="your-token-here"
export EMAIL="security@555capitolmall.com"
export PASSWORD="555_Security"
export ADMIN_PASSWORD="admin555"
export AUTO_TOKEN_REFRESH="true"
```

**Windows:**
```cmd
set AUTH_KEY=your-token-here
set EMAIL=security@555capitolmall.com
set PASSWORD=555_Security
set ADMIN_PASSWORD=admin555
set AUTO_TOKEN_REFRESH=true
```

**Or use .env file:**
```bash
# Create .env file
cat > .env <<EOF
AUTH_KEY=your-token-here
EMAIL=security@555capitolmall.com
PASSWORD=555_Security
ADMIN_PASSWORD=admin555
AUTO_TOKEN_REFRESH=true
EOF

# Load it
source .env  # Linux/Mac
# OR load in Python with python-dotenv
```

---

## Common Errors and Solutions

### Error: "Selenium not available"

```bash
pip install selenium
# Install browser driver
# Chrome: https://chromedriver.chromium.org/
# Edge: Included with Edge browser
```

### Error: "Token decode error"

- AUTH_KEY is invalid or corrupted
- Check that token has 3 parts separated by dots: `header.payload.signature`
- Get fresh token from Metropolis portal

### Error: "Could not open gate"

- Token is invalid/expired
- Gate ID is wrong
- API endpoint changed
- Check logs for HTTP status code

### Error: "Address already in use"

```bash
# Port 10000 is already used
# Kill existing process
lsof -ti:10000 | xargs kill -9
# Or use different port
PORT=10001 python app.py
```

---

## Debugging Tips

### Enable Debug Logging

```python
# In app.py, change:
logging.basicConfig(level=logging.DEBUG)
```

### Test Token Manually

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     https://specialist.api.metropolis.io/api/site/4005/occupancy
```

### Check Background Threads

```python
# Add to dashboard
import threading
print("Active threads:", threading.active_count())
for thread in threading.enumerate():
    print(f"  - {thread.name}")
```

### Monitor Real-Time

```bash
# Watch logs in real-time
tail -f app.log

# Or in Python console
python app.py 2>&1 | tee app.log
```

---

## Still Having Issues?

1. **Check README.md** - Comprehensive documentation
2. **Review startup logs** - Shows exactly what's happening
3. **Test with manual refresh** - Click "Get New Token" button
4. **Verify environment** - All required variables set
5. **Check browser driver** - Selenium can launch browser

---

**The system should NEVER show "Invalid" or "Never" if configured correctly. If it does, there's an environment or configuration issue.**
