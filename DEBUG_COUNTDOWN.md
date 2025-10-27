# Debug Token Countdown Timer

## ✅ Quick Test in Browser

1. **Open Dashboard** (`http://localhost:10000`)

2. **Open Browser Console**
   - Chrome/Edge: Press `F12` → Go to "Console" tab
   - Or right-click anywhere → "Inspect" → "Console"

3. **Run These Commands in Console:**

```javascript
// Check if countdown elements exist
console.log('Countdown container:', document.getElementById('token-countdown-container'));
console.log('Countdown display:', document.getElementById('token-countdown'));
console.log('Progress bar:', document.getElementById('token-progress'));
console.log('Status text:', document.getElementById('token-status-text'));
console.log('Spinner:', document.getElementById('token-spinner'));

// Check if countdown is running
console.log('lastCheckTime:', lastCheckTime ? new Date(lastCheckTime) : 'Not set');
console.log('countdownInterval:', countdownInterval);

// Manually trigger countdown update
if (typeof updateTokenCountdown === 'function') {
    updateTokenCountdown();
    console.log('✅ Countdown update triggered');
} else {
    console.error('❌ updateTokenCountdown function not found');
}

// Check if auto-refresh is enabled
fetch('/api/token-status')
    .then(response => response.json())
    .then(data => {
        console.log('Token Status API Response:', data);
        console.log('Auto-refresh enabled:', data.auto_refresh_enabled);
        console.log('Selenium available:', data.selenium_available);
    });
```

---

## 🔍 What to Look For

### **If Countdown is Working:**
```
✅ Countdown container: <div id="token-countdown-container">...
✅ Countdown display: <span id="token-countdown">...
✅ lastCheckTime: Sun Oct 27 2025 03:19:36 GMT...
✅ countdownInterval: 123 (some number)
Console logs every second: "Checking token status..."
```

### **If Countdown is NOT Working:**
```
❌ Countdown container: null
❌ Auto-refresh enabled: false
❌ Selenium available: false
```

---

## 🛠️ Common Issues & Fixes

### **Issue 1: Countdown Container Not Found**

**Symptoms:**
```javascript
console.log('Countdown container:', null);
// Console shows: "Token countdown container not found - auto-refresh may be disabled"
```

**Cause:** `AUTO_TOKEN_REFRESH` is not set to `"true"` or Selenium is not installed

**Fix:**
```bash
# Check environment variables
echo $AUTO_TOKEN_REFRESH
echo $HAS_SELENIUM

# Should show:
# true
# (Selenium should be installed)

# If not:
export AUTO_TOKEN_REFRESH="true"
pip install selenium
```

Then restart the server:
```bash
python app.py
```

---

### **Issue 2: lastCheckTime Not Set**

**Symptoms:**
```javascript
console.log('lastCheckTime:', null);
// Console shows error: "lastCheckTime not set"
```

**Cause:** Token hasn't been checked yet on startup

**Fix:**
```javascript
// Manually set it to current time
lastCheckTime = new Date().getTime();
console.log('Set lastCheckTime to now:', new Date(lastCheckTime));

// Then manually start countdown
if (countdownInterval) clearInterval(countdownInterval);
countdownInterval = setInterval(updateTokenCountdown, 1000);
updateTokenCountdown();
```

---

### **Issue 3: Countdown Updates Once Then Stops**

**Symptoms:**
- Countdown shows "3:00" but never changes
- No console logs

**Cause:** `setInterval` not running or being cleared

**Fix:**
```javascript
// Check if interval is running
console.log('Interval ID:', countdownInterval);

// Manually restart interval
if (countdownInterval) clearInterval(countdownInterval);
countdownInterval = setInterval(function() {
    console.log('Tick...'); // Should log every second
    updateTokenCountdown();
}, 1000);
```

---

### **Issue 4: Elements Exist But Nothing Happens**

**Symptoms:**
- All elements found
- `lastCheckTime` is set
- But countdown doesn't update

**Cause:** JavaScript error stopping execution

**Fix:**
```javascript
// Check for JavaScript errors
console.clear();
try {
    updateTokenCountdown();
    console.log('✅ No errors');
} catch (e) {
    console.error('❌ Error:', e);
}

// Check if function is defined
console.log('updateTokenCountdown:', typeof updateTokenCountdown);
console.log('initTokenCountdown:', typeof initTokenCountdown);
```

---

## 🧪 Manual Test of Full Flow

Run this in browser console to simulate the full countdown:

```javascript
// 1. Set last check to 2 minutes ago
lastCheckTime = new Date().getTime() - (120 * 1000); // 2 min ago
console.log('Set last check to 2 minutes ago');

// 2. Trigger update
updateTokenCountdown();

// 3. Check countdown shows ~1:00
console.log('Countdown should show ~1:00');

// 4. Wait 5 seconds and check again
setTimeout(function() {
    updateTokenCountdown();
    console.log('After 5 seconds, should show ~0:55');
}, 5000);

// 5. Set to expire in 5 seconds
setTimeout(function() {
    lastCheckTime = new Date().getTime() - (175 * 1000); // 2min 55sec ago
    console.log('Set to expire in 5 seconds...');
}, 10000);
```

---

## 🔥 Nuclear Option: Force Restart Everything

If nothing works, run this in console:

```javascript
// 1. Clear all intervals
if (countdownInterval) {
    clearInterval(countdownInterval);
    console.log('Cleared old interval');
}

// 2. Reset variables
lastCheckTime = new Date().getTime();
console.log('Reset lastCheckTime to now');

// 3. Restart countdown
countdownInterval = setInterval(function() {
    const countdownEl = document.getElementById('token-countdown');
    const progressEl = document.getElementById('token-progress');
    const statusTextEl = document.getElementById('token-status-text');

    if (!countdownEl) {
        console.error('Countdown element not found!');
        return;
    }

    const now = new Date().getTime();
    const timeSinceCheck = Math.floor((now - lastCheckTime) / 1000);
    const timeUntilNext = Math.max(0, 180 - timeSinceCheck);

    const minutes = Math.floor(timeUntilNext / 60);
    const seconds = timeUntilNext % 60;

    countdownEl.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;

    const progressPercent = (timeUntilNext / 180) * 100;
    progressEl.style.width = progressPercent + '%';

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

    console.log(`Countdown: ${minutes}:${seconds.toString().padStart(2, '0')} (${progressPercent.toFixed(1)}%)`);
}, 1000);

console.log('✅ Countdown manually restarted - should see logs every second');
```

---

## 📋 Checklist

Before asking for help, verify:

- [ ] `AUTO_TOKEN_REFRESH="true"` is set
- [ ] Selenium is installed (`pip install selenium`)
- [ ] Server was restarted after changes
- [ ] Browser cache was cleared (Ctrl+Shift+R or Cmd+Shift+R)
- [ ] Browser console shows no JavaScript errors
- [ ] Dashboard loads without errors
- [ ] Token status shows "Valid"
- [ ] Countdown container exists in page HTML

---

## 🎯 Expected Console Output (Working)

When countdown is working correctly, console should show:

```
Initializing token countdown with last check: 2025-10-27 03:19:36
Parsed last check time: Sun Oct 27 2025 03:19:36 GMT-0700 (Pacific Daylight Time)
Token countdown timer started
(Then every update):
Countdown: 2:47 (92.2%)
Countdown: 2:46 (91.7%)
Countdown: 2:45 (91.1%)
...
```

---

## 🚨 If Still Not Working

1. **Check server logs** - ensure token monitor is actually running
2. **Verify AUTO_TOKEN_REFRESH** - must be string `"true"` not boolean
3. **Check Selenium** - `pip list | grep selenium`
4. **Clear browser cache** - Hard refresh (Ctrl+Shift+R)
5. **Try different browser** - Chrome, Edge, Firefox
6. **Check console for errors** - Look for red error messages

---

**The countdown REQUIRES both server-side monitoring AND client-side JavaScript to work together!**
