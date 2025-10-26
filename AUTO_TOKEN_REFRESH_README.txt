================================================================================
🚀 METROPOLIS PARKING MANAGEMENT - AUTO TOKEN REFRESH EDITION
================================================================================

Your parking management system now includes AUTOMATIC TOKEN REFRESH that ensures
your API access never expires! This system runs completely in the background with
no visual browser windows.

================================================================================
🔄 AUTO TOKEN REFRESH FEATURES
================================================================================

✅ AUTOMATIC MONITORING
   - Checks token validity every 3 minutes
   - Detects expired or invalid tokens immediately
   - No manual intervention required

✅ HEADLESS BROWSER AUTOMATION
   - Runs invisibly in the background
   - Uses Selenium WebDriver
   - Supports Chrome, Edge, and Firefox
   - No visual browser windows

✅ INTELLIGENT TOKEN MANAGEMENT
   - Automatically logs into Metropolis
   - Intercepts API calls to capture new token
   - Verifies new token before using it
   - Saves token to persist across restarts

✅ DASHBOARD INTEGRATION
   - Real-time token status display
   - Shows last check time
   - Shows last refresh time
   - Visual indicators (green = valid, red = expired)
   - Manual "Test Token" button
   - Manual "Get New Token" button

================================================================================
📊 TOKEN STATUS INDICATORS ON DASHBOARD
================================================================================

The dashboard now shows a prominent token status card with:

🟢 GREEN BORDER + "Valid" Badge
   - Token is working correctly
   - System is fully operational
   - Auto-refresh is maintaining the token

🔴 RED BORDER + "Invalid/Expired" Badge
   - Token has expired or is invalid
   - System will auto-refresh within 3 minutes
   - Or use "Get New Token" button for immediate refresh

📅 TIMESTAMPS
   - Last Check: When token was last verified
   - Last Refresh: When token was last updated

⚠️ ERROR MESSAGES
   - Shows specific error if refresh fails
   - Helps diagnose connection issues

================================================================================
🎯 HOW IT WORKS
================================================================================

1. STARTUP
   - System loads saved token (if exists)
   - Verifies token validity
   - Starts monitoring thread

2. MONITORING (Every 3 Minutes)
   - Makes test API call to verify token
   - If valid: continues monitoring
   - If expired: triggers refresh

3. AUTO REFRESH PROCESS
   - Launches headless browser
   - Navigates to Metropolis login
   - Enters credentials automatically
   - Injects JavaScript to capture token
   - Waits for API call with token
   - Extracts and saves new token
   - Verifies new token works
   - Updates system with new token

4. PERSISTENCE
   - Saves token to auth_token.txt
   - Survives app restarts
   - Updates environment variable

================================================================================
📦 FILES INCLUDED
================================================================================

1. app.py - Main application with auto-refresh
2. requirements.txt - Basic dependencies
3. requirements-with-selenium.txt - With Selenium for auto-refresh
4. Dockerfile - Docker container with Chrome
5. docker-compose.yml - Easy Docker deployment
6. run-local.sh - Linux/Mac testing script
7. run-local.bat - Windows testing script
8. guide.txt - Complete deployment guide

================================================================================
🚀 QUICK START OPTIONS
================================================================================

OPTION 1: RENDER.COM (RECOMMENDED)
-----------------------------------
1. Upload files to GitHub
2. Connect to Render
3. Uncomment selenium in requirements.txt
4. Add Chrome buildpack
5. Set environment variables
6. Deploy!

OPTION 2: DOCKER
----------------
1. Install Docker
2. Run: docker-compose up
3. Open http://localhost:10000
4. Login with your password

OPTION 3: LOCAL TESTING
------------------------
Linux/Mac: ./run-local.sh
Windows: run-local.bat
Opens at: http://localhost:5000

================================================================================
⚙️ CONFIGURATION
================================================================================

REQUIRED ENVIRONMENT VARIABLES:
--------------------------------
SECRET_KEY=<random-32-char-string>
ADMIN_PASSWORD=<your-login-password>

FOR AUTO TOKEN REFRESH:
------------------------
AUTO_TOKEN_REFRESH=true
EMAIL=security@555capitolmall.com
PASSWORD=555_Security

OPTIONAL:
---------
AUTH_KEY=<initial-token>
BASE_URL=https://specialist.api.metropolis.io
SITE_ID=4005
PORT=10000

================================================================================
🔧 TROUBLESHOOTING
================================================================================

TOKEN REFRESH NOT WORKING?
---------------------------
1. Check Selenium is installed
2. Verify Chrome/Edge/Firefox available
3. Check EMAIL and PASSWORD are correct
4. Look at console logs for errors
5. Try manual "Get New Token" button

SELENIUM NOT AVAILABLE?
------------------------
- Install with: pip install selenium==4.16.0
- For Render: Add Chrome buildpack
- For Docker: Use provided Dockerfile
- Dashboard will show "Selenium not installed"

TOKEN STILL EXPIRES?
---------------------
- Check AUTO_TOKEN_REFRESH=true
- Verify credentials are correct
- Check network connectivity
- Review error messages on dashboard

================================================================================
🎉 BENEFITS
================================================================================

✅ NO MORE MANUAL TOKEN UPDATES
✅ 24/7 UNINTERRUPTED OPERATION
✅ AUTOMATIC ERROR RECOVERY
✅ VISUAL STATUS MONITORING
✅ HEADLESS (NO VISUAL BROWSER)
✅ WORKS ON CLOUD SERVERS
✅ PERSIST ACROSS RESTARTS
✅ FALLBACK MANUAL CONTROLS

================================================================================
📝 NOTES
================================================================================

- Token checks run every 3 minutes
- Refresh only happens when needed
- Uses minimal resources
- Works with all major browsers
- Completely headless operation
- Safe credential handling
- Automatic retry on failures

================================================================================
🔐 SECURITY
================================================================================

- Credentials stored as environment variables
- Tokens never logged in plain text
- HTTPS connections only
- Session-based authentication
- No credentials in source code
- Secure headless browser operation

================================================================================
💡 TIPS
================================================================================

1. Enable auto-refresh for production
2. Monitor dashboard regularly
3. Keep credentials secure
4. Use strong admin password
5. Rotate SECRET_KEY periodically
6. Check logs for any issues
7. Test manual refresh occasionally

================================================================================
ENJOY YOUR SELF-MAINTAINING PARKING SYSTEM! 🚗
================================================================================
