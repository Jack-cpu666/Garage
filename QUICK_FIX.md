# 🔥 QUICK FIX - Countdown Not Ticking

## The Problem

Your screenshot shows **"Next check in: 3:00"** but it's NOT counting down. This means:

1. ✅ The countdown HTML is rendering (you can see it)
2. ❌ The JavaScript countdown is NOT running

---

## ⚡ Quick Fix #1: Check Environment Variables

```bash
# Stop the server (Ctrl+C)

# Check if AUTO_TOKEN_REFRESH is set correctly
echo $AUTO_TOKEN_REFRESH

# If it's not "true", set it:
export AUTO_TOKEN_REFRESH="true"

# Or on Windows:
set AUTO_TOKEN_REFRESH=true

# Restart server
python app.py
```

---

## ⚡ Quick Fix #2: Hard Refresh Browser

The old JavaScript might be cached:

1. **Chrome/Edge/Firefox:**
   - Press: `Ctrl + Shift + R` (Windows)
   - Or: `Cmd + Shift + R` (Mac)

2. **Or clear cache manually:**
   - Press `F12` to open DevTools
   - Right-click the refresh button
   - Select "Empty Cache and Hard Reload"

---

## ⚡ Quick Fix #3: Check Browser Console

1. **Open browser console:**
   - Press `F12`
   - Go to "Console" tab

2. **Look for these messages:**
   ```
   ✅ SHOULD SEE:
   "Initializing token countdown with last check: 2025-10-27 03:19:36"
   "Token countdown timer started"

   ❌ IF YOU SEE:
   "Token countdown container not found - auto-refresh may be disabled"
   "Token countdown elements not found"
   "lastCheckTime not set"
   ```

3. **If you see errors, run this in console:**
   ```javascript
   // Check if countdown elements exist
   console.log('Container:', document.getElementById('token-countdown-container'));
   console.log('Display:', document.getElementById('token-countdown'));

   // If both are null, auto-refresh is disabled
   // If both exist, try manual start:
   lastCheckTime = new Date().getTime();
   if (countdownInterval) clearInterval(countdownInterval);
   countdownInterval = setInterval(updateTokenCountdown, 1000);
   updateTokenCountdown();
   console.log('✅ Manually started countdown');
   ```

---

## ⚡ Quick Fix #4: Verify Server Logs

Check your server console for these messages at startup:

```
✅ SHOULD SEE:
============================================================
METROPOLIS PARKING MANAGEMENT SYSTEM - WEB APP
============================================================
📁 Loading member and blacklist data...
✅ Loaded X members and Y blacklisted plates
🔍 Verifying initial token...
✅ Initial token is VALID
🔄 Starting automatic token monitoring (checks every 3 minutes)...
✅ Token monitor started  <-- THIS IS CRITICAL
```

```
❌ IF YOU SEE:
ℹ️ Auto token refresh is disabled  <-- THIS MEANS IT'S OFF
```

If auto-refresh is disabled, check your `.env` file or environment variables.

---

## ⚡ Quick Fix #5: Manual JavaScript Restart

If everything is set up correctly but countdown still won't start, paste this into browser console:

```javascript
// Force restart countdown
(function() {
    console.log('🔧 Force restarting countdown...');

    // Get last check time from page
    const lastCheckText = document.getElementById('last-check-time').textContent;
    console.log('Last check from page:', lastCheckText);

    // Parse it
    window.lastCheckTime = new Date(lastCheckText).getTime();
    if (isNaN(window.lastCheckTime)) {
        console.log('Could not parse, using current time');
        window.lastCheckTime = new Date().getTime();
    }

    console.log('Set lastCheckTime to:', new Date(window.lastCheckTime));

    // Clear any existing interval
    if (window.countdownInterval) {
        clearInterval(window.countdownInterval);
        console.log('Cleared old interval');
    }

    // Start new interval
    window.countdownInterval = setInterval(function() {
        const countdownEl = document.getElementById('token-countdown');
        const progressEl = document.getElementById('token-progress');
        const statusTextEl = document.getElementById('token-status-text');

        if (!countdownEl || !progressEl || !statusTextEl) {
            console.error('❌ Countdown elements missing');
            return;
        }

        const now = new Date().getTime();
        const timeSinceCheck = Math.floor((now - window.lastCheckTime) / 1000);
        const timeUntilNext = Math.max(0, 180 - timeSinceCheck);

        const minutes = Math.floor(timeUntilNext / 60);
        const seconds = timeUntilNext % 60;

        // Update display
        countdownEl.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;

        // Update progress bar
        const progressPercent = (timeUntilNext / 180) * 100;
        progressEl.style.width = progressPercent + '%';

        // Update status text and color
        if (timeUntilNext <= 10) {
            progressEl.className = 'progress-bar progress-bar-striped progress-bar-animated bg-danger';
            statusTextEl.textContent = 'Checking now...';
        } else if (timeUntilNext <= 30) {
            progressEl.className = 'progress-bar progress-bar-striped progress-bar-animated bg-warning';
            statusTextEl.textContent = 'Checking soon...';
        } else {
            progressEl.className = 'progress-bar progress-bar-striped progress-bar-animated bg-info';
            statusTextEl.textContent = 'Waiting for next automatic check...';
        }

        // Log every 10 seconds
        if (seconds % 10 === 0) {
            console.log(`⏱️ Countdown: ${minutes}:${seconds.toString().padStart(2, '0')}`);
        }

        // When it hits zero, fetch new status
        if (timeUntilNext === 0) {
            console.log('🔄 Countdown reached 0, fetching new status...');
            fetch('/api/token-status')
                .then(response => response.json())
                .then(data => {
                    if (data.last_check && data.last_check !== 'Never') {
                        window.lastCheckTime = new Date(data.last_check).getTime();
                        document.getElementById('last-check-time').textContent = data.last_check;
                        console.log('✅ Updated last check to:', data.last_check);
                    }
                })
                .catch(error => console.error('❌ Fetch error:', error));
        }
    }, 1000);

    // Trigger immediate update
    setTimeout(function() {
        const countdownEl = document.getElementById('token-countdown');
        if (countdownEl) {
            console.log('✅ Countdown started successfully');
            console.log('   Current display:', countdownEl.textContent);
            console.log('   Watch for updates every second...');
        } else {
            console.error('❌ Failed to start - countdown element not found');
        }
    }, 100);

    console.log('🎉 Countdown force-restarted! Check console for updates every 10 seconds.');
})();
```

After pasting this, you should see console logs every 10 seconds showing the countdown ticking down.

---

## 🎯 Root Cause Analysis

### **Most Likely Causes:**

1. **AUTO_TOKEN_REFRESH not set to "true"**
   - Check: `echo $AUTO_TOKEN_REFRESH`
   - Fix: `export AUTO_TOKEN_REFRESH="true"`

2. **Selenium not installed**
   - Check: `pip list | grep selenium`
   - Fix: `pip install selenium`

3. **Browser cache has old JavaScript**
   - Fix: Hard refresh (`Ctrl+Shift+R`)

4. **JavaScript error stopping countdown**
   - Check: Browser console for red errors
   - Fix: See Quick Fix #5 above

---

## 📝 Verification Steps

After trying fixes above:

1. ✅ Countdown shows time (e.g., "2:47")
2. ✅ Countdown CHANGES every second (2:47 → 2:46 → 2:45)
3. ✅ Progress bar SHRINKS from left to right
4. ✅ Status text shows "Waiting for next automatic check..."
5. ✅ Browser console shows "Token countdown timer started"
6. ✅ Server logs show "🔄 Token monitor started"

---

## 🔥 If STILL Not Working

**Do this:**

1. **Stop server** (`Ctrl+C`)

2. **Set environment variable:**
   ```bash
   export AUTO_TOKEN_REFRESH="true"
   # Windows: set AUTO_TOKEN_REFRESH=true
   ```

3. **Verify it's set:**
   ```bash
   echo $AUTO_TOKEN_REFRESH  # Should show: true
   ```

4. **Start server:**
   ```bash
   python app.py
   ```

5. **Check startup logs** - Should see:
   ```
   🔄 Starting automatic token monitoring (checks every 3 minutes)...
   ✅ Token monitor started
   ```

6. **Open dashboard in NEW incognito/private window**
   - This bypasses all cache

7. **Open console immediately** (`F12`)
   - Should see: "Token countdown timer started"

8. **Wait 5 seconds**
   - Countdown should tick: 3:00 → 2:59 → 2:58 → 2:57 → 2:56 → 2:55

---

## 💡 The Real Issue

**From your screenshot:**
- ✅ Token is Valid
- ✅ Last Check time is shown
- ✅ Auto-Refresh shows "Enabled"
- ✅ Countdown HTML exists
- ❌ Countdown is stuck at "3:00"

**This means:** The HTML rendered correctly, but the JavaScript `setInterval` is not running.

**Most likely cause:** Browser cached the old JavaScript that doesn't have the countdown code.

**Solution:** Hard refresh (`Ctrl+Shift+R`) or use incognito mode.

---

**Try the hard refresh first - that's the most common fix!**
