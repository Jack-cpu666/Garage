from flask import Flask, render_template, render_template_string, request, jsonify, session, redirect, url_for, flash, get_flashed_messages
import requests
import json
import os
import base64
import re
from datetime import datetime, timedelta
import threading
import time
from functools import wraps
import secrets
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))

# Configuration from environment variables
AUTH_KEY = os.environ.get('AUTH_KEY', 'eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJpbXpVMnE4NXQxSDB5U2RpUHRKNmtmeWpkYXZlR2ZiaHdyZ01KbXNHZTQ4In0.eyJleHAiOjE3NjE0NTMwOTMsImlhdCI6MTc2MTQ0OTQ5MywiYXV0aF90aW1lIjoxNzYxNDQ5NDkyLCJqdGkiOiJlZmI2NzY2ZS04MTFlLTQzMmUtODc0Yy05NDc3YTRhYTIxMGQiLCJpc3MiOiJodHRwczovL2F1dGgubWV0cm9wb2xpcy5pby9yZWFsbXMvbWV0cm9wb2xpcyIsImF1ZCI6WyJtZXRyb3BvbGlzLXJlc291cmNlLWNsaWVudCIsIm1ldHJvcG9saXMtdXNlci1jbGllbnQiLCJtZXRyb3BvbGlzLXNlcnZlci1jbGllbnQiLCJhY2NvdW50Il0sInN1YiI6ImU2MzEzOWI2LWUyNzgtNGUwNS05ZDJmLTMzZWUxOGQwZGI4YyIsInR5cCI6IkJlYXJlciIsImF6cCI6Im1ldHJvcG9saXMtd2ViLWNsaWVudCIsIm5vbmNlIjoiMzA5MzA4MTYtM2JlYS00NTg1LTkyYWEtMzJlMDYwYzBhNjIzIiwic2Vzc2lvbl9zdGF0ZSI6ImQxMDk4YWJlLTM0ZTYtNGQ2Ny1hMTk2LTdlZWI3YTQ4YWRjZSIsImFjciI6IjEiLCJhbGxvd2VkLW9yaWdpbnMiOlsiaHR0cHM6Ly9tYW5hZ2VyLm1ldHJvcG9saXMuaW8iLCJodHRwczovL3BvcnRhbC5tZXRyb3BvbGlzLmlvIiwiaHR0cHM6Ly9yZXF1ZXN0Lm1ldHJvcG9saXMuaW8iLCJodHRwczovL2ludGFrZS5tZXRyb3BvbGlzLmlvIiwiaHR0cHM6Ly9kZXZvcHMudG9vbHMubWV0cm9wLmlvIiwiaHR0cHM6Ly9oYXJkd2FyZS5lZGdlLm1ldHJvcG9saXMuaW8iLCJodHRwczovL3NwZWNpYWxpc3QubWV0cm9wb2xpcy5pbyIsImh0dHA6Ly9sb2NhbGhvc3Q6MzAwMSIsImh0dHA6Ly9sb2NhbGhvc3Q6MzAwMCIsImh0dHBzOi8vZWRnZS5hdGcubWV0cm9wb2xpcy5pbyJdLCJyZWFsbV9hY2Nlc3MiOnsicm9sZXMiOlsiZGVmYXVsdC1yb2xlcy10ZXN0Iiwib2ZmbGluZV9hY2Nlc3MiLCJ1bWFfYXV0aG9yaXphdGlvbiJdfSwicmVzb3VyY2VfYWNjZXNzIjp7Im1ldHJvcG9saXMtc2VydmVyLWNsaWVudCI6eyJyb2xlcyI6WyJlbmZvcmNlbWVudCIsInBhcmtpbmcgcGFzcyIsInZhbGV0IiwiaW50YWtlIiwib3BlcmF0b3IiXX19LCJzY29wZSI6Im9wZW5pZCBwcm9maWxlIGVtYWlsIiwic2lkIjoiZDEwOThhYmUtMzRlNi00ZDY3LWExOTYtN2VlYjdhNDhhZGNlIiwiZW1haWxfdmVyaWZpZWQiOnRydWUsIm5hbWUiOiI1NTUgU2VjdXJpdHkgIiwicHJlZmVycmVkX3VzZXJuYW1lIjoic2VjdXJpdHlANTU1Y2FwaXRvbG1hbGwuY29tIiwiZ2l2ZW5fbmFtZSI6IjU1NSIsImZhbWlseV9uYW1lIjoiU2VjdXJpdHkgIiwiZW1haWwiOiJzZWN1cml0eUA1NTVjYXBpdG9sbWFsbC5jb20ifQ.Xcaxd5K_0sazYYyaqDZiKWapPLqkKcrJcr6ox_Uei-PpRNLBRFTcjCuj3EAHTVL1Va0w0WFvY0uVP51PTRnrx8IvZsNpbu38B9BF6a_gjk0oMHSIb8A3Eu-rQsNdniiirDk7Yy_f-7mp6FCa6xIr83rHeyNnwMdTP_EkOzD-fUSgLtUVWmM9JoRDlv9U2A6hM1gVehV3EY5T5PQH4IcHATkeJmCWCA2N5KTjCmTHNVlWyrX84YX6TGmuDIdzJCdb2WHfOIM5Pf6128s-BHDhurB-nF27ktZ7dlbQOUkaCiIUlHzMqdAVqHRJK-eyX0Fd6KBUZa64cuJoanZNRTGldQ')
BASE_URL = os.environ.get('BASE_URL', 'https://specialist.api.metropolis.io')
SITE_ID = os.environ.get('SITE_ID', '4005')
EMAIL = os.environ.get('EMAIL', 'security@555capitolmall.com')
PASSWORD = os.environ.get('PASSWORD', '555_Security')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin555')
AUTO_TOKEN_REFRESH = os.environ.get('AUTO_TOKEN_REFRESH', 'true').lower() == 'true'

# Storage files (matches WORKING_GATE_OPENER.py)
MEMBERS_FILE = "memberships.json"
BLACKLIST_FILE = "blacklist.json"

# In-memory storage
member_plates = []
blacklist_plates = []
monitoring_active = False
token_status = {'valid': False, 'last_check': None, 'last_refresh': None, 'error': None}
token_monitor_thread = None

def load_members():
    """Load member plates from JSON file"""
    global member_plates
    if os.path.exists(MEMBERS_FILE):
        try:
            with open(MEMBERS_FILE, 'r') as f:
                member_plates = json.load(f)
            logger.info(f"Loaded {len(member_plates)} member plates")
        except Exception as e:
            logger.error(f"Error loading members: {e}")
            member_plates = []
    else:
        member_plates = []

def save_members():
    """Save member plates to JSON file"""
    try:
        with open(MEMBERS_FILE, 'w') as f:
            json.dump(member_plates, f, indent=2)
        logger.info(f"Saved {len(member_plates)} member plates")
    except Exception as e:
        logger.error(f"Error saving members: {e}")

def load_blacklist():
    """Load blacklisted plates from JSON file"""
    global blacklist_plates
    if os.path.exists(BLACKLIST_FILE):
        try:
            with open(BLACKLIST_FILE, 'r') as f:
                blacklist_plates = json.load(f)
            logger.info(f"Loaded {len(blacklist_plates)} blacklisted plates")
        except Exception as e:
            logger.error(f"Error loading blacklist: {e}")
            blacklist_plates = []
    else:
        blacklist_plates = []

def save_blacklist():
    """Save blacklisted plates to JSON file"""
    try:
        with open(BLACKLIST_FILE, 'w') as f:
            json.dump(blacklist_plates, f, indent=2)
        logger.info(f"Saved {len(blacklist_plates)} blacklisted plates")
    except Exception as e:
        logger.error(f"Error saving blacklist: {e}")

# Try importing Selenium for auto token refresh
HAS_SELENIUM = False
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.edge.options import Options as EdgeOptions
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.firefox.options import Options as FirefoxOptions
    HAS_SELENIUM = True
    logger.info("✅ Selenium available - Auto token refresh enabled")
except ImportError:
    logger.warning("⚠️ Selenium not available - Auto token refresh disabled")
    logger.warning("Install with: pip install selenium")

def verify_token():
    """Verify if current token is valid by making a test API call"""
    global AUTH_KEY, token_status

    try:
        # Use the correct endpoint format (singular "site" not "sites")
        url = f"{BASE_URL}/api/site/{SITE_ID}/occupancy"
        headers = {
            "Authorization": f"Bearer {AUTH_KEY}",
            "Accept": "*/*"
        }

        logger.info(f"Verifying token... (length: {len(AUTH_KEY)}, dots: {AUTH_KEY.count('.')})")
        response = requests.get(url, headers=headers, timeout=10)

        logger.info(f"Verification response: {response.status_code}")

        if response.status_code == 200:
            token_status['valid'] = True
            token_status['last_check'] = datetime.now()
            token_status['error'] = None
            logger.info("✅ Token is valid")
            return True
        elif response.status_code == 401:
            token_status['valid'] = False
            token_status['error'] = 'Token expired or invalid'
            logger.warning(f"❌ Token is invalid/expired - Response: {response.text[:200]}")
            return False
        else:
            error_msg = f'Unexpected status: {response.status_code}'
            token_status['error'] = error_msg
            logger.warning(f"⚠️ {error_msg} - Response: {response.text[:200]}")
            return False

    except Exception as e:
        token_status['error'] = str(e)
        logger.error(f"Error verifying token: {e}")
        return False

def get_new_token_selenium():
    """Get a new token using headless Selenium"""
    if not HAS_SELENIUM:
        logger.error("Selenium not available")
        return None
    
    driver = None
    try:
        logger.info("🤖 Starting headless token refresh...")
        
        # Try different browsers in order of preference
        browsers = []
        
        # Try Edge first
        try:
            edge_options = EdgeOptions()
            edge_options.add_argument('--headless')
            edge_options.add_argument('--no-sandbox')
            edge_options.add_argument('--disable-dev-shm-usage')
            edge_options.add_argument('--disable-gpu')
            edge_options.add_argument('--window-size=1920,1080')
            edge_options.add_experimental_option('excludeSwitches', ['enable-logging'])
            browsers.append(('edge', lambda: webdriver.Edge(options=edge_options)))
        except:
            pass
        
        # Try Chrome
        try:
            chrome_options = ChromeOptions()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
            browsers.append(('chrome', lambda: webdriver.Chrome(options=chrome_options)))
        except:
            pass
        
        # Try Firefox
        try:
            firefox_options = FirefoxOptions()
            firefox_options.add_argument('--headless')
            firefox_options.add_argument('--width=1920')
            firefox_options.add_argument('--height=1080')
            browsers.append(('firefox', lambda: webdriver.Firefox(options=firefox_options)))
        except:
            pass
        
        if not browsers:
            logger.error("No browser drivers available")
            return None
        
        # Try each browser until one works
        for browser_name, browser_func in browsers:
            try:
                logger.info(f"Trying {browser_name}...")
                driver = browser_func()
                break
            except Exception as e:
                logger.warning(f"{browser_name} failed: {e}")
                continue
        
        if not driver:
            logger.error("Could not initialize any browser")
            return None
        
        # Navigate to login page
        login_url = f"https://specialist.metropolis.io/site/{SITE_ID}"
        logger.info(f"Navigating to {login_url}")
        driver.get(login_url)
        time.sleep(3)
        
        # Login
        logger.info("Logging in...")
        email_field = driver.find_element(By.ID, "username")
        email_field.send_keys(EMAIL)
        time.sleep(1)
        
        password_field = driver.find_element(By.ID, "password")
        password_field.send_keys(PASSWORD)
        password_field.send_keys(Keys.RETURN)
        time.sleep(5)
        
        # Inject JavaScript to capture token (using exact logic from get token.py)
        logger.info("Injecting token interceptor...")
        intercept_script = """
        window.capturedToken = null;

        // Override fetch
        const originalFetch = window.fetch;
        window.fetch = function(...args) {
            const [url, config] = args;

            // Capture Authorization header
            if (config && config.headers) {
                const auth = config.headers['Authorization'] || config.headers['authorization'];
                if (auth && auth.startsWith('Bearer ')) {
                    window.capturedToken = auth.replace('Bearer ', '');
                    console.log('✅ Captured token from fetch!');
                }
            }

            return originalFetch.apply(this, args);
        };

        // Override XMLHttpRequest
        const originalOpen = XMLHttpRequest.prototype.open;
        const originalSetHeader = XMLHttpRequest.prototype.setRequestHeader;

        XMLHttpRequest.prototype.open = function(...args) {
            this._requestHeaders = {};
            return originalOpen.apply(this, args);
        };

        XMLHttpRequest.prototype.setRequestHeader = function(header, value) {
            this._requestHeaders[header] = value;

            if (header.toLowerCase() === 'authorization' && value.startsWith('Bearer ')) {
                window.capturedToken = value.replace('Bearer ', '');
                console.log('✅ Captured token from XHR!');
            }

            return originalSetHeader.apply(this, arguments);
        };

        console.log('🎣 Fetch interceptor installed!');
        """

        driver.execute_script(intercept_script)

        # Wait for token capture (using exact logic from get token.py)
        logger.info("Waiting for API call to capture token...")
        token = None
        for i in range(30):  # Check for 30 seconds
            time.sleep(1)
            token = driver.execute_script("return window.capturedToken;")

            if token:
                logger.info(f"✅ TOKEN CAPTURED after {i+1} seconds!")
                logger.info(f"Token length: {len(token)} chars")
                logger.info(f"Token preview: {token[:50]}...")
                break

            # Trigger a page interaction to force API calls
            if i == 5:
                logger.info("Refreshing page to trigger API calls...")
                driver.refresh()
                time.sleep(2)
                driver.execute_script(intercept_script)  # Re-inject after refresh
        
        if token:
            logger.info("🎉 Successfully obtained new token")
            return token
        else:
            logger.error("❌ No token captured after 30 seconds")
            logger.info("💡 The page might not have made any API calls.")
            return None
            
    except Exception as e:
        logger.error(f"Error getting new token: {e}")
        return None
    finally:
        if driver:
            driver.quit()

def refresh_token_if_needed():
    """Check token and refresh if needed"""
    global AUTH_KEY, token_status
    
    logger.info("🔍 Checking token status...")
    
    if verify_token():
        logger.info("✅ Token is still valid")
        return True
    
    logger.warning("⚠️ Token expired, attempting refresh...")
    
    if not HAS_SELENIUM:
        logger.error("Cannot refresh - Selenium not available")
        token_status['error'] = "Auto-refresh unavailable (Selenium not installed)"
        return False
    
    new_token = get_new_token_selenium()
    
    if new_token:
        AUTH_KEY = new_token
        token_status['last_refresh'] = datetime.now()
        
        # Verify the new token works
        if verify_token():
            logger.info("✅ Token refreshed successfully")
            
            # Save to environment for persistence
            os.environ['AUTH_KEY'] = new_token
            
            # Save to file as backup
            try:
                with open('auth_token.txt', 'w') as f:
                    f.write(new_token)
                logger.info("💾 Token saved to auth_token.txt")
            except:
                pass
            
            return True
        else:
            logger.error("New token verification failed")
            return False
    else:
        logger.error("Failed to obtain new token")
        return False

def token_monitor_loop():
    """Background thread that monitors and refreshes token"""
    global token_status
    
    logger.info("🔄 Token monitor started")
    
    while monitoring_active:
        try:
            refresh_token_if_needed()
            
            # Wait 3 minutes before next check
            for _ in range(180):  # 180 seconds = 3 minutes
                if not monitoring_active:
                    break
                time.sleep(1)
                
        except Exception as e:
            logger.error(f"Token monitor error: {e}")
            token_status['error'] = str(e)
            time.sleep(10)
    
    logger.info("Token monitor stopped")

def start_token_monitor():
    """Start the token monitoring thread"""
    global monitoring_active, token_monitor_thread
    
    if not AUTO_TOKEN_REFRESH:
        logger.info("Auto token refresh disabled by configuration")
        return
    
    if not HAS_SELENIUM:
        logger.warning("Auto token refresh unavailable - Selenium not installed")
        return
    
    if monitoring_active:
        logger.info("Token monitor already running")
        return
    
    monitoring_active = True
    token_monitor_thread = threading.Thread(target=token_monitor_loop, daemon=True)
    token_monitor_thread.start()
    logger.info("✅ Token monitor started")

def stop_token_monitor():
    """Stop the token monitoring thread"""
    global monitoring_active
    
    monitoring_active = False
    logger.info("Token monitor stop requested")

def render_content(content, **kwargs):
    """Helper function to properly render content in the HTML template"""
    full_template = HTML_TEMPLATE.replace('{% block content %}{% endblock %}', 
                                          '{% block content %}' + content + '{% endblock %}')
    return render_template_string(full_template, **kwargs)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# HTML Template (embedded for single file deployment)
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Metropolis Parking Management</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        :root {
            --primary: #1e88e5;
            --secondary: #00acc1;
            --success: #43a047;
            --danger: #e53935;
            --warning: #fb8c00;
            --dark: #212121;
            --light: #f5f5f5;
            --gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        
        .login-container {
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }
        
        .login-card {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            width: 400px;
            backdrop-filter: blur(10px);
        }
        
        .navbar {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 1rem 0;
        }
        
        .navbar-brand {
            font-weight: bold;
            font-size: 1.5rem;
            color: white!important;
        }
        
        .nav-link {
            color: rgba(255,255,255,0.9)!important;
            margin: 0 10px;
            border-radius: 5px;
            transition: all 0.3s;
        }
        
        .nav-link:hover, .nav-link.active {
            background: rgba(255,255,255,0.2);
            color: white!important;
        }
        
        .main-container {
            background: white;
            min-height: 100vh;
            padding-top: 70px;
        }
        
        .dashboard-card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 25px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.08);
            transition: transform 0.3s, box-shadow 0.3s;
        }
        
        .dashboard-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        }
        
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 15px;
            padding: 30px;
            text-align: center;
            margin-bottom: 25px;
        }
        
        .stat-number {
            font-size: 3rem;
            font-weight: bold;
            margin: 10px 0;
        }
        
        .btn-custom {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 25px;
            font-weight: 600;
            transition: all 0.3s;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .btn-custom:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4);
            color: white;
        }
        
        .gate-btn {
            width: 100%;
            padding: 20px;
            margin: 10px 0;
            border-radius: 10px;
            font-size: 1.2rem;
            font-weight: bold;
            transition: all 0.3s;
        }
        
        .gate-btn.entry {
            background: linear-gradient(135deg, #00c851 0%, #00695c 100%);
            color: white;
            border: none;
        }
        
        .gate-btn.exit {
            background: linear-gradient(135deg, #ff4444 0%, #cc0000 100%);
            color: white;
            border: none;
        }
        
        .gate-btn:hover {
            transform: scale(1.05);
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        
        .table-custom {
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 5px 20px rgba(0,0,0,0.08);
        }
        
        .table-custom thead {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .badge-custom {
            padding: 8px 15px;
            border-radius: 20px;
            font-weight: 600;
        }
        
        .loading-spinner {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(255,255,255,.3);
            border-radius: 50%;
            border-top-color: #fff;
            animation: spin 1s ease-in-out infinite;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        .camera-feed {
            background: #000;
            border-radius: 10px;
            padding: 10px;
            margin: 10px;
            text-align: center;
        }
        
        .camera-feed img {
            max-width: 100%;
            border-radius: 5px;
        }
        
        .alert-custom {
            border-radius: 10px;
            border: none;
            padding: 15px 20px;
        }
        
        .tab-content {
            padding: 30px;
            background: #f8f9fa;
            border-radius: 0 0 15px 15px;
        }
        
        .nav-tabs .nav-link {
            color: #666;
            border: none;
            padding: 15px 25px;
            font-weight: 600;
        }
        
        .nav-tabs .nav-link.active {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 10px 10px 0 0;
        }
        
        .form-control:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
        }
        
        .modal-content {
            border-radius: 15px;
        }
        
        .modal-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 15px 15px 0 0;
        }
        
        @media (max-width: 768px) {
            .dashboard-card {
                margin-bottom: 15px;
            }
            
            .stat-card {
                margin-bottom: 15px;
            }
        }
    </style>
</head>
<body>
    {% if session.get('logged_in') %}
    <!-- Navigation -->
    <nav class="navbar navbar-expand-lg navbar-dark fixed-top">
        <div class="container-fluid">
            <a class="navbar-brand" href="/">
                <i class="fas fa-parking"></i> Metropolis Parking
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="/" id="nav-dashboard">
                            <i class="fas fa-tachometer-alt"></i> Dashboard
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/gates" id="nav-gates">
                            <i class="fas fa-door-open"></i> Gates
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/transactions" id="nav-transactions">
                            <i class="fas fa-receipt"></i> Transactions
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/members" id="nav-members">
                            <i class="fas fa-users"></i> Members
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/visitor" id="nav-visitor">
                            <i class="fas fa-user-plus"></i> Visitor Pass
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/cameras" id="nav-cameras">
                            <i class="fas fa-video"></i> Cameras
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/logout">
                            <i class="fas fa-sign-out-alt"></i> Logout
                        </a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <!-- Main Content -->
    <div class="main-container">
        <div class="container-fluid pt-4">
            {% block content %}{% endblock %}
        </div>
    </div>
    {% else %}
    <!-- Login Page -->
    <div class="login-container">
        <div class="login-card">
            <h2 class="text-center mb-4">
                <i class="fas fa-parking" style="color: #667eea;"></i>
                <br>
                Metropolis Parking
            </h2>
            <form method="POST" action="/login">
                <div class="mb-3">
                    <label class="form-label">Password</label>
                    <input type="password" class="form-control" name="password" required>
                </div>
                <button type="submit" class="btn btn-custom w-100">
                    <i class="fas fa-sign-in-alt"></i> Login
                </button>
            </form>
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    {% for category, message in messages %}
                    <div class="alert alert-{{ 'danger' if category == 'error' else category }} mt-3">
                        {{ message }}
                    </div>
                    {% endfor %}
                {% endif %}
            {% endwith %}
        </div>
    </div>
    {% endif %}

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script>
        // Set active nav item
        $(document).ready(function() {
            const path = window.location.pathname;
            $('.nav-link').removeClass('active');
            if (path === '/') {
                $('#nav-dashboard').addClass('active');
            } else if (path.includes('gates')) {
                $('#nav-gates').addClass('active');
            } else if (path.includes('transactions')) {
                $('#nav-transactions').addClass('active');
            } else if (path.includes('members')) {
                $('#nav-members').addClass('active');
            } else if (path.includes('visitor')) {
                $('#nav-visitor').addClass('active');
            } else if (path.includes('cameras')) {
                $('#nav-cameras').addClass('active');
            }
        });

        // Auto-refresh functions
        function autoRefresh(elementId, url, interval) {
            function refresh() {
                fetch(url)
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById(elementId).innerHTML = data.html || JSON.stringify(data, null, 2);
                    })
                    .catch(error => console.error('Error:', error));
            }
            refresh();
            setInterval(refresh, interval);
        }

        // Gate control
        function openGate(laneId, gateName, siteId) {
            if (!confirm(`Open ${gateName}?`)) return;
            
            fetch('/api/open-gate', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    lane_id: laneId,
                    gate_name: gateName,
                    site_id: siteId
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert(`${gateName} opened successfully!`);
                } else {
                    alert(`Error: ${data.message}`);
                }
            })
            .catch(error => {
                alert(`Error: ${error}`);
            });
        }

        // Member management
        function addMember() {
            const plate = document.getElementById('member-plate').value.trim().toUpperCase();
            if (!plate) return;
            
            fetch('/api/members/add', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({plate: plate})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    location.reload();
                } else {
                    alert(data.message);
                }
            });
        }

        function removeMember(plate) {
            if (!confirm(`Remove ${plate} from members?`)) return;
            
            fetch('/api/members/remove', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({plate: plate})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    location.reload();
                }
            });
        }

        // Blacklist management
        function addBlacklist() {
            const plate = document.getElementById('blacklist-plate').value.trim().toUpperCase();
            const reason = document.getElementById('blacklist-reason').value.trim();
            if (!plate) return;
            
            fetch('/api/blacklist/add', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({plate: plate, reason: reason})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    location.reload();
                } else {
                    alert(data.message);
                }
            });
        }

        function removeBlacklist(plate) {
            if (!confirm(`Remove ${plate} from blacklist?`)) return;
            
            fetch('/api/blacklist/remove', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({plate: plate})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    location.reload();
                }
            });
        }

        // Create visitor pass
        function createVisitorPass() {
            const plate = document.getElementById('visitor-plate').value.trim().toUpperCase();
            const hours = document.getElementById('visitor-hours').value;
            const siteId = document.getElementById('visitor-site').value;
            
            if (!plate || !hours) {
                alert('Please fill all fields');
                return;
            }
            
            fetch('/api/visitor-pass', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    plate: plate,
                    hours: hours,
                    site_id: siteId
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    document.getElementById('visitor-result').innerHTML = `
                        <div class="alert alert-success">
                            <h5>Visitor Pass Created!</h5>
                            <p>Plate: ${data.plate}</p>
                            <p>Valid until: ${data.valid_until}</p>
                            <p>Site: ${data.site}</p>
                        </div>
                    `;
                } else {
                    alert(`Error: ${data.message}`);
                }
            });
        }
    </script>
</body>
</html>
'''

# Routes
@app.route('/')
@login_required
def dashboard():
    # Check token status
    token_info = {
        'valid': token_status.get('valid', False),
        'last_check': token_status.get('last_check', 'Never').strftime('%Y-%m-%d %H:%M:%S') if isinstance(token_status.get('last_check'), datetime) else 'Never',
        'last_refresh': token_status.get('last_refresh', 'Never').strftime('%Y-%m-%d %H:%M:%S') if isinstance(token_status.get('last_refresh'), datetime) else 'Never',
        'error': token_status.get('error', None),
        'auto_refresh': AUTO_TOKEN_REFRESH and HAS_SELENIUM,
        'selenium_available': HAS_SELENIUM
    }
    
    content = '''
    <div class="row">
        <div class="col-12">
            <h1 class="mb-4">Dashboard</h1>
        </div>
    </div>
    
    <!-- Token Status Card -->
    <div class="row mb-4">
        <div class="col-12">
            <div class="dashboard-card" style="border-left: 4px solid {{ '#43a047' if token_info.valid else '#e53935' }};">
                <div class="row align-items-center">
                    <div class="col-md-8">
                        <h4>
                            <i class="fas fa-key"></i> API Token Status
                            {% if token_info.valid %}
                                <span class="badge bg-success ms-2">Valid</span>
                            {% else %}
                                <span class="badge bg-danger ms-2">Invalid/Expired</span>
                            {% endif %}
                        </h4>
                        <p class="mb-1">
                            <strong>Last Check:</strong> {{ token_info.last_check }}<br>
                            <strong>Last Refresh:</strong> {{ token_info.last_refresh }}<br>
                            <strong>Auto-Refresh:</strong> 
                            {% if token_info.auto_refresh %}
                                <span class="text-success">Enabled (every 3 minutes)</span>
                            {% elif not token_info.selenium_available %}
                                <span class="text-warning">Disabled (Selenium not installed)</span>
                            {% else %}
                                <span class="text-muted">Disabled</span>
                            {% endif %}
                        </p>
                        {% if token_info.error %}
                        <div class="alert alert-warning mb-0 mt-2">
                            <i class="fas fa-exclamation-triangle"></i> {{ token_info.error }}
                        </div>
                        {% endif %}
                    </div>
                    <div class="col-md-4 text-end">
                        <button class="btn btn-primary me-2" onclick="testToken()">
                            <i class="fas fa-check-circle"></i> Test Token
                        </button>
                        <button class="btn btn-success" onclick="refreshToken()" {% if not token_info.selenium_available %}disabled title="Selenium not installed"{% endif %}>
                            <i class="fas fa-sync"></i> Get New Token
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <div class="row">
        <!-- Statistics -->
        <div class="col-md-3 col-sm-6">
            <div class="stat-card">
                <i class="fas fa-car fa-3x mb-3"></i>
                <div class="stat-number" id="occupancy-555">--</div>
                <div>555 Capitol Occupancy</div>
            </div>
        </div>
        <div class="col-md-3 col-sm-6">
            <div class="stat-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
                <i class="fas fa-car fa-3x mb-3"></i>
                <div class="stat-number" id="occupancy-boa">--</div>
                <div>Bank of America Occupancy</div>
            </div>
        </div>
        <div class="col-md-3 col-sm-6">
            <div class="stat-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
                <i class="fas fa-clock fa-3x mb-3"></i>
                <div class="stat-number" id="waiting-count">--</div>
                <div>Cars Waiting at Exit</div>
            </div>
        </div>
        <div class="col-md-3 col-sm-6">
            <div class="stat-card" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);">
                <i class="fas fa-users fa-3x mb-3"></i>
                <div class="stat-number">{{ member_count }}</div>
                <div>Active Members</div>
            </div>
        </div>
    </div>
    
    <div class="row mt-4">
        <!-- Recent Transactions -->
        <div class="col-md-6">
            <div class="dashboard-card">
                <h3 class="mb-3">
                    <i class="fas fa-receipt"></i> Recent Transactions
                </h3>
                <div id="recent-transactions" style="max-height: 400px; overflow-y: auto;">
                    <div class="text-center">
                        <div class="loading-spinner"></div>
                        <p>Loading...</p>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Quick Actions -->
        <div class="col-md-6">
            <div class="dashboard-card">
                <h3 class="mb-3">
                    <i class="fas fa-bolt"></i> Quick Actions
                </h3>
                <div class="d-grid gap-2">
                    <a href="/gates" class="btn btn-custom">
                        <i class="fas fa-door-open"></i> Open Gates
                    </a>
                    <a href="/visitor" class="btn btn-custom">
                        <i class="fas fa-user-plus"></i> Create Visitor Pass
                    </a>
                    <a href="/transactions" class="btn btn-custom">
                        <i class="fas fa-search"></i> Search Transactions
                    </a>
                    <a href="/members" class="btn btn-custom">
                        <i class="fas fa-users"></i> Manage Members
                    </a>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Token management functions
        function testToken() {
            fetch('/api/test-token')
                .then(response => response.json())
                .then(data => {
                    if (data.valid) {
                        alert('✅ Token is valid and working!');
                    } else {
                        alert('❌ Token is invalid or expired!\\n' + (data.error || ''));
                    }
                    setTimeout(() => location.reload(), 1000);
                })
                .catch(error => {
                    alert('Error testing token: ' + error);
                });
        }
        
        function refreshToken() {
            if (!confirm('This will get a new token from Metropolis. Continue?')) return;
            
            const btn = event.target;
            btn.disabled = true;
            btn.innerHTML = '<span class="loading-spinner"></span> Getting new token...';
            
            fetch('/api/refresh-token', {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert('✅ Token refreshed successfully!');
                        location.reload();
                    } else {
                        alert('❌ Failed to refresh token:\\n' + (data.error || 'Unknown error'));
                        btn.disabled = false;
                        btn.innerHTML = '<i class="fas fa-sync"></i> Get New Token';
                    }
                })
                .catch(error => {
                    alert('Error refreshing token: ' + error);
                    btn.disabled = false;
                    btn.innerHTML = '<i class="fas fa-sync"></i> Get New Token';
                });
        }

        // Auto-refresh occupancy and transactions after page loads
        $(document).ready(function() {
            autoRefresh('occupancy-555', '/api/occupancy/4005', 5000);
            autoRefresh('occupancy-boa', '/api/occupancy/4007', 5000);
            autoRefresh('waiting-count', '/api/waiting-count', 5000);
            autoRefresh('recent-transactions', '/api/recent-transactions', 3000);
        });
    </script>
    '''
    
    return render_content(content, member_count=len(member_plates), token_info=token_info)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        else:
            return render_template_string(HTML_TEMPLATE, error='Invalid password')
    return render_template_string(HTML_TEMPLATE)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/gates')
@login_required
def gates():
    content = '''
    <div class="row">
        <div class="col-12">
            <h1 class="mb-4">Gate Control</h1>
        </div>
    </div>

    <div class="row">
        <!-- 555 Capitol Mall Gates -->
        <div class="col-md-6">
            <div class="dashboard-card">
                <h3 class="text-center mb-4">555 Capitol Mall</h3>
                <button class="gate-btn exit" onclick="openGate('5568', '6th Street Exit', '4005')">
                    <i class="fas fa-door-open"></i> 6th Street Exit
                </button>
                <button class="gate-btn exit" onclick="openGate('5569', 'L Street Exit', '4005')">
                    <i class="fas fa-door-open"></i> L Street Exit
                </button>
            </div>
        </div>

        <!-- Bank of America Gates -->
        <div class="col-md-6">
            <div class="dashboard-card">
                <h3 class="text-center mb-4">Bank of America</h3>
                <button class="gate-btn exit" onclick="openGate('5565', 'Bank of America Exit', '4007')">
                    <i class="fas fa-door-open"></i> Bank of America Exit
                </button>
            </div>
        </div>
    </div>
    
    <div class="row mt-4">
        <div class="col-12">
            <div class="dashboard-card">
                <h3 class="mb-3">Gate Status</h3>
                <div id="gate-status">
                    <p class="text-muted">Click a gate button to open it</p>
                </div>
            </div>
        </div>
    </div>
    '''
    
    return render_content(content)

@app.route('/transactions')
@login_required
def transactions():
    content = '''
    <div class="row">
        <div class="col-12">
            <h1 class="mb-4">
                <i class="fas fa-receipt"></i> Live Vehicle Activity
            </h1>
        </div>
    </div>

    <div class="dashboard-card mb-3">
        <div class="row">
            <div class="col-md-4">
                <label>Filter by Plate</label>
                <input type="text" class="form-control" id="filter-plate" placeholder="Enter plate number">
            </div>
            <div class="col-md-3">
                <label>Site</label>
                <select class="form-control" id="filter-site">
                    <option value="all">All Sites</option>
                    <option value="4005">555 Capitol Mall</option>
                    <option value="4007">Bank of America</option>
                </select>
            </div>
            <div class="col-md-3">
                <label>Type</label>
                <select class="form-control" id="filter-type">
                    <option value="all">Entry & Exit</option>
                    <option value="entry">Entry Only</option>
                    <option value="exit">Exit Only</option>
                </select>
            </div>
            <div class="col-md-2">
                <label>&nbsp;</label>
                <button class="btn btn-custom w-100" onclick="loadTransactions()">
                    <i class="fas fa-sync"></i> Refresh
                </button>
            </div>
        </div>
    </div>

    <!-- Transaction Cards Container -->
    <div id="transaction-cards" style="max-height: 700px; overflow-y: auto;">
        <div class="text-center">
            <div class="loading-spinner"></div>
            <p>Loading recent activity...</p>
        </div>
    </div>

    <script>
        function loadTransactions() {
            const plate = document.getElementById('filter-plate').value;
            const site = document.getElementById('filter-site').value;
            const type = document.getElementById('filter-type').value;

            document.getElementById('transaction-cards').innerHTML =
                '<div class="text-center"><div class="loading-spinner"></div><p>Loading...</p></div>';

            fetch('/api/recent-activity', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({plate: plate, site: site, type: type})
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('transaction-cards').innerHTML = data.html;
            })
            .catch(error => {
                document.getElementById('transaction-cards').innerHTML =
                    '<div class="alert alert-danger">Error loading activity: ' + error + '</div>';
            });
        }

        // Auto-load on page load
        loadTransactions();

        // Auto-refresh every 10 seconds
        setInterval(loadTransactions, 10000);
    </script>
    '''
    return render_content(content)

@app.route('/members')
@login_required
def members():
    content = '''
    <div class="row">
        <div class="col-12">
            <h1 class="mb-4">Member Management</h1>
        </div>
    </div>
    
    <ul class="nav nav-tabs" role="tablist">
        <li class="nav-item">
            <a class="nav-link active" data-bs-toggle="tab" href="#members-tab">Members</a>
        </li>
        <li class="nav-item">
            <a class="nav-link" data-bs-toggle="tab" href="#blacklist-tab">Blacklist</a>
        </li>
    </ul>
    
    <div class="tab-content">
        <!-- Members Tab -->
        <div id="members-tab" class="tab-pane active">
            <div class="dashboard-card">
                <h3>Add Member</h3>
                <div class="row">
                    <div class="col-md-8">
                        <input type="text" class="form-control" id="member-plate" 
                               placeholder="Enter license plate" style="text-transform: uppercase;">
                    </div>
                    <div class="col-md-4">
                        <button class="btn btn-custom w-100" onclick="addMember()">
                            <i class="fas fa-plus"></i> Add Member
                        </button>
                    </div>
                </div>
            </div>
            
            <div class="dashboard-card mt-4">
                <h3>Current Members ({{ members|length }})</h3>
                <div class="table-responsive">
                    <table class="table table-hover">
                        <thead>
                            <tr>
                                <th>License Plate</th>
                                <th>Added</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for member in members %}
                            <tr>
                                <td><strong>{{ member }}</strong></td>
                                <td>{{ current_time }}</td>
                                <td>
                                    <button class="btn btn-sm btn-danger" 
                                            onclick="removeMember('{{ member }}')">
                                        <i class="fas fa-trash"></i> Remove
                                    </button>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        
        <!-- Blacklist Tab -->
        <div id="blacklist-tab" class="tab-pane">
            <div class="dashboard-card">
                <h3>Add to Blacklist</h3>
                <div class="row">
                    <div class="col-md-4">
                        <input type="text" class="form-control" id="blacklist-plate" 
                               placeholder="License plate" style="text-transform: uppercase;">
                    </div>
                    <div class="col-md-4">
                        <input type="text" class="form-control" id="blacklist-reason" 
                               placeholder="Reason">
                    </div>
                    <div class="col-md-4">
                        <button class="btn btn-danger w-100" onclick="addBlacklist()">
                            <i class="fas fa-ban"></i> Add to Blacklist
                        </button>
                    </div>
                </div>
            </div>
            
            <div class="dashboard-card mt-4">
                <h3>Blacklisted Vehicles ({{ blacklist|length }})</h3>
                <div class="table-responsive">
                    <table class="table table-hover">
                        <thead>
                            <tr>
                                <th>License Plate</th>
                                <th>Reason</th>
                                <th>Added</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for item in blacklist %}
                            <tr>
                                <td><strong>{{ item['plate'] }}</strong></td>
                                <td>{{ item.get('reason', 'N/A') }}</td>
                                <td>{{ current_time }}</td>
                                <td>
                                    <button class="btn btn-sm btn-success" 
                                            onclick="removeBlacklist('{{ item['plate'] }}')">
                                        <i class="fas fa-check"></i> Remove
                                    </button>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
    '''
    return render_content(content, members=member_plates, 
                         blacklist=[{'plate': p} for p in blacklist_plates], 
                         current_time=datetime.now().strftime('%Y-%m-%d %H:%M'))

@app.route('/visitor')
@login_required
def visitor():
    content = '''
    <div class="row">
        <div class="col-12">
            <h1 class="mb-4">Create Visitor Pass</h1>
        </div>
    </div>
    
    <div class="row">
        <div class="col-md-6">
            <div class="dashboard-card">
                <h3>Visitor Information</h3>
                <form onsubmit="createVisitorPass(); return false;">
                    <div class="mb-3">
                        <label>License Plate</label>
                        <input type="text" class="form-control" id="visitor-plate" 
                               placeholder="Enter plate number" required style="text-transform: uppercase;">
                    </div>
                    <div class="mb-3">
                        <label>Valid for (hours)</label>
                        <select class="form-control" id="visitor-hours">
                            <option value="1">1 Hour</option>
                            <option value="2">2 Hours</option>
                            <option value="4" selected>4 Hours</option>
                            <option value="8">8 Hours</option>
                            <option value="24">24 Hours</option>
                        </select>
                    </div>
                    <div class="mb-3">
                        <label>Site</label>
                        <select class="form-control" id="visitor-site">
                            <option value="4005">555 Capitol Mall</option>
                            <option value="4007">Bank of America</option>
                        </select>
                    </div>
                    <button type="submit" class="btn btn-custom w-100">
                        <i class="fas fa-ticket-alt"></i> Create Pass
                    </button>
                </form>
            </div>
        </div>
        
        <div class="col-md-6">
            <div class="dashboard-card">
                <h3>Pass Details</h3>
                <div id="visitor-result">
                    <div class="text-center text-muted">
                        <i class="fas fa-ticket-alt fa-4x mb-3"></i>
                        <p>Fill in the form to create a visitor pass</p>
                    </div>
                </div>
            </div>
        </div>
    </div>
    '''
    return render_content(content)

@app.route('/cameras')
@login_required
def cameras():
    content = '''
    <div class="row">
        <div class="col-12">
            <h1 class="mb-4">
                <i class="fas fa-users"></i> Member Directory
            </h1>
            <p class="text-muted">All members with active subscriptions or recent visits</p>
        </div>
    </div>

    <!-- Member Directory Container -->
    <div id="member-directory-container" style="max-height: 700px; overflow-y: auto;">
        <div class="text-center">
            <div class="loading-spinner"></div>
            <p>Loading member directory...</p>
        </div>
    </div>

    <div class="text-center mt-3">
        <button class="btn btn-custom" onclick="loadMemberDirectory()">
            <i class="fas fa-sync"></i> Refresh Directory
        </button>
    </div>

    <script>
        function loadMemberDirectory() {
            document.getElementById('member-directory-container').innerHTML =
                '<div class="text-center"><div class="loading-spinner"></div><p>Loading...</p></div>';

            fetch('/api/member-directory')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('member-directory-container').innerHTML = data.html;
                })
                .catch(error => {
                    document.getElementById('member-directory-container').innerHTML =
                        '<div class="alert alert-danger">Error loading directory: ' + error + '</div>';
                });
        }

        // Load immediately
        loadMemberDirectory();
    </script>
    '''
    return render_content(content)

# API Routes
@app.route('/api/open-gate', methods=['POST'])
@login_required
def api_open_gate():
    data = request.json
    lane_id = data.get('lane_id')
    gate_name = data.get('gate_name')
    site_id = data.get('site_id', SITE_ID)
    visit_id = data.get('visit_id', None)  # Optional visitId parameter

    # Build endpoint - matches WORKING_GATE_OPENER.py exactly
    endpoint = f"/api/specialist/site/{site_id}/lane/{lane_id}/open-gate"

    # Add visitId parameter if provided
    if visit_id:
        endpoint += f"?visitId={visit_id}"

    url = BASE_URL + endpoint

    # Headers match WORKING_GATE_OPENER.py exactly
    headers = {
        "Authorization": f"Bearer {AUTH_KEY}",
        "Accept": "*/*",
        "Content-Type": "application/json",
        "Origin": "https://specialist.metropolis.io",
        "Referer": "https://specialist.metropolis.io/",
        "User-Agent": "Mozilla/5.0"
    }

    try:
        logger.info(f"Opening gate: POST {endpoint}")
        response = requests.post(url, headers=headers, timeout=10)
        logger.info(f"Status: {response.status_code}")

        # Accept 200, 201, or 204 as success (matches working script)
        if response.status_code in [200, 201, 204]:
            try:
                response_data = response.json()
                logger.info(f"Response: {response_data}")
            except:
                # No JSON response, but success status
                pass
            return jsonify({'success': True, 'message': f'{gate_name} opened successfully'})
        else:
            logger.error(f"Error response: {response.text}")
            return jsonify({'success': False, 'message': f'Failed with status {response.status_code}'})
    except Exception as e:
        logger.error(f"Error opening gate: {e}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/occupancy/<site_id>')
@login_required
def api_occupancy(site_id):
    url = f"{BASE_URL}/api/site/{site_id}/occupancy"
    headers = {"Authorization": f"Bearer {AUTH_KEY}", "Accept": "*/*"}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            occupancy = data.get('currentOccupancy', 0)
            return jsonify({'html': str(occupancy)})
    except:
        pass
    return jsonify({'html': '--'})

@app.route('/api/waiting-count')
@login_required
def api_waiting_count():
    total = 0
    for site_id in ["4005", "4007"]:
        url = f"{BASE_URL}/api/specialist/site/{site_id}/event/hanging-exit/count"
        headers = {"Authorization": f"Bearer {AUTH_KEY}", "Accept": "*/*"}
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                total += data.get('count', 0)
        except:
            pass
    return jsonify({'html': str(total)})

@app.route('/api/recent-transactions')
@login_required  
def api_recent_transactions():
    html = '<div class="table-responsive"><table class="table table-sm">'
    html += '<thead><tr><th>Time</th><th>Plate</th><th>Site</th></tr></thead><tbody>'
    
    for site_id in ["4005", "4007"]:
        site_name = "555" if site_id == "4005" else "BoA"
        url = f"{BASE_URL}/api/specialist/site/{site_id}/visits/closed?count=5"
        headers = {"Authorization": f"Bearer {AUTH_KEY}", "Accept": "*/*"}
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    transactions = data.get('data', {}).get('transactions', [])
                    for t in transactions[:5]:
                        vehicle = t.get('vehicle', {})
                        plate = vehicle.get('licensePlate', {}).get('text', 'Unknown') if vehicle else 'Unknown'
                        entry_time = t.get('entryTimestamp', '')
                        if entry_time:
                            entry_time = entry_time.split('T')[1][:5]
                        html += f'<tr><td>{entry_time}</td><td><strong>{plate}</strong></td><td>{site_name}</td></tr>'
        except:
            pass
    
    html += '</tbody></table></div>'
    return jsonify({'html': html})

@app.route('/api/members/add', methods=['POST'])
@login_required
def api_add_member():
    plate = request.json.get('plate', '').upper()
    if plate and plate not in member_plates:
        member_plates.append(plate)
        save_members()  # Save to file
        logger.info(f"Added member: {plate}")
        return jsonify({'success': True, 'message': f'Added {plate} to members'})
    return jsonify({'success': False, 'message': 'Plate already exists or invalid'})

@app.route('/api/members/remove', methods=['POST'])
@login_required
def api_remove_member():
    plate = request.json.get('plate', '').upper()
    if plate in member_plates:
        member_plates.remove(plate)
        save_members()  # Save to file
        logger.info(f"Removed member: {plate}")
        return jsonify({'success': True, 'message': f'Removed {plate}'})
    return jsonify({'success': False, 'message': 'Plate not found'})

@app.route('/api/blacklist/add', methods=['POST'])
@login_required
def api_add_blacklist():
    plate = request.json.get('plate', '').upper()
    if plate and plate not in blacklist_plates:
        blacklist_plates.append(plate)
        save_blacklist()  # Save to file
        logger.warning(f"Blacklisted plate: {plate}")
        return jsonify({'success': True, 'message': f'Blacklisted {plate}'})
    return jsonify({'success': False, 'message': 'Plate already blacklisted or invalid'})

@app.route('/api/blacklist/remove', methods=['POST'])
@login_required
def api_remove_blacklist():
    plate = request.json.get('plate', '').upper()
    if plate in blacklist_plates:
        blacklist_plates.remove(plate)
        save_blacklist()  # Save to file
        logger.info(f"Removed from blacklist: {plate}")
        return jsonify({'success': True, 'message': f'Removed {plate} from blacklist'})
    return jsonify({'success': False, 'message': 'Plate not found'})

@app.route('/api/visitor-pass', methods=['POST'])
@login_required
def api_visitor_pass():
    data = request.json
    plate = data.get('plate', '').upper()
    hours = int(data.get('hours', 4))
    site_id = data.get('site_id', '4005')
    
    valid_until = datetime.now() + timedelta(hours=hours)
    site_name = "555 Capitol Mall" if site_id == "4005" else "Bank of America"
    
    # In a real app, you would save this to a database
    return jsonify({
        'success': True,
        'plate': plate,
        'valid_until': valid_until.strftime('%Y-%m-%d %H:%M'),
        'site': site_name
    })

@app.route('/api/camera-feeds-live')
@login_required
def api_camera_feeds_live():
    """Get live camera feeds with actual vehicle images - matches WORKING_GATE_OPENER.py"""
    html = ''

    for site_id in ['4005', '4007']:
        site_name = "555 Capitol Mall" if site_id == "4005" else "Bank of America"

        url = f"{BASE_URL}/api/specialist/site/{site_id}/visits/closed?count=10"
        headers = {"Authorization": f"Bearer {AUTH_KEY}", "Accept": "*/*"}

        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                api_data = response.json()
                if api_data.get('success'):
                    transactions = api_data.get('data', {}).get('transactions', [])

                    for t in transactions[:10]:  # Show latest 10
                        vehicle = t.get('vehicle', {})
                        plate_obj = vehicle.get('licensePlate', {})
                        plate = plate_obj.get('text', 'N/A')
                        state = plate_obj.get('state', {}).get('name', 'CA')

                        images = t.get('images', {})

                        # Show EXIT events (most recent activity)
                        exit_event = images.get('exitEvent')
                        if exit_event:
                            html += create_vehicle_card_html(t, exit_event, plate, state, is_entry=False)

                        # Also show ENTRY events
                        entry_event = images.get('entryEvent')
                        if entry_event:
                            html += create_vehicle_card_html(t, entry_event, plate, state, is_entry=True)

        except Exception as e:
            logger.error(f"Error fetching camera feeds: {e}")

    if not html:
        html = '<div class="alert alert-info text-center">No recent camera activity</div>'

    return jsonify({'html': html})

@app.route('/api/recent-activity', methods=['POST'])
@login_required
def api_recent_activity():
    """Get recent vehicle activity with images - matches WORKING_GATE_OPENER.py layout"""
    data = request.json
    filter_plate = data.get('plate', '').upper()
    filter_site = data.get('site', 'all')
    filter_type = data.get('type', 'all')

    html = ''
    sites = ['4005', '4007'] if filter_site == 'all' else [filter_site]

    for site_id in sites:
        site_name = "555 Capitol Mall" if site_id == "4005" else "Bank of America"

        # Header for site
        html += f'''
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white; padding: 10px 20px; margin: 20px 0 10px 0;
                    border-radius: 10px; font-weight: bold; font-size: 1.1rem;">
            {site_name}
        </div>
        '''

        url = f"{BASE_URL}/api/specialist/site/{site_id}/visits/closed?count=20"
        headers = {"Authorization": f"Bearer {AUTH_KEY}", "Accept": "*/*"}

        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                api_data = response.json()
                if api_data.get('success'):
                    transactions = api_data.get('data', {}).get('transactions', [])

                    for t in transactions:
                        vehicle = t.get('vehicle', {})
                        plate_obj = vehicle.get('licensePlate', {})
                        plate = plate_obj.get('text', 'N/A')
                        state = plate_obj.get('state', {}).get('name', 'CA')

                        # Filter by plate if specified
                        if filter_plate and filter_plate not in plate.upper():
                            continue

                        images = t.get('images', {})

                        # Process ENTRY event
                        if filter_type in ['all', 'entry']:
                            entry_event = images.get('entryEvent')
                            if entry_event:
                                html += create_vehicle_card_html(t, entry_event, plate, state, is_entry=True)

                        # Process EXIT event
                        if filter_type in ['all', 'exit']:
                            exit_event = images.get('exitEvent')
                            if exit_event:
                                html += create_vehicle_card_html(t, exit_event, plate, state, is_entry=False)

        except Exception as e:
            logger.error(f"Error fetching activity: {e}")

    if not html:
        html = '<div class="alert alert-info text-center">No recent activity found</div>'

    return jsonify({'html': html})

def create_vehicle_card_html(transaction, event, plate, state, is_entry=True):
    """Create HTML for a vehicle card matching WORKING_GATE_OPENER.py style"""

    # Get timestamp
    timestamp_ms = transaction.get('start') if is_entry else transaction.get('end')
    if timestamp_ms:
        dt = datetime.fromtimestamp(timestamp_ms / 1000)
        time_str = dt.strftime('%I:%M %p')
        date_str = dt.strftime('%m/%d/%Y')
    else:
        time_str = 'N/A'
        date_str = ''

    # Get lane info
    equipment = event.get('siteEquipment') if event else None
    lane_name = equipment.get('notes', 'Unknown Lane') if equipment else 'Unknown Lane'

    # Get image URL
    context_url = event.get('contextImageUrl', '') if event else ''

    # Entry/Exit styling
    direction_color = '#4CAF50' if is_entry else '#F44336'
    direction_text = '→ ENTRY' if is_entry else '← EXIT'
    direction_icon = 'fa-arrow-right' if is_entry else 'fa-arrow-left'

    card_html = f'''
    <div style="background: #2a2a2a; border-radius: 10px; padding: 15px; margin-bottom: 15px;
                display: flex; align-items: center; box-shadow: 0 5px 15px rgba(0,0,0,0.3);">

        <!-- Left: Image -->
        <div style="flex-shrink: 0; margin-right: 20px;">
            {f'<img src="{context_url}" style="width: 150px; height: 100px; object-fit: cover; border-radius: 5px; background: #000;" />'
             if context_url else
             '<div style="width: 150px; height: 100px; background: #000; border-radius: 5px; display: flex; align-items: center; justify-content: center; color: #666;"><i class="fas fa-camera" style="font-size: 2rem;"></i></div>'}
        </div>

        <!-- Middle: Info -->
        <div style="flex-grow: 1;">
            <!-- License Plate Badge -->
            <div style="display: inline-block; background: #1E88E5; padding: 5px 15px; border-radius: 5px; margin-bottom: 8px;">
                <span style="color: white; font-weight: bold; font-size: 1.2rem; margin-right: 10px;">{plate}</span>
                <span style="background: white; color: black; padding: 2px 8px; border-radius: 3px; font-size: 0.9rem; font-weight: bold;">{state}</span>
            </div>

            <!-- Entry/Exit Indicator -->
            <div style="color: {direction_color}; font-weight: bold; margin-bottom: 3px;">
                <i class="fas {direction_icon}"></i> {direction_text}
            </div>

            <!-- Lane Name -->
            <div style="color: #aaa; font-size: 0.9rem;">{lane_name}</div>
        </div>

        <!-- Right: Time -->
        <div style="text-align: right; min-width: 120px;">
            <div style="font-size: 1.3rem; font-weight: bold; color: white;">{time_str}</div>
            <div style="font-size: 0.8rem; color: #888;">{date_str}</div>
        </div>
    </div>
    '''

    return card_html

@app.route('/api/search-transactions', methods=['POST'])
@login_required
def api_search_transactions():
    data = request.json
    plate = data.get('plate', '').upper()
    site = data.get('site', 'all')
    
    html = '<div class="table-responsive"><table class="table">'
    html += '<thead><tr><th>Time</th><th>Plate</th><th>Duration</th><th>Site</th><th>Amount</th></tr></thead><tbody>'
    
    sites = ['4005', '4007'] if site == 'all' else [site]
    
    for site_id in sites:
        site_name = "555 Capitol" if site_id == "4005" else "Bank of America"
        url = f"{BASE_URL}/api/specialist/site/{site_id}/visits/closed?count=50"
        headers = {"Authorization": f"Bearer {AUTH_KEY}", "Accept": "*/*"}
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    transactions = data.get('data', {}).get('transactions', [])
                    for t in transactions:
                        vehicle = t.get('vehicle', {})
                        t_plate = vehicle.get('licensePlate', {}).get('text', '') if vehicle else ''
                        
                        if plate and plate not in t_plate.upper():
                            continue
                        
                        entry_time = t.get('entryTimestamp', '')
                        exit_time = t.get('exitTimestamp', '')
                        amount = t.get('paymentDue', 0)
                        
                        if entry_time:
                            entry_time = entry_time.replace('T', ' ')[:16]
                        
                        duration = 'N/A'
                        if entry_time and exit_time:
                            try:
                                entry_dt = datetime.fromisoformat(t.get('entryTimestamp', '').replace('Z', '+00:00'))
                                exit_dt = datetime.fromisoformat(t.get('exitTimestamp', '').replace('Z', '+00:00'))
                                duration_td = exit_dt - entry_dt
                                hours = duration_td.seconds // 3600
                                minutes = (duration_td.seconds % 3600) // 60
                                duration = f'{hours}h {minutes}m'
                            except:
                                pass
                        
                        html += f'''
                        <tr>
                            <td>{entry_time}</td>
                            <td><strong>{t_plate}</strong></td>
                            <td>{duration}</td>
                            <td>{site_name}</td>
                            <td>${amount:.2f}</td>
                        </tr>
                        '''
        except Exception as e:
            print(f"Error searching transactions: {e}")
    
    html += '</tbody></table></div>'
    return jsonify({'html': html})

@app.route('/api/test-token')
@login_required
def api_test_token():
    """Test if the current token is valid"""
    is_valid = verify_token()
    return jsonify({
        'valid': is_valid,
        'error': token_status.get('error'),
        'last_check': token_status.get('last_check').isoformat() if isinstance(token_status.get('last_check'), datetime) else None
    })

@app.route('/api/refresh-token', methods=['POST'])
@login_required
def api_refresh_token():
    """Manually trigger token refresh"""
    if not HAS_SELENIUM:
        return jsonify({
            'success': False,
            'error': 'Selenium not installed. Please install selenium to enable token refresh.'
        })
    
    try:
        success = refresh_token_if_needed()
        return jsonify({
            'success': success,
            'error': token_status.get('error') if not success else None
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/token-status')
@login_required
def api_token_status():
    """Get current token status"""
    return jsonify({
        'valid': token_status.get('valid', False),
        'last_check': token_status.get('last_check').isoformat() if isinstance(token_status.get('last_check'), datetime) else None,
        'last_refresh': token_status.get('last_refresh').isoformat() if isinstance(token_status.get('last_refresh'), datetime) else None,
        'error': token_status.get('error'),
        'auto_refresh_enabled': AUTO_TOKEN_REFRESH and HAS_SELENIUM,
        'selenium_available': HAS_SELENIUM
    })

if __name__ == '__main__':
    logger.info("="*60)
    logger.info("METROPOLIS PARKING MANAGEMENT SYSTEM - WEB APP")
    logger.info("="*60)

    # Load members and blacklist from files
    logger.info("Loading member and blacklist data...")
    load_members()
    load_blacklist()
    logger.info(f"Loaded {len(member_plates)} members and {len(blacklist_plates)} blacklisted plates")

    # Try to load token from file if it exists
    try:
        with open('auth_token.txt', 'r') as f:
            saved_token = f.read().strip()
            if saved_token and len(saved_token) > 100:  # Basic validation
                AUTH_KEY = saved_token
                logger.info(f"✅ Loaded token from auth_token.txt (length: {len(saved_token)})")
            else:
                logger.warning("Token in auth_token.txt appears invalid")
    except FileNotFoundError:
        logger.info("No auth_token.txt found, using environment token")
    except Exception as e:
        logger.warning(f"Could not load token from file: {e}")

    # Start token monitor if enabled
    if AUTO_TOKEN_REFRESH:
        logger.info("Starting automatic token monitoring...")
        start_token_monitor()

    # Verify initial token
    logger.info("Verifying initial token...")
    verify_token()

    # Start Flask app
    port = int(os.environ.get('PORT', 10000))
    logger.info(f"Starting Flask app on port {port}...")
    logger.info("="*60)
    app.run(host='0.0.0.0', port=port, debug=False)
