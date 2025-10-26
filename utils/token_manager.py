"""
Token Management Functions
JWT decoding, expiration checking, and headless token refresh
"""

import base64
import json
import time
import os
from datetime import datetime

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.chrome.options import Options
    HAS_SELENIUM = True
except:
    HAS_SELENIUM = False
    print("Warning: Selenium not available. Token auto-refresh disabled.")

def decode_jwt_payload(token):
    """Decode JWT token payload to check expiration"""
    try:
        parts = token.split('.')
        if len(parts) != 3:
            return None

        payload = parts[1]
        padding = 4 - len(payload) % 4
        if padding != 4:
            payload += '=' * padding

        decoded = base64.urlsafe_b64decode(payload)
        return json.loads(decoded)
    except Exception as e:
        print(f"JWT decode error: {e}")
        return None

def is_token_expired(token):
    """Check if JWT token is expired"""
    payload = decode_jwt_payload(token)
    if not payload:
        return True

    exp = payload.get('exp')
    if not exp:
        return True

    # Check if expired (with 5 minute buffer)
    current_time = time.time()
    return current_time >= (exp - 300)

def get_token_expiration_time(token):
    """Get token expiration time as datetime"""
    payload = decode_jwt_payload(token)
    if not payload:
        return None

    exp = payload.get('exp')
    if not exp:
        return None

    return datetime.fromtimestamp(exp)

def refresh_token_headless(email, password):
    """Get fresh token automatically using headless browser"""

    if not HAS_SELENIUM:
        print("ERROR: Selenium not available. Cannot refresh token.")
        return None

    LOGIN_URL = "https://specialist.metropolis.io/site/4005"

    print("\n" + "="*60)
    print("REFRESHING TOKEN (Headless Mode)")
    print("="*60)

    try:
        # Setup headless browser (use Chrome for Render compatibility)
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--log-level=3')

        # Use Chrome instead of Edge for Linux compatibility
        driver = webdriver.Chrome(options=options)
        driver.get(LOGIN_URL)

        print("Navigating to login page...")
        time.sleep(3)

        # Auto-login
        try:
            print("Logging in...")
            email_field = driver.find_element(By.ID, "username")
            email_field.send_keys(email)
            time.sleep(1)

            password_field = driver.find_element(By.ID, "password")
            password_field.send_keys(password)
            password_field.send_keys(Keys.RETURN)

            print("Waiting for authentication...")
            time.sleep(5)

        except Exception as e:
            print(f"Login error: {e}")
            driver.quit()
            return None

        # Inject JavaScript to intercept fetch requests
        print("Injecting token interceptor...")

        intercept_script = """
        window.capturedToken = null;

        const originalFetch = window.fetch;
        window.fetch = function(...args) {
            const [url, config] = args;

            if (config && config.headers) {
                const auth = config.headers['Authorization'] || config.headers['authorization'];
                if (auth && auth.startsWith('Bearer ')) {
                    window.capturedToken = auth.replace('Bearer ', '');
                    console.log('Captured token from fetch!');
                }
            }

            return originalFetch.apply(this, args);
        };

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
                console.log('Captured token from XHR!');
            }

            return originalSetHeader.apply(this, arguments);
        };

        console.log('Token interceptor installed!');
        """

        driver.execute_script(intercept_script)
        print("Interceptor installed!")

        # Wait for token capture
        print("Waiting for API call to capture token...")
        token = None

        for i in range(30):
            time.sleep(1)
            token = driver.execute_script("return window.capturedToken;")

            if token:
                print(f"\nTOKEN CAPTURED! (after {i+1} seconds)")
                break

            if i == 5:
                print("   Refreshing page to trigger API calls...")
                driver.refresh()
                time.sleep(2)
                driver.execute_script(intercept_script)

            print(f"   Waiting... ({i+1}s)", end='\r')

        driver.quit()

        if token:
            print(f"\nSUCCESS! Token refreshed!")
            print(f"Token preview: {token[:50]}...")

            # Update environment variable
            os.environ['AUTH_KEY'] = token

            print("="*60)
            return token
        else:
            print("\nNo token captured after 30 seconds")
            print("="*60)
            return None

    except Exception as e:
        print(f"Token refresh error: {e}")
        import traceback
        traceback.print_exc()
        try:
            driver.quit()
        except:
            pass
        return None
