#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Token Grabber - Intercepts fetch() to capture Authorization header
"""
import sys
import io

# Fix encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import re

EMAIL = "security@555capitolmall.com"
PASSWORD = "555_Security"
URL = "https://specialist.metropolis.io/site/4005"

print("🚀 Starting token grabber in headless mode...")

# Configure Edge to run headlessly
from selenium.webdriver.edge.options import Options as EdgeOptions
options = EdgeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920,1080')
options.add_experimental_option('excludeSwitches', ['enable-logging'])

driver = webdriver.Edge(options=options)
driver.get(URL)

print("⏳ Waiting for page load...")
time.sleep(3)

# Auto-login
try:
    print("📧 Logging in...")
    email_field = driver.find_element(By.ID, "username")
    email_field.send_keys(EMAIL)
    time.sleep(1)

    password_field = driver.find_element(By.ID, "password")
    password_field.send_keys(PASSWORD)
    password_field.send_keys(Keys.RETURN)

    print("🔐 Logging in...")
    time.sleep(5)

except Exception as e:
    print(f"⚠️ Login error: {e}")

# Inject JavaScript to intercept fetch requests
print("\n💉 Injecting fetch interceptor...")

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

print("✅ Interceptor installed!")
print("⏳ Waiting for API call to capture token...")

# Wait and check for captured token
for i in range(30):  # Check for 30 seconds
    time.sleep(1)

    token = driver.execute_script("return window.capturedToken;")

    if token:
        print(f"\n✅ TOKEN CAPTURED! (after {i+1} seconds)")
        break

    # Trigger a page interaction to force API calls
    if i == 5:
        print("   Refreshing page to trigger API calls...")
        driver.refresh()
        time.sleep(2)
        driver.execute_script(intercept_script)  # Re-inject after refresh

    print(f"   Still waiting... ({i+1}s)", end='\r')

driver.quit()

print("\n" + "="*60)

if token:
    print("🎉 SUCCESS!")
    print(f"\nToken: {token[:50]}...")

    # Save to file
    with open('auth_token.txt', 'w') as f:
        f.write(token)
    print("\n💾 Saved to auth_token.txt")

    # Update main script
    script_path = r"C:\Users\khjb\Desktop\gpt data\workuselessstuff\WORKING_GATE_OPENER.py"

    try:
        with open(script_path, 'r', encoding='utf-8') as f:
            content = f.read()

        pattern = r'AUTH_KEY = "eyJ[^"]*"'
        updated = re.sub(pattern, f'AUTH_KEY = "{token}"', content)

        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(updated)

        print(f"✅ Updated {script_path}!")
        print("\n🚀 You can now run the main gate opener script!")

    except Exception as e:
        print(f"⚠️ Could not update script: {e}")
        print(f"\nCopy this token manually:\n{token}\n")

else:
    print("❌ No token captured after 30 seconds")
    print("\n💡 The page might not have made any API calls.")
    print("Try running the script again - it will refresh the page to trigger calls.")
