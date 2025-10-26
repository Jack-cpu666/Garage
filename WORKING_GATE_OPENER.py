

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import requests
import json
import threading
import time
import os
import base64
import re
from datetime import datetime
from io import BytesIO
try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except:
    HAS_PIL = False
    print("Warning: PIL not available. Image display will be limited.")

# Desktop notifications
try:
    from plyer import notification
    HAS_NOTIFICATIONS = True
except:
    HAS_NOTIFICATIONS = False
    print("Warning: plyer not available. Desktop notifications disabled.")

# Selenium for token refresh
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.edge.options import Options
    HAS_SELENIUM = True
except:
    HAS_SELENIUM = False
    print("Warning: Selenium not available. Auto token refresh disabled.")

# YOUR AUTH KEY (JWT Bearer Token)
AUTH_KEY = "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJpbXpVMnE4NXQxSDB5U2RpUHRKNmtmeWpkYXZlR2ZiaHdyZ01KbXNHZTQ4In0.eyJleHAiOjE3NjE1MTc1MTgsImlhdCI6MTc2MTUxMzkxOCwiYXV0aF90aW1lIjoxNzYxNTEzOTE3LCJqdGkiOiIzODVmNjE4MS00ZmI0LTRmOWMtYmQwZC1jOWUyNmVhNzQxOGEiLCJpc3MiOiJodHRwczovL2F1dGgubWV0cm9wb2xpcy5pby9yZWFsbXMvbWV0cm9wb2xpcyIsImF1ZCI6WyJtZXRyb3BvbGlzLXJlc291cmNlLWNsaWVudCIsIm1ldHJvcG9saXMtdXNlci1jbGllbnQiLCJtZXRyb3BvbGlzLXNlcnZlci1jbGllbnQiLCJhY2NvdW50Il0sInN1YiI6ImU2MzEzOWI2LWUyNzgtNGUwNS05ZDJmLTMzZWUxOGQwZGI4YyIsInR5cCI6IkJlYXJlciIsImF6cCI6Im1ldHJvcG9saXMtd2ViLWNsaWVudCIsIm5vbmNlIjoiMjhmM2M1MWUtZTg5ZS00MDdjLTg4ZTMtOTcwZWNmNzM5MzEzIiwic2Vzc2lvbl9zdGF0ZSI6IjM2MTg5MTBlLTQxMjQtNDNlYS1hYTRhLWI2ZmFkNzM0ZTMwNyIsImFjciI6IjEiLCJhbGxvd2VkLW9yaWdpbnMiOlsiaHR0cHM6Ly9tYW5hZ2VyLm1ldHJvcG9saXMuaW8iLCJodHRwczovL3BvcnRhbC5tZXRyb3BvbGlzLmlvIiwiaHR0cHM6Ly9yZXF1ZXN0Lm1ldHJvcG9saXMuaW8iLCJodHRwczovL2ludGFrZS5tZXRyb3BvbGlzLmlvIiwiaHR0cHM6Ly9kZXZvcHMudG9vbHMubWV0cm9wLmlvIiwiaHR0cHM6Ly9oYXJkd2FyZS5lZGdlLm1ldHJvcG9saXMuaW8iLCJodHRwczovL3NwZWNpYWxpc3QubWV0cm9wb2xpcy5pbyIsImh0dHA6Ly9sb2NhbGhvc3Q6MzAwMSIsImh0dHA6Ly9sb2NhbGhvc3Q6MzAwMCIsImh0dHBzOi8vZWRnZS5hdGcubWV0cm9wb2xpcy5pbyJdLCJyZWFsbV9hY2Nlc3MiOnsicm9sZXMiOlsiZGVmYXVsdC1yb2xlcy10ZXN0Iiwib2ZmbGluZV9hY2Nlc3MiLCJ1bWFfYXV0aG9yaXphdGlvbiJdfSwicmVzb3VyY2VfYWNjZXNzIjp7Im1ldHJvcG9saXMtc2VydmVyLWNsaWVudCI6eyJyb2xlcyI6WyJlbmZvcmNlbWVudCIsInBhcmtpbmcgcGFzcyIsInZhbGV0IiwiaW50YWtlIiwib3BlcmF0b3IiXX19LCJzY29wZSI6Im9wZW5pZCBwcm9maWxlIGVtYWlsIiwic2lkIjoiMzYxODkxMGUtNDEyNC00M2VhLWFhNGEtYjZmYWQ3MzRlMzA3IiwiZW1haWxfdmVyaWZpZWQiOnRydWUsIm5hbWUiOiI1NTUgU2VjdXJpdHkgIiwicHJlZmVycmVkX3VzZXJuYW1lIjoic2VjdXJpdHlANTU1Y2FwaXRvbG1hbGwuY29tIiwiZ2l2ZW5fbmFtZSI6IjU1NSIsImZhbWlseV9uYW1lIjoiU2VjdXJpdHkgIiwiZW1haWwiOiJzZWN1cml0eUA1NTVjYXBpdG9sbWFsbC5jb20ifQ.tb4ViCB42dJrFqs3lzowgG7jMdTAl_60jnG2AblsDou46Tn10IbJ-c2The3Ja2u4dcbQVqEjktGEXAExHZ44ehZD_AIo4dGx_hIEdbEz8nPoKVi-dYjO9U_HY7oZJZ0H2kXGwPUeiMhwaw7xlie1ifvwXiNZfkrCJ-gRxZ_06c6BKPUgyb-qsJ0UTeCcRu3OretpIXuD9iAabtrMTMIkJdVpAOzF0EFz9A5rempJqPbuYG-aTSjxegsoZSVkDzOq6hdMxCqgNOePyB_FK1GRXNyTtTbJVsiZXux1UeceUkrZWOWSedDepUK3T65eG23U1cKONgtfy5sLbv7J2GAawA"
BASE_URL = "https://specialist.api.metropolis.io"
SITE_ID = "4005"

# Login credentials for auto token refresh
EMAIL = "security@555capitolmall.com"
PASSWORD = "555_Security"
LOGIN_URL = "https://specialist.metropolis.io/site/4005"

# Membership storage
MEMBERS_FILE = "memberships.json"
BLACKLIST_FILE = "blacklist.json"
member_plates = []
blacklist_plates = []
monitoring_active = False
monitoring_thread = None
notifications_enabled = True

# Token verification
token_monitor_active = False
token_monitor_thread = None
token_status_callback = None

def get_gates():
    """Fetch available gates"""
    url = f"{BASE_URL}/api/sites/{SITE_ID}/gates"

    headers = {
        "Authorization": f"Bearer {AUTH_KEY}",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0",
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Get gates: Status {response.status_code}")

        if response.status_code == 200:
            try:
                data = response.json()
                print(f"Gates data: {json.dumps(data, indent=2)}")
                return data
            except:
                print(f"Response is HTML, not JSON")
                print(f"Response: {response.text[:500]}")

    except Exception as e:
        print(f"Error fetching gates: {e}")

    return None

def get_hanging_exits(site_id):
    """Get count of cars waiting at exit"""
    url = f"{BASE_URL}/api/specialist/site/{site_id}/event/hanging-exit/count"
    headers = {
        "Authorization": f"Bearer {AUTH_KEY}",
        "Accept": "*/*",
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Error fetching hanging exits: {e}")
    return None

def get_closed_visits(site_id, count=25):
    """Get recent closed visits"""
    url = f"{BASE_URL}/api/specialist/site/{site_id}/visits/closed?count={count}&minPaymentDueAgeSeconds=180&zoneIds={site_id}"
    headers = {
        "Authorization": f"Bearer {AUTH_KEY}",
        "Accept": "*/*",
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Error fetching closed visits: {e}")
    return None

def get_occupancy(site_id):
    """Get current garage occupancy"""
    url = f"{BASE_URL}/api/site/{site_id}/occupancy"
    headers = {
        "Authorization": f"Bearer {AUTH_KEY}",
        "Accept": "*/*",
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Error fetching occupancy: {e}")
    return None

def open_gate(lane_id, gate_name, status_label, site_id=None, visit_id=None):
    """Open a specific gate/lane"""

    # Use the site_id provided, or fall back to default SITE_ID
    site = site_id if site_id else SITE_ID

    # Use the correct endpoint format: /api/specialist/site/{site_id}/lane/{lane_id}/open-gate
    endpoint = f"/api/specialist/site/{site}/lane/{lane_id}/open-gate"

    # Add visitId parameter if provided (optional)
    if visit_id:
        endpoint += f"?visitId={visit_id}"

    url = BASE_URL + endpoint

    headers = {
        "Authorization": f"Bearer {AUTH_KEY}",
        "Accept": "*/*",
        "Content-Type": "application/json",
        "Origin": "https://specialist.metropolis.io",
        "Referer": "https://specialist.metropolis.io/",
        "User-Agent": "Mozilla/5.0",
    }

    try:
        print(f"\nOpening gate: POST {endpoint}")

        response = requests.post(
            url,
            headers=headers,
            timeout=10
        )

        print(f"Status: {response.status_code}")

        if response.status_code in [200, 201, 204]:
            try:
                data = response.json()
                print(f"Response: {data}")

                status_label.config(text=f"Gate {gate_name} opened!", fg='#4CAF50')
                messagebox.showinfo("Success", f"{gate_name} opened!")
                return True

            except:
                # No JSON response, but 200 status = success
                status_label.config(text=f"Gate {gate_name} opened!", fg='#4CAF50')
                messagebox.showinfo("Success", f"{gate_name} opened!")
                return True
        else:
            print(f"Error response: {response.text}")
            status_label.config(text=f"Failed to open {gate_name}", fg='#F44336')
            messagebox.showerror("Error", f"Could not open {gate_name}\nStatus: {response.status_code}")
            return False

    except Exception as e:
        print(f"Error: {e}")
        status_label.config(text=f"Failed to open {gate_name}", fg='#F44336')
        messagebox.showerror("Error", f"Could not open {gate_name}\n{str(e)}")
        return False

def load_members():
    """Load member plates from JSON file"""
    global member_plates
    if os.path.exists(MEMBERS_FILE):
        try:
            with open(MEMBERS_FILE, 'r') as f:
                member_plates = json.load(f)
            print(f"Loaded {len(member_plates)} member plates")
        except Exception as e:
            print(f"Error loading members: {e}")
            member_plates = []
    else:
        member_plates = []

def save_members():
    """Save member plates to JSON file"""
    try:
        with open(MEMBERS_FILE, 'w') as f:
            json.dump(member_plates, f, indent=2)
        print(f"Saved {len(member_plates)} member plates")
    except Exception as e:
        print(f"Error saving members: {e}")

def load_blacklist():
    """Load blacklisted plates from JSON file"""
    global blacklist_plates
    if os.path.exists(BLACKLIST_FILE):
        try:
            with open(BLACKLIST_FILE, 'r') as f:
                blacklist_plates = json.load(f)
            print(f"Loaded {len(blacklist_plates)} blacklisted plates")
        except Exception as e:
            print(f"Error loading blacklist: {e}")
            blacklist_plates = []
    else:
        blacklist_plates = []

def save_blacklist():
    """Save blacklisted plates to JSON file"""
    try:
        with open(BLACKLIST_FILE, 'w') as f:
            json.dump(blacklist_plates, f, indent=2)
        print(f"Saved {len(blacklist_plates)} blacklisted plates")
    except Exception as e:
        print(f"Error saving blacklist: {e}")

def send_notification(title, message):
    """Send desktop notification"""
    global notifications_enabled
    if not notifications_enabled:
        return

    if HAS_NOTIFICATIONS:
        try:
            notification.notify(
                title=title,
                message=message,
                app_name="Metropolis Parking",
                timeout=5
            )
        except Exception as e:
            print(f"Notification error: {e}")
    else:
        # Fallback: just print
        print(f"[NOTIFICATION] {title}: {message}")

def get_all_members(site_id):
    """Get all members/users with active visits or subscriptions"""
    # Get a large count of recent transactions to find members
    url = f"{BASE_URL}/api/specialist/site/{site_id}/visits/closed?count=100&minPaymentDueAgeSeconds=0&zoneIds={site_id}"
    headers = {
        "Authorization": f"Bearer {AUTH_KEY}",
        "Accept": "*/*",
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('data'):
                transactions = data['data'].get('transactions', [])
                # Filter for members only
                members = []
                seen_users = set()
                for t in transactions:
                    user = t.get('user', {})
                    if user.get('isMember') and user.get('phoneNumber') not in seen_users:
                        member_info = {
                            'user': user,
                            'vehicle': t.get('vehicle', {}),
                            'hasSubscription': user.get('hasSubscription', False),
                            'lastVisit': t.get('end'),
                            'coveredBySubscription': t.get('coveredBySubscription', False)
                        }
                        members.append(member_info)
                        seen_users.add(user.get('phoneNumber'))
                return members
    except Exception as e:
        print(f"Error getting members: {e}")
    return []

def get_active_visits(site_id):
    """Get currently active visits (cars in garage/at gates)"""
    # Fetch closed visits - these show cars ready to exit
    url = f"{BASE_URL}/api/specialist/site/{site_id}/visits/closed?count=50&minPaymentDueAgeSeconds=0&zoneIds={site_id}"
    headers = {
        "Authorization": f"Bearer {AUTH_KEY}",
        "Accept": "*/*",
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            # Return transactions that have VEND_GATE action available
            if data.get('success') and data.get('data'):
                transactions = data['data'].get('transactions', [])
                # Filter for transactions that can be vended
                return [t for t in transactions if 'VEND_GATE' in t.get('availableActionsForSpecialist', [])]
    except Exception as e:
        print(f"Error getting visits: {e}")
    return None

def monitor_and_auto_open(status_callback):
    """Background thread to monitor for member vehicles and auto-open gates"""
    global monitoring_active

    last_opened = {}  # Track recently opened gates to avoid duplicates

    while monitoring_active:
        try:
            for site_id in ["4005", "4007"]:
                # Get active visits (transactions waiting to exit)
                transactions = get_active_visits(site_id)

                if transactions:
                    for transaction in transactions:
                        # Extract license plate from vehicle.licensePlate.text
                        vehicle = transaction.get('vehicle', {})
                        license_plate_obj = vehicle.get('licensePlate', {}) if vehicle else {}
                        plate = license_plate_obj.get('text', '').upper() if license_plate_obj else ''

                        # Get transaction ID (this is the visitId)
                        visit_id = transaction.get('id')

                        # Get exit lane ID from exit event
                        images = transaction.get('images', {})
                        exit_event = images.get('exitEvent') if images else None
                        site_equipment = exit_event.get('siteEquipment') if exit_event else None
                        lane_id = site_equipment.get('laneId') if site_equipment else None

                        # CHECK BLACKLIST FIRST - deny even if they're a member
                        if plate and plate in [p.upper() for p in blacklist_plates]:
                            if visit_id and visit_id not in last_opened:
                                user = transaction.get('user', {})
                                user_name = f"{user.get('firstName', '')} {user.get('lastName', '')}".strip()

                                status_callback(f"BLOCKED: {plate} ({user_name}) - ON BLACKLIST!")
                                print(f"[BLOCKED] Blacklisted plate detected: {plate} - NOT opening gate")
                                send_notification("BLACKLISTED VEHICLE", f"{plate} ({user_name}) blocked at site {site_id}")

                                last_opened[visit_id] = time.time()
                        # Check if plate is in member list
                        elif plate and plate in [p.upper() for p in member_plates]:
                            # Check if we haven't recently opened for this transaction
                            if visit_id and visit_id not in last_opened:
                                user = transaction.get('user', {})
                                user_name = f"{user.get('firstName', '')} {user.get('lastName', '')}".strip()

                                status_callback(f"AUTO-OPEN: {plate} ({user_name}) at site {site_id}")
                                print(f"[AUTO-OPEN] Detected member: {plate} - Transaction ID: {visit_id} - Lane: {lane_id}")

                                # Send notification
                                send_notification("Member Detected", f"{plate} ({user_name}) auto-opening gate")

                                # Open the gate at the detected lane
                                if lane_id:
                                    open_gate(str(lane_id), f"Auto Lane {lane_id}", None, site_id=site_id, visit_id=visit_id)
                                else:
                                    # Fallback to default lane for site
                                    default_lane = "5568" if site_id == "4005" else "5565"
                                    open_gate(default_lane, "Default Gate", None, site_id=site_id, visit_id=visit_id)

                                last_opened[visit_id] = time.time()

                # Clean up old entries (older than 10 minutes)
                current_time = time.time()
                last_opened = {k: v for k, v in last_opened.items() if current_time - v < 600}

            time.sleep(3)  # Check every 3 seconds

        except Exception as e:
            print(f"Monitor error: {e}")
            import traceback
            traceback.print_exc()
            time.sleep(5)

def decode_jwt_payload(token):
    """Decode JWT token payload to check expiration"""
    try:
        # JWT has 3 parts separated by dots: header.payload.signature
        parts = token.split('.')
        if len(parts) != 3:
            return None

        # Decode the payload (second part)
        payload = parts[1]
        # Add padding if needed
        padding = 4 - len(payload) % 4
        if padding != 4:
            payload += '=' * padding

        # Decode base64
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
    return current_time >= (exp - 300)  # 5 min buffer

def get_token_expiration_time(token):
    """Get token expiration time as datetime"""
    payload = decode_jwt_payload(token)
    if not payload:
        return None

    exp = payload.get('exp')
    if not exp:
        return None

    return datetime.fromtimestamp(exp)

def refresh_token_headless():
    """Get fresh token automatically using headless browser"""
    global AUTH_KEY

    if not HAS_SELENIUM:
        print("ERROR: Selenium not available. Cannot refresh token.")
        return None

    print("\n" + "="*60)
    print("🔄 REFRESHING TOKEN (Headless Mode)")
    print("="*60)

    try:
        # Setup headless browser
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--log-level=3')  # Suppress logs

        driver = webdriver.Edge(options=options)
        driver.get(LOGIN_URL)

        print("📱 Navigating to login page...")
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

            print("🔐 Waiting for authentication...")
            time.sleep(5)

        except Exception as e:
            print(f"⚠️ Login error: {e}")
            driver.quit()
            return None

        # Inject JavaScript to intercept fetch requests
        print("💉 Injecting token interceptor...")

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

        console.log('🎣 Token interceptor installed!');
        """

        driver.execute_script(intercept_script)
        print("✅ Interceptor installed!")

        # Wait for token capture
        print("⏳ Waiting for API call to capture token...")
        token = None

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

            print(f"   Waiting... ({i+1}s)", end='\r')

        driver.quit()

        if token:
            print(f"\n✅ SUCCESS! Token refreshed!")
            print(f"Token preview: {token[:50]}...")

            # Update global AUTH_KEY
            AUTH_KEY = token

            # Save to file for persistence
            with open('auth_token.txt', 'w') as f:
                f.write(token)

            # Update this script file
            script_path = __file__
            try:
                with open(script_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                pattern = r'AUTH_KEY = "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJpbXpVMnE4NXQxSDB5U2RpUHRKNmtmeWpkYXZlR2ZiaHdyZ01KbXNHZTQ4In0.eyJleHAiOjE3NjE1MTc1MTgsImlhdCI6MTc2MTUxMzkxOCwiYXV0aF90aW1lIjoxNzYxNTEzOTE3LCJqdGkiOiIzODVmNjE4MS00ZmI0LTRmOWMtYmQwZC1jOWUyNmVhNzQxOGEiLCJpc3MiOiJodHRwczovL2F1dGgubWV0cm9wb2xpcy5pby9yZWFsbXMvbWV0cm9wb2xpcyIsImF1ZCI6WyJtZXRyb3BvbGlzLXJlc291cmNlLWNsaWVudCIsIm1ldHJvcG9saXMtdXNlci1jbGllbnQiLCJtZXRyb3BvbGlzLXNlcnZlci1jbGllbnQiLCJhY2NvdW50Il0sInN1YiI6ImU2MzEzOWI2LWUyNzgtNGUwNS05ZDJmLTMzZWUxOGQwZGI4YyIsInR5cCI6IkJlYXJlciIsImF6cCI6Im1ldHJvcG9saXMtd2ViLWNsaWVudCIsIm5vbmNlIjoiMjhmM2M1MWUtZTg5ZS00MDdjLTg4ZTMtOTcwZWNmNzM5MzEzIiwic2Vzc2lvbl9zdGF0ZSI6IjM2MTg5MTBlLTQxMjQtNDNlYS1hYTRhLWI2ZmFkNzM0ZTMwNyIsImFjciI6IjEiLCJhbGxvd2VkLW9yaWdpbnMiOlsiaHR0cHM6Ly9tYW5hZ2VyLm1ldHJvcG9saXMuaW8iLCJodHRwczovL3BvcnRhbC5tZXRyb3BvbGlzLmlvIiwiaHR0cHM6Ly9yZXF1ZXN0Lm1ldHJvcG9saXMuaW8iLCJodHRwczovL2ludGFrZS5tZXRyb3BvbGlzLmlvIiwiaHR0cHM6Ly9kZXZvcHMudG9vbHMubWV0cm9wLmlvIiwiaHR0cHM6Ly9oYXJkd2FyZS5lZGdlLm1ldHJvcG9saXMuaW8iLCJodHRwczovL3NwZWNpYWxpc3QubWV0cm9wb2xpcy5pbyIsImh0dHA6Ly9sb2NhbGhvc3Q6MzAwMSIsImh0dHA6Ly9sb2NhbGhvc3Q6MzAwMCIsImh0dHBzOi8vZWRnZS5hdGcubWV0cm9wb2xpcy5pbyJdLCJyZWFsbV9hY2Nlc3MiOnsicm9sZXMiOlsiZGVmYXVsdC1yb2xlcy10ZXN0Iiwib2ZmbGluZV9hY2Nlc3MiLCJ1bWFfYXV0aG9yaXphdGlvbiJdfSwicmVzb3VyY2VfYWNjZXNzIjp7Im1ldHJvcG9saXMtc2VydmVyLWNsaWVudCI6eyJyb2xlcyI6WyJlbmZvcmNlbWVudCIsInBhcmtpbmcgcGFzcyIsInZhbGV0IiwiaW50YWtlIiwib3BlcmF0b3IiXX19LCJzY29wZSI6Im9wZW5pZCBwcm9maWxlIGVtYWlsIiwic2lkIjoiMzYxODkxMGUtNDEyNC00M2VhLWFhNGEtYjZmYWQ3MzRlMzA3IiwiZW1haWxfdmVyaWZpZWQiOnRydWUsIm5hbWUiOiI1NTUgU2VjdXJpdHkgIiwicHJlZmVycmVkX3VzZXJuYW1lIjoic2VjdXJpdHlANTU1Y2FwaXRvbG1hbGwuY29tIiwiZ2l2ZW5fbmFtZSI6IjU1NSIsImZhbWlseV9uYW1lIjoiU2VjdXJpdHkgIiwiZW1haWwiOiJzZWN1cml0eUA1NTVjYXBpdG9sbWFsbC5jb20ifQ.tb4ViCB42dJrFqs3lzowgG7jMdTAl_60jnG2AblsDou46Tn10IbJ-c2The3Ja2u4dcbQVqEjktGEXAExHZ44ehZD_AIo4dGx_hIEdbEz8nPoKVi-dYjO9U_HY7oZJZ0H2kXGwPUeiMhwaw7xlie1ifvwXiNZfkrCJ-gRxZ_06c6BKPUgyb-qsJ0UTeCcRu3OretpIXuD9iAabtrMTMIkJdVpAOzF0EFz9A5rempJqPbuYG-aTSjxegsoZSVkDzOq6hdMxCqgNOePyB_FK1GRXNyTtTbJVsiZXux1UeceUkrZWOWSedDepUK3T65eG23U1cKONgtfy5sLbv7J2GAawA"]*"'
                updated = re.sub(pattern, f'AUTH_KEY = "{token}"', content)

                with open(script_path, 'w', encoding='utf-8') as f:
                    f.write(updated)

                print(f"✅ Updated script file with new token!")
            except Exception as e:
                print(f"⚠️ Could not update script file: {e}")

            print("="*60)
            return token
        else:
            print("\n❌ No token captured after 30 seconds")
            print("="*60)
            return None

    except Exception as e:
        print(f"❌ Token refresh error: {e}")
        import traceback
        traceback.print_exc()
        try:
            driver.quit()
        except:
            pass
        return None

def token_monitor_loop(status_callback):
    """Background thread to monitor token expiration every 3 minutes"""
    global token_monitor_active, AUTH_KEY

    print("\n🔍 Token monitor started - checking every 3 minutes")

    while token_monitor_active:
        try:
            exp_time = get_token_expiration_time(AUTH_KEY)

            if exp_time:
                time_remaining = exp_time - datetime.now()
                hours = int(time_remaining.total_seconds() // 3600)
                minutes = int((time_remaining.total_seconds() % 3600) // 60)

                status_msg = f"Token expires in {hours}h {minutes}m"
                print(f"[TOKEN CHECK] {status_msg}")

                if status_callback:
                    status_callback(status_msg)

                # Check if expired or expiring soon (within 5 minutes)
                if is_token_expired(AUTH_KEY):
                    print("\n⚠️ TOKEN EXPIRED OR EXPIRING SOON - Auto-refreshing...")

                    if status_callback:
                        status_callback("🔄 Refreshing token...")

                    new_token = refresh_token_headless()

                    if new_token:
                        AUTH_KEY = new_token
                        print("✅ Token successfully refreshed!")
                        send_notification("Token Refreshed", "Authentication token has been automatically renewed")

                        if status_callback:
                            status_callback("✅ Token refreshed successfully!")
                    else:
                        print("❌ Token refresh failed!")
                        send_notification("Token Refresh Failed", "Could not renew authentication token")

                        if status_callback:
                            status_callback("❌ Token refresh failed!")
            else:
                print("[TOKEN CHECK] Could not decode token")
                if status_callback:
                    status_callback("⚠️ Token decode error")

            # Wait 3 minutes before next check
            time.sleep(180)

        except Exception as e:
            print(f"Token monitor error: {e}")
            import traceback
            traceback.print_exc()
            time.sleep(60)  # Wait 1 minute on error

def create_gui():
    """Create the multi-tab GUI"""

    window = tk.Tk()
    window.title("Metropolis Parking Management System")
    window.geometry("800x700")
    window.configure(bg='#1a1a1a')

    # Header
    header = tk.Frame(window, bg='#1a1a1a')
    header.pack(fill='x', pady=10)

    title = tk.Label(
        header,
        text="Metropolis Parking Management",
        font=("Arial", 18, "bold"),
        bg='#1a1a1a',
        fg='white'
    )
    title.pack()

    auth_status = tk.Label(
        header,
        text=f"Auth: ...{AUTH_KEY[-20:]}",
        font=("Arial", 8),
        bg='#1a1a1a',
        fg='#4CAF50'
    )
    auth_status.pack()

    # Create tab container
    notebook = ttk.Notebook(window)
    notebook.pack(fill='both', expand=True, padx=10, pady=10)

    # Style for tabs
    style = ttk.Style()
    style.theme_use('default')
    style.configure('TNotebook', background='#1a1a1a')
    style.configure('TNotebook.Tab', padding=[20, 10])

    # ==================== TAB 1: GATE CONTROLS ====================
    tab1 = tk.Frame(notebook, bg='#1a1a1a')
    notebook.add(tab1, text='Gate Controls')

    # Status label
    status_label = tk.Label(
        tab1,
        text="Ready",
        font=("Arial", 11),
        bg='#1a1a1a',
        fg='#4CAF50'
    )
    status_label.pack(pady=10)

    # Gates frame
    gates_frame = tk.Frame(tab1, bg='#1a1a1a')
    gates_frame.pack(padx=30, pady=10, fill='both', expand=True)

    # Confirmed gates from both sites
    gates = [
        {"id": "5568", "name": "6th Street Exit", "site_id": "4005"},
        {"id": "5569", "name": "L Street Exit", "site_id": "4005"},
        {"id": "5565", "name": "Bank of America Exit", "site_id": "4007"},
    ]

    # Create buttons for each gate
    for gate in gates:
        gate_id = gate['id']
        gate_name = gate['name']
        site_id = gate['site_id']

        btn = tk.Button(
            gates_frame,
            text=f"Open {gate_name}",
            command=lambda gid=gate_id, gn=gate_name, sid=site_id: open_gate(gid, gn, status_label, site_id=sid),
            bg='#1E88E5',
            fg='white',
            font=("Arial", 12, "bold"),
            height=2,
            cursor='hand2'
        )
        btn.pack(pady=8, fill='x')

    # ==================== TAB 2: WAITING CARS ====================
    tab2 = tk.Frame(notebook, bg='#1a1a1a')
    notebook.add(tab2, text='Waiting Cars')

    waiting_text = scrolledtext.ScrolledText(
        tab2,
        bg='#2a2a2a',
        fg='white',
        font=("Consolas", 10),
        height=25
    )
    waiting_text.pack(fill='both', expand=True, padx=10, pady=10)

    refresh_btn_waiting = tk.Button(
        tab2,
        text="Refresh",
        command=lambda: update_waiting_cars(waiting_text),
        bg='#4CAF50',
        fg='white',
        font=("Arial", 11, "bold"),
        cursor='hand2'
    )
    refresh_btn_waiting.pack(pady=5)

    # ==================== TAB 3: RECENT VISITS ====================
    tab3 = tk.Frame(notebook, bg='#1a1a1a')
    notebook.add(tab3, text='Recent Visits')

    visits_text = scrolledtext.ScrolledText(
        tab3,
        bg='#2a2a2a',
        fg='white',
        font=("Consolas", 9),
        height=25
    )
    visits_text.pack(fill='both', expand=True, padx=10, pady=10)

    refresh_btn_visits = tk.Button(
        tab3,
        text="Refresh",
        command=lambda: update_visits(visits_text),
        bg='#4CAF50',
        fg='white',
        font=("Arial", 11, "bold"),
        cursor='hand2'
    )
    refresh_btn_visits.pack(pady=5)

    # ==================== TAB 4: OCCUPANCY ====================
    tab4 = tk.Frame(notebook, bg='#1a1a1a')
    notebook.add(tab4, text='Occupancy')

    occupancy_text = scrolledtext.ScrolledText(
        tab4,
        bg='#2a2a2a',
        fg='white',
        font=("Consolas", 12),
        height=25
    )
    occupancy_text.pack(fill='both', expand=True, padx=10, pady=10)

    refresh_btn_occ = tk.Button(
        tab4,
        text="Refresh",
        command=lambda: update_occupancy(occupancy_text),
        bg='#4CAF50',
        fg='white',
        font=("Arial", 11, "bold"),
        cursor='hand2'
    )
    refresh_btn_occ.pack(pady=5)

    # ==================== TAB 5: MEMBERSHIPS ====================
    tab5 = tk.Frame(notebook, bg='#1a1a1a')
    notebook.add(tab5, text='Memberships')

    # Header
    tk.Label(
        tab5,
        text="Auto-Open Gate for Member Vehicles",
        font=("Arial", 14, "bold"),
        bg='#1a1a1a',
        fg='white'
    ).pack(pady=10)

    # Monitoring status
    monitor_status = tk.Label(
        tab5,
        text="Monitoring: OFF",
        font=("Arial", 11),
        bg='#1a1a1a',
        fg='#F44336'
    )
    monitor_status.pack(pady=5)

    # Member list frame
    list_frame = tk.Frame(tab5, bg='#1a1a1a')
    list_frame.pack(fill='both', expand=True, padx=20, pady=10)

    tk.Label(
        list_frame,
        text="Member License Plates:",
        font=("Arial", 11, "bold"),
        bg='#1a1a1a',
        fg='white'
    ).pack(anchor='w', pady=5)

    # Listbox for members
    members_listbox = tk.Listbox(
        list_frame,
        bg='#2a2a2a',
        fg='white',
        font=("Consolas", 11),
        selectmode=tk.SINGLE,
        height=15
    )
    members_listbox.pack(fill='both', expand=True, pady=5)

    # Add/Remove frame
    control_frame = tk.Frame(tab5, bg='#1a1a1a')
    control_frame.pack(fill='x', padx=20, pady=10)

    tk.Label(
        control_frame,
        text="License Plate:",
        bg='#1a1a1a',
        fg='white',
        font=("Arial", 10)
    ).pack(side='left', padx=5)

    plate_entry = tk.Entry(control_frame, font=("Arial", 11), width=15)
    plate_entry.pack(side='left', padx=5)

    def refresh_member_list():
        """Update the listbox with current members"""
        members_listbox.delete(0, tk.END)
        for plate in member_plates:
            members_listbox.insert(tk.END, plate)

    def add_member():
        """Add a new member plate"""
        plate = plate_entry.get().strip().upper()
        if plate:
            if plate not in member_plates:
                member_plates.append(plate)
                save_members()
                refresh_member_list()
                plate_entry.delete(0, tk.END)
                messagebox.showinfo("Success", f"Added {plate} to members")
            else:
                messagebox.showwarning("Duplicate", f"{plate} already in list")
        else:
            messagebox.showwarning("Error", "Please enter a license plate")

    def remove_member():
        """Remove selected member plate"""
        selection = members_listbox.curselection()
        if selection:
            plate = members_listbox.get(selection[0])
            member_plates.remove(plate)
            save_members()
            refresh_member_list()
            messagebox.showinfo("Success", f"Removed {plate}")
        else:
            messagebox.showwarning("Error", "Please select a plate to remove")

    def toggle_monitoring():
        """Start/stop auto-monitoring"""
        global monitoring_active, monitoring_thread

        if not monitoring_active:
            monitoring_active = True
            monitor_status.config(text="Monitoring: ON", fg='#4CAF50')
            toggle_btn.config(text="Stop Monitoring", bg='#F44336')

            def status_update(msg):
                monitor_status.config(text=f"Monitoring: ON - {msg}")

            monitoring_thread = threading.Thread(
                target=monitor_and_auto_open,
                args=(status_update,),
                daemon=True
            )
            monitoring_thread.start()
        else:
            monitoring_active = False
            monitor_status.config(text="Monitoring: OFF", fg='#F44336')
            toggle_btn.config(text="Start Monitoring", bg='#4CAF50')

    add_btn = tk.Button(
        control_frame,
        text="Add",
        command=add_member,
        bg='#4CAF50',
        fg='white',
        font=("Arial", 10, "bold"),
        cursor='hand2',
        width=8
    )
    add_btn.pack(side='left', padx=5)

    remove_btn = tk.Button(
        control_frame,
        text="Remove",
        command=remove_member,
        bg='#F44336',
        fg='white',
        font=("Arial", 10, "bold"),
        cursor='hand2',
        width=8
    )
    remove_btn.pack(side='left', padx=5)

    toggle_btn = tk.Button(
        control_frame,
        text="Start Monitoring",
        command=toggle_monitoring,
        bg='#4CAF50',
        fg='white',
        font=("Arial", 11, "bold"),
        cursor='hand2',
        width=15
    )
    toggle_btn.pack(side='right', padx=10)

    # Load members and refresh list
    load_members()
    refresh_member_list()

    # ==================== TAB 6: MEMBER DIRECTORY ====================
    tab6 = tk.Frame(notebook, bg='#1a1a1a')
    notebook.add(tab6, text='Member Directory')

    # Header
    tk.Label(
        tab6,
        text="All Members with Active Subscriptions",
        font=("Arial", 14, "bold"),
        bg='#1a1a1a',
        fg='white'
    ).pack(pady=10)

    # Member directory display
    directory_text = scrolledtext.ScrolledText(
        tab6,
        bg='#2a2a2a',
        fg='white',
        font=("Consolas", 10),
        height=30,
        wrap=tk.WORD
    )
    directory_text.pack(fill='both', expand=True, padx=10, pady=10)

    def update_member_directory():
        """Fetch and display all members"""
        directory_text.delete('1.0', tk.END)
        directory_text.insert(tk.END, "Loading member directory...\n\n")

        def fetch():
            all_members = []

            # Get members from both sites
            for site_id in ["4005", "4007"]:
                site_name = "555 Capitol Mall" if site_id == "4005" else "Bank of America"
                members = get_all_members(site_id)

                if members:
                    directory_text.insert(tk.END, f"\n{'='*80}\n")
                    directory_text.insert(tk.END, f"  {site_name} (Site {site_id}) - {len(members)} Members\n")
                    directory_text.insert(tk.END, f"{'='*80}\n\n")

                    for idx, member in enumerate(members, 1):
                        user = member['user']
                        vehicle = member['vehicle']

                        # User info
                        name = f"{user.get('firstName', '')} {user.get('lastName', '')}".strip()
                        phone = user.get('phoneNumber', 'N/A')
                        has_sub = "YES" if member['hasSubscription'] else "NO"

                        # Vehicle info
                        plate_obj = vehicle.get('licensePlate', {})
                        plate = plate_obj.get('text', 'N/A')
                        state = plate_obj.get('state', {}).get('name', '')

                        make_obj = vehicle.get('make', {})
                        make = make_obj.get('name', 'Unknown') if make_obj else 'Unknown'

                        model_obj = vehicle.get('model', {})
                        model = model_obj.get('name', 'Unknown') if model_obj else 'Unknown'

                        color = vehicle.get('color', 'Unknown')

                        # Last visit time
                        last_visit_ms = member.get('lastVisit')
                        if last_visit_ms:
                            last_visit = datetime.fromtimestamp(last_visit_ms / 1000).strftime('%Y-%m-%d %H:%M')
                        else:
                            last_visit = 'N/A'

                        # Format member entry
                        directory_text.insert(tk.END, f"[{idx}] {name}\n")
                        directory_text.insert(tk.END, f"    Phone: {phone}\n")
                        directory_text.insert(tk.END, f"    Subscription: {has_sub}\n")
                        directory_text.insert(tk.END, f"    Vehicle: {color} {make} {model}\n")
                        directory_text.insert(tk.END, f"    Plate: {plate} ({state})\n")
                        directory_text.insert(tk.END, f"    Last Visit: {last_visit}\n")
                        directory_text.insert(tk.END, f"\n")

            directory_text.insert(tk.END, f"\n{'='*80}\n")
            directory_text.insert(tk.END, "End of Directory\n")

        threading.Thread(target=fetch, daemon=True).start()

    refresh_btn_directory = tk.Button(
        tab6,
        text="Refresh Directory",
        command=update_member_directory,
        bg='#4CAF50',
        fg='white',
        font=("Arial", 11, "bold"),
        cursor='hand2'
    )
    refresh_btn_directory.pack(pady=5)

    # Initial load
    update_member_directory()

    # ==================== TAB 7: BLACKLIST ====================
    tab7 = tk.Frame(notebook, bg='#1a1a1a')
    notebook.add(tab7, text='Blacklist')

    # Header
    tk.Label(
        tab7,
        text="Blacklisted Vehicles - AUTO-DENY Gate Access",
        font=("Arial", 14, "bold"),
        bg='#1a1a1a',
        fg='#F44336'
    ).pack(pady=10)

    tk.Label(
        tab7,
        text="⚠️ Blacklisted plates will be BLOCKED even if they're members",
        font=("Arial", 10),
        bg='#1a1a1a',
        fg='#FFA726'
    ).pack(pady=5)

    # Blacklist frame
    blacklist_frame = tk.Frame(tab7, bg='#1a1a1a')
    blacklist_frame.pack(fill='both', expand=True, padx=20, pady=10)

    tk.Label(
        blacklist_frame,
        text="Blacklisted License Plates:",
        font=("Arial", 11, "bold"),
        bg='#1a1a1a',
        fg='white'
    ).pack(anchor='w', pady=5)

    blacklist_listbox = tk.Listbox(
        blacklist_frame,
        bg='#2a2a2a',
        fg='#F44336',
        font=("Consolas", 11, "bold"),
        selectmode=tk.SINGLE,
        height=15
    )
    blacklist_listbox.pack(fill='both', expand=True, pady=5)

    # Control frame
    blacklist_control = tk.Frame(tab7, bg='#1a1a1a')
    blacklist_control.pack(fill='x', padx=20, pady=10)

    tk.Label(
        blacklist_control,
        text="License Plate:",
        bg='#1a1a1a',
        fg='white',
        font=("Arial", 10)
    ).pack(side='left', padx=5)

    blacklist_entry = tk.Entry(blacklist_control, font=("Arial", 11), width=15)
    blacklist_entry.pack(side='left', padx=5)

    def refresh_blacklist():
        blacklist_listbox.delete(0, tk.END)
        for plate in blacklist_plates:
            blacklist_listbox.insert(tk.END, plate)

    def add_to_blacklist():
        plate = blacklist_entry.get().strip().upper()
        if plate:
            if plate not in blacklist_plates:
                blacklist_plates.append(plate)
                save_blacklist()
                refresh_blacklist()
                blacklist_entry.delete(0, tk.END)
                messagebox.showwarning("Blacklisted", f"{plate} added to blacklist - will be auto-denied!")
            else:
                messagebox.showwarning("Duplicate", f"{plate} already blacklisted")
        else:
            messagebox.showwarning("Error", "Please enter a license plate")

    def remove_from_blacklist():
        selection = blacklist_listbox.curselection()
        if selection:
            plate = blacklist_listbox.get(selection[0])
            blacklist_plates.remove(plate)
            save_blacklist()
            refresh_blacklist()
            messagebox.showinfo("Removed", f"{plate} removed from blacklist")
        else:
            messagebox.showwarning("Error", "Please select a plate to remove")

    tk.Button(
        blacklist_control,
        text="Add to Blacklist",
        command=add_to_blacklist,
        bg='#F44336',
        fg='white',
        font=("Arial", 10, "bold"),
        width=15
    ).pack(side='left', padx=5)

    tk.Button(
        blacklist_control,
        text="Remove",
        command=remove_from_blacklist,
        bg='#4CAF50',
        fg='white',
        font=("Arial", 10, "bold"),
        width=10
    ).pack(side='left', padx=5)

    load_blacklist()
    refresh_blacklist()

    # ==================== TAB 8: TOKEN MANAGEMENT ====================
    tab8 = tk.Frame(notebook, bg='#1a1a1a')
    notebook.add(tab8, text='Token Management')

    tk.Label(
        tab8,
        text="🔐 Authentication Token Management",
        font=("Arial", 16, "bold"),
        bg='#1a1a1a',
        fg='white'
    ).pack(pady=20)

    token_frame = tk.Frame(tab8, bg='#2a2a2a')
    token_frame.pack(padx=40, pady=20, fill='both', expand=True)

    # Token status display
    token_info_frame = tk.Frame(token_frame, bg='#2a2a2a')
    token_info_frame.pack(fill='x', padx=20, pady=10)

    tk.Label(
        token_info_frame,
        text="Current Token Status:",
        font=("Arial", 12, "bold"),
        bg='#2a2a2a',
        fg='white'
    ).pack(anchor='w', pady=5)

    # Display token expiration
    exp_time = get_token_expiration_time(AUTH_KEY)
    if exp_time:
        time_remaining = exp_time - datetime.now()
        hours = int(time_remaining.total_seconds() // 3600)
        minutes = int((time_remaining.total_seconds() % 3600) // 60)
        exp_str = f"Expires: {exp_time.strftime('%Y-%m-%d %H:%M:%S')}"
        remaining_str = f"Time Remaining: {hours}h {minutes}m"

        if is_token_expired(AUTH_KEY):
            status_color = '#F44336'
            status_text = "⚠️ EXPIRED or EXPIRING SOON"
        else:
            status_color = '#4CAF50'
            status_text = "✅ VALID"
    else:
        exp_str = "Expires: Unable to decode"
        remaining_str = "Time Remaining: Unknown"
        status_color = '#FFA726'
        status_text = "⚠️ UNKNOWN"

    token_exp_label = tk.Label(
        token_info_frame,
        text=exp_str,
        font=("Consolas", 10),
        bg='#2a2a2a',
        fg='white'
    )
    token_exp_label.pack(anchor='w', padx=20)

    token_remaining_label = tk.Label(
        token_info_frame,
        text=remaining_str,
        font=("Consolas", 10),
        bg='#2a2a2a',
        fg='white'
    )
    token_remaining_label.pack(anchor='w', padx=20)

    token_status_label = tk.Label(
        token_info_frame,
        text=f"Status: {status_text}",
        font=("Arial", 11, "bold"),
        bg='#2a2a2a',
        fg=status_color
    )
    token_status_label.pack(anchor='w', padx=20, pady=5)

    # Auto-monitor status
    monitor_status_label = tk.Label(
        token_frame,
        text="Auto-Monitor: OFF",
        font=("Arial", 11),
        bg='#2a2a2a',
        fg='#F44336'
    )
    monitor_status_label.pack(pady=10)

    # Separator
    tk.Frame(token_frame, bg='#444', height=2).pack(fill='x', padx=20, pady=15)

    # Manual Test Button
    def manual_token_test():
        """Manually trigger token refresh for testing"""
        test_btn.config(state='disabled', text="🔄 Refreshing...")
        window.update()

        def refresh_thread():
            new_token = refresh_token_headless()

            if new_token:
                global AUTH_KEY
                AUTH_KEY = new_token
                messagebox.showinfo("Success", "Token refreshed successfully!\n\nThe application will now use the new token.")

                # Update display
                update_token_display()
            else:
                messagebox.showerror("Error", "Failed to refresh token.\n\nCheck console for details.")

            test_btn.config(state='normal', text="🧪 Test Token Refresh")

        threading.Thread(target=refresh_thread, daemon=True).start()

    def update_token_display():
        """Update token status display"""
        exp_time = get_token_expiration_time(AUTH_KEY)
        if exp_time:
            time_remaining = exp_time - datetime.now()
            hours = int(time_remaining.total_seconds() // 3600)
            minutes = int((time_remaining.total_seconds() % 3600) // 60)
            exp_str = f"Expires: {exp_time.strftime('%Y-%m-%d %H:%M:%S')}"
            remaining_str = f"Time Remaining: {hours}h {minutes}m"

            if is_token_expired(AUTH_KEY):
                status_color = '#F44336'
                status_text = "⚠️ EXPIRED or EXPIRING SOON"
            else:
                status_color = '#4CAF50'
                status_text = "✅ VALID"
        else:
            exp_str = "Expires: Unable to decode"
            remaining_str = "Time Remaining: Unknown"
            status_color = '#FFA726'
            status_text = "⚠️ UNKNOWN"

        token_exp_label.config(text=exp_str)
        token_remaining_label.config(text=remaining_str)
        token_status_label.config(text=f"Status: {status_text}", fg=status_color)

    test_btn = tk.Button(
        token_frame,
        text="🧪 Test Token Refresh",
        command=manual_token_test,
        bg='#1E88E5',
        fg='white',
        font=("Arial", 14, "bold"),
        height=2,
        cursor='hand2'
    )
    test_btn.pack(pady=10, fill='x', padx=40)

    tk.Label(
        token_frame,
        text="Manually refresh the authentication token (for testing)",
        font=("Arial", 9),
        bg='#2a2a2a',
        fg='#888'
    ).pack()

    # Auto-monitor toggle
    def toggle_token_monitor():
        """Start/stop automatic token monitoring"""
        global token_monitor_active, token_monitor_thread

        if not HAS_SELENIUM:
            messagebox.showerror("Error", "Selenium not available.\n\nCannot enable auto token refresh.")
            return

        if not token_monitor_active:
            token_monitor_active = True
            monitor_status_label.config(text="Auto-Monitor: ON - Checking every 3 minutes", fg='#4CAF50')
            monitor_toggle_btn.config(text="⏸ Stop Auto-Monitor", bg='#F44336')

            def status_update(msg):
                monitor_status_label.config(text=f"Auto-Monitor: ON - {msg}")
                update_token_display()

            token_monitor_thread = threading.Thread(
                target=token_monitor_loop,
                args=(status_update,),
                daemon=True
            )
            token_monitor_thread.start()
        else:
            token_monitor_active = False
            monitor_status_label.config(text="Auto-Monitor: OFF", fg='#F44336')
            monitor_toggle_btn.config(text="▶ Start Auto-Monitor", bg='#4CAF50')

    tk.Frame(token_frame, bg='#444', height=2).pack(fill='x', padx=20, pady=15)

    monitor_toggle_btn = tk.Button(
        token_frame,
        text="▶ Start Auto-Monitor",
        command=toggle_token_monitor,
        bg='#4CAF50',
        fg='white',
        font=("Arial", 13, "bold"),
        height=2,
        cursor='hand2'
    )
    monitor_toggle_btn.pack(pady=10, fill='x', padx=40)

    tk.Label(
        token_frame,
        text="Automatically check token every 3 minutes and refresh if needed",
        font=("Arial", 9),
        bg='#2a2a2a',
        fg='#888'
    ).pack()

    # Info section
    info_frame = tk.Frame(token_frame, bg='#1a3a4a', relief=tk.RAISED, borderwidth=1)
    info_frame.pack(fill='x', padx=20, pady=20)

    tk.Label(
        info_frame,
        text="ℹ️ How Auto-Monitor Works:",
        font=("Arial", 10, "bold"),
        bg='#1a3a4a',
        fg='white'
    ).pack(anchor='w', padx=10, pady=(10, 5))

    tk.Label(
        info_frame,
        text="• Checks token expiration every 3 minutes\n"
             "• Automatically refreshes if token expires within 5 minutes\n"
             "• Uses headless browser (no windows appear)\n"
             "• Updates AUTH_KEY in memory and saves to file\n"
             "• Sends desktop notification on refresh",
        font=("Arial", 9),
        bg='#1a3a4a',
        fg='#ccc',
        justify='left'
    ).pack(anchor='w', padx=20, pady=(0, 10))

    # ==================== TAB 9: EMERGENCY CONTROLS ====================
    tab9 = tk.Frame(notebook, bg='#1a1a1a')
    notebook.add(tab9, text='Emergency Controls')

    tk.Label(
        tab9,
        text="⚠️ EMERGENCY GATE CONTROLS ⚠️",
        font=("Arial", 16, "bold"),
        bg='#1a1a1a',
        fg='#F44336'
    ).pack(pady=20)

    emergency_frame = tk.Frame(tab9, bg='#2a2a2a')
    emergency_frame.pack(padx=40, pady=20, fill='both', expand=True)

    def open_all_gates():
        response = messagebox.askyesno(
            "CONFIRM EMERGENCY ACTION",
            "Open ALL gates at BOTH sites?\n\n" +
            "This will:\n" +
            "- Open 6th Street Exit (Site 4005)\n" +
            "- Open L Street Exit (Site 4005)\n" +
            "- Open Bank of America Exit (Site 4007)\n\n" +
            "Continue?"
        )
        if response:
            gates = [
                ("5568", "6th Street Exit", "4005"),
                ("5569", "L Street Exit", "4005"),
                ("5565", "Bank of America Exit", "4007"),
            ]
            for lane_id, name, site in gates:
                print(f"Emergency open: {name}")
                open_gate(lane_id, name, None, site_id=site)

            send_notification("EMERGENCY", "All gates opened!")
            messagebox.showinfo("Complete", "All gates have been opened!")

    tk.Button(
        emergency_frame,
        text="🚨 OPEN ALL GATES 🚨",
        command=open_all_gates,
        bg='#F44336',
        fg='white',
        font=("Arial", 18, "bold"),
        height=3,
        cursor='hand2'
    ).pack(pady=30, fill='x', padx=40)

    tk.Label(
        emergency_frame,
        text="Use this in emergencies to open all gates simultaneously",
        font=("Arial", 11),
        bg='#2a2a2a',
        fg='white'
    ).pack(pady=10)

    # Toggle notifications
    def toggle_notifications():
        global notifications_enabled
        notifications_enabled = not notifications_enabled
        if notifications_enabled:
            notif_btn.config(text="🔔 Notifications: ON", bg='#4CAF50')
            send_notification("Notifications Enabled", "You will receive alerts")
        else:
            notif_btn.config(text="🔕 Notifications: OFF", bg='#F44336')

    notif_btn = tk.Button(
        emergency_frame,
        text=f"🔔 Notifications: {'ON' if notifications_enabled else 'OFF'}",
        command=toggle_notifications,
        bg='#4CAF50' if notifications_enabled else '#F44336',
        fg='white',
        font=("Arial", 12, "bold"),
        height=2,
        cursor='hand2'
    )
    notif_btn.pack(pady=10, fill='x', padx=40)

    # ==================== TAB 10: CAMERA/IMAGES ====================
    tab10 = tk.Frame(notebook, bg='#1a1a1a')
    notebook.add(tab10, text='Camera/Images')

    tk.Label(
        tab10,
        text="Live Vehicle Activity",
        font=("Arial", 14, "bold"),
        bg='#1a1a1a',
        fg='white'
    ).pack(pady=10)

    # Create canvas with scrollbar for cards
    canvas_frame = tk.Frame(tab10, bg='#1a1a1a')
    canvas_frame.pack(fill='both', expand=True, padx=10, pady=5)

    canvas = tk.Canvas(canvas_frame, bg='#1a1a1a', highlightthickness=0)
    scrollbar = tk.Scrollbar(canvas_frame, orient='vertical', command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg='#1a1a1a')

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side='left', fill='both', expand=True)
    scrollbar.pack(side='right', fill='y')

    # Mouse wheel scrolling
    def on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    canvas.bind_all("<MouseWheel>", on_mousewheel)

    def download_image(url, size=(150, 100)):
        """Download and resize image from URL"""
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                img_data = BytesIO(response.content)
                if HAS_PIL:
                    img = Image.open(img_data)
                    img.thumbnail(size, Image.Resampling.LANCZOS)
                    return ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"Image download error: {e}")
        return None

    def create_vehicle_card(parent, transaction, is_entry=True):
        """Create a card showing vehicle entry or exit"""
        vehicle = transaction.get('vehicle', {})
        plate_obj = vehicle.get('licensePlate', {})
        plate = plate_obj.get('text', 'N/A')
        state = plate_obj.get('state', {}).get('name', 'CA')

        user = transaction.get('user', {})
        name = f"{user.get('firstName', '')} {user.get('lastName', '')}".strip()
        is_member = user.get('isMember', False)

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
        images = transaction.get('images', {})
        event = images.get('entryEvent' if is_entry else 'exitEvent', {})
        equipment = event.get('siteEquipment') if event else None
        lane_name = equipment.get('notes', 'Unknown Lane') if equipment else 'Unknown Lane'
        context_url = event.get('contextImageUrl') if event else None

        # Card frame
        card = tk.Frame(parent, bg='#2a2a2a', relief=tk.RAISED, borderwidth=1)
        card.pack(fill='x', padx=10, pady=5)

        # Left: Image
        img_frame = tk.Frame(card, bg='#2a2a2a')
        img_frame.pack(side='left', padx=10, pady=10)

        if context_url and HAS_PIL:
            def load_img():
                photo = download_image(context_url, (150, 100))
                if photo:
                    img_label = tk.Label(img_frame, image=photo, bg='#2a2a2a')
                    img_label.image = photo  # Keep reference
                    img_label.pack()
                else:
                    tk.Label(img_frame, text="[No Image]", bg='#2a2a2a', fg='#666', width=20, height=6).pack()
            threading.Thread(target=load_img, daemon=True).start()
        else:
            tk.Label(img_frame, text="[No Image]", bg='#2a2a2a', fg='#666', width=20, height=6).pack()

        # Middle: Info
        info_frame = tk.Frame(card, bg='#2a2a2a')
        info_frame.pack(side='left', fill='both', expand=True, padx=10, pady=10)

        # License plate box
        plate_frame = tk.Frame(info_frame, bg='#1E88E5', relief=tk.RAISED, borderwidth=2)
        plate_frame.pack(anchor='w', pady=5)

        tk.Label(
            plate_frame,
            text=plate,
            font=("Arial", 14, "bold"),
            bg='#1E88E5',
            fg='white',
            padx=10,
            pady=2
        ).pack(side='left')

        tk.Label(
            plate_frame,
            text=state,
            font=("Arial", 10),
            bg='white',
            fg='black',
            padx=5,
            pady=2
        ).pack(side='left')

        # Entry/Exit indicator with arrow
        direction_color = '#4CAF50' if is_entry else '#F44336'
        direction_text = '→ ENTRY' if is_entry else '← EXIT'
        tk.Label(
            info_frame,
            text=direction_text,
            font=("Arial", 10, "bold"),
            bg='#2a2a2a',
            fg=direction_color
        ).pack(anchor='w')

        # Lane/Location
        tk.Label(
            info_frame,
            text=lane_name,
            font=("Arial", 9),
            bg='#2a2a2a',
            fg='#aaa'
        ).pack(anchor='w')

        # Right: Status and time
        right_frame = tk.Frame(card, bg='#2a2a2a')
        right_frame.pack(side='right', padx=15, pady=10)

        # Time
        tk.Label(
            right_frame,
            text=time_str,
            font=("Arial", 12, "bold"),
            bg='#2a2a2a',
            fg='white'
        ).pack()

        tk.Label(
            right_frame,
            text=date_str,
            font=("Arial", 8),
            bg='#2a2a2a',
            fg='#888'
        ).pack()

        # Member status
        if is_member and name:
            tk.Label(
                right_frame,
                text=name,
                font=("Arial", 9, "bold"),
                bg='#2a2a2a',
                fg='#4CAF50'
            ).pack(pady=(10, 0))
        elif name:
            tk.Label(
                right_frame,
                text="New Visitor",
                font=("Arial", 9),
                bg='#2a2a2a',
                fg='#FFA726'
            ).pack(pady=(10, 0))

    def load_recent_images():
        # Clear existing cards
        for widget in scrollable_frame.winfo_children():
            widget.destroy()

        tk.Label(
            scrollable_frame,
            text="Loading recent activity...",
            bg='#1a1a1a',
            fg='white',
            font=("Arial", 11)
        ).pack(pady=20)

        def fetch():
            # Clear loading message
            for widget in scrollable_frame.winfo_children():
                widget.destroy()

            all_transactions = []

            # Get transactions from both sites
            for site_id in ["4005", "4007"]:
                site_name = "555 Capitol Mall" if site_id == "4005" else "Bank of America"
                data = get_closed_visits(site_id, count=15)

                if data and data.get('success') and data.get('data'):
                    transactions = data['data'].get('transactions', [])

                    # Site header
                    tk.Label(
                        scrollable_frame,
                        text=f"{'='*60}\n  {site_name}\n{'='*60}",
                        bg='#1a1a1a',
                        fg='white',
                        font=("Consolas", 10),
                        justify='left'
                    ).pack(fill='x', pady=(10, 5))

                    for t in transactions[:10]:
                        # Show both entry and exit if available
                        images = t.get('images', {})
                        if images.get('entryEvent'):
                            create_vehicle_card(scrollable_frame, t, is_entry=True)
                        if images.get('exitEvent'):
                            create_vehicle_card(scrollable_frame, t, is_entry=False)

        threading.Thread(target=fetch, daemon=True).start()

    refresh_btn_cam = tk.Button(
        tab10,
        text="Refresh Activity",
        command=load_recent_images,
        bg='#4CAF50',
        fg='white',
        font=("Arial", 11, "bold"),
        cursor='hand2'
    )
    refresh_btn_cam.pack(pady=5)

    # Initial load
    load_recent_images()

    # ==================== TAB 11: LIVE FEED ====================
    tab11 = tk.Frame(notebook, bg='#1a1a1a')
    notebook.add(tab11, text='Live Feed')

    tk.Label(
        tab11,
        text="🔴 LIVE Camera Feeds",
        font=("Arial", 14, "bold"),
        bg='#1a1a1a',
        fg='#F44336'
    ).pack(pady=10)

    # Live feed control
    live_feed_active = False
    live_feed_thread = None

    # Camera grid
    cameras_frame = tk.Frame(tab11, bg='#1a1a1a')
    cameras_frame.pack(fill='both', expand=True, padx=10, pady=10)

    # Define cameras for each lane
    cameras = {
        '4005': [
            {'lane': '5568', 'name': '6th Street Exit', 'label': None, 'last_url': None},
            {'lane': '5569', 'name': 'L Street Exit', 'label': None, 'last_url': None},
            {'lane': '5570', 'name': 'Garage → Nest', 'label': None, 'last_url': None},
        ],
        '4007': [
            {'lane': '5565', 'name': 'Bank of America Exit', 'label': None, 'last_url': None},
        ]
    }

    # Create camera displays in grid
    row = 0
    for site_id, cams in cameras.items():
        site_name = "555 Capitol Mall" if site_id == "4005" else "Bank of America"

        tk.Label(
            cameras_frame,
            text=f"━━━ {site_name} ━━━",
            font=("Arial", 11, "bold"),
            bg='#1a1a1a',
            fg='white'
        ).grid(row=row, column=0, columnspan=2, pady=(10, 5), sticky='w')
        row += 1

        for cam in cams:
            # Camera frame
            cam_frame = tk.Frame(cameras_frame, bg='#2a2a2a', relief=tk.RAISED, borderwidth=2)
            cam_frame.grid(row=row, column=0, padx=5, pady=5, sticky='nsew')

            # Camera name
            tk.Label(
                cam_frame,
                text=cam['name'],
                font=("Arial", 10, "bold"),
                bg='#2a2a2a',
                fg='white'
            ).pack(pady=5)

            # Image display
            img_label = tk.Label(cam_frame, bg='#000', width=40, height=20)
            img_label.pack(padx=10, pady=10)
            cam['label'] = img_label

            # Status
            status_label = tk.Label(
                cam_frame,
                text="⚫ Waiting for data...",
                font=("Arial", 8),
                bg='#2a2a2a',
                fg='#888'
            )
            status_label.pack(pady=5)
            cam['status_label'] = status_label

            row += 1

    # Make grid responsive
    cameras_frame.grid_columnconfigure(0, weight=1)

    def update_camera_feed(cam, site_id, image_url, plate_text=""):
        """Update a single camera feed"""
        if image_url and image_url != cam['last_url']:
            cam['last_url'] = image_url

            def load():
                photo = download_image(image_url, (320, 240))
                if photo:
                    cam['label'].config(image=photo)
                    cam['label'].image = photo
                    cam['status_label'].config(
                        text=f"🔴 LIVE - {plate_text}" if plate_text else "🔴 LIVE",
                        fg='#F44336'
                    )

            threading.Thread(target=load, daemon=True).start()

    def live_feed_loop():
        """Continuously update live feeds"""
        while live_feed_active:
            try:
                for site_id, cams in cameras.items():
                    # Get latest transactions
                    data = get_closed_visits(site_id, count=5)

                    if data and data.get('success') and data.get('data'):
                        transactions = data['data'].get('transactions', [])

                        # Map latest image to each lane
                        lane_images = {}
                        for t in transactions:
                            images = t.get('images', {})
                            vehicle = t.get('vehicle', {})
                            plate = vehicle.get('licensePlate', {}).get('text', '') if vehicle else ''

                            # Try exit event first (more recent)
                            exit_event = images.get('exitEvent') if images else None
                            if exit_event:
                                equipment = exit_event.get('siteEquipment') if exit_event else None
                                if equipment:
                                    lane = str(equipment.get('laneId', ''))
                                    url = exit_event.get('contextImageUrl')
                                    if lane and url and lane not in lane_images:
                                        lane_images[lane] = (url, plate)

                            # Also check entry event
                            entry_event = images.get('entryEvent') if images else None
                            if entry_event:
                                equipment = entry_event.get('siteEquipment') if entry_event else None
                                if equipment:
                                    lane = str(equipment.get('laneId', ''))
                                    url = entry_event.get('contextImageUrl')
                                    if lane and url and lane not in lane_images:
                                        lane_images[lane] = (url, plate)

                        # Update camera displays
                        for cam in cams:
                            lane = cam['lane']
                            if lane in lane_images:
                                url, plate = lane_images[lane]
                                update_camera_feed(cam, site_id, url, plate)

                time.sleep(0.2)  # 5 FPS refresh rate

            except Exception as e:
                print(f"Live feed error: {e}")
                import traceback
                traceback.print_exc()
                time.sleep(1)

    def toggle_live_feed():
        global live_feed_active, live_feed_thread

        if not live_feed_active:
            live_feed_active = True
            live_feed_btn.config(text="⏸ Stop Live Feed", bg='#F44336')
            live_feed_thread = threading.Thread(target=live_feed_loop, daemon=True)
            live_feed_thread.start()
        else:
            live_feed_active = False
            live_feed_btn.config(text="▶ Start Live Feed", bg='#4CAF50')

    live_feed_btn = tk.Button(
        tab11,
        text="▶ Start Live Feed",
        command=toggle_live_feed,
        bg='#4CAF50',
        fg='white',
        font=("Arial", 12, "bold"),
        height=2,
        cursor='hand2'
    )
    live_feed_btn.pack(pady=10, fill='x', padx=40)

    tk.Label(
        tab11,
        text="Updates every 0.2 seconds (5 FPS)",
        font=("Arial", 9),
        bg='#1a1a1a',
        fg='#888'
    ).pack()

    # Auto-refresh functions
    def update_waiting_cars(text_widget):
        text_widget.delete('1.0', tk.END)
        text_widget.insert(tk.END, "Loading waiting cars...\n\n")

        def fetch():
            for site_id in ["4005", "4007"]:
                site_name = "555 Capitol Mall" if site_id == "4005" else "Bank of America"
                data = get_hanging_exits(site_id)
                if data:
                    text_widget.insert(tk.END, f"{'='*50}\n")
                    text_widget.insert(tk.END, f"{site_name} (Site {site_id})\n")
                    text_widget.insert(tk.END, f"{'='*50}\n")
                    text_widget.insert(tk.END, json.dumps(data, indent=2))
                    text_widget.insert(tk.END, "\n\n")

        threading.Thread(target=fetch, daemon=True).start()

    def update_visits(text_widget):
        text_widget.delete('1.0', tk.END)
        text_widget.insert(tk.END, "Loading recent visits...\n\n")

        def fetch():
            for site_id in ["4005", "4007"]:
                site_name = "555 Capitol Mall" if site_id == "4005" else "Bank of America"
                data = get_closed_visits(site_id, count=10)
                if data:
                    text_widget.insert(tk.END, f"{'='*50}\n")
                    text_widget.insert(tk.END, f"{site_name} (Site {site_id})\n")
                    text_widget.insert(tk.END, f"{'='*50}\n")
                    text_widget.insert(tk.END, json.dumps(data, indent=2))
                    text_widget.insert(tk.END, "\n\n")

        threading.Thread(target=fetch, daemon=True).start()

    def update_occupancy(text_widget):
        text_widget.delete('1.0', tk.END)
        text_widget.insert(tk.END, "Loading occupancy data...\n\n")

        def fetch():
            for site_id in ["4005", "4007"]:
                site_name = "555 Capitol Mall" if site_id == "4005" else "Bank of America"
                data = get_occupancy(site_id)
                if data:
                    text_widget.insert(tk.END, f"{'='*50}\n")
                    text_widget.insert(tk.END, f"{site_name} (Site {site_id})\n")
                    text_widget.insert(tk.END, f"{'='*50}\n")
                    text_widget.insert(tk.END, json.dumps(data, indent=2))
                    text_widget.insert(tk.END, "\n\n")

        threading.Thread(target=fetch, daemon=True).start()

    # Initial load
    update_waiting_cars(waiting_text)
    update_occupancy(occupancy_text)

    window.mainloop()

if __name__ == "__main__":
    print("="*80)
    print("METROPOLIS PARKING MANAGEMENT SYSTEM")
    print("="*80)
    print(f"Auth Key: {AUTH_KEY[:50]}...")
    print(f"Sites: 4005 (555 Capitol Mall), 4007 (Bank of America)")
    print("="*80)

    create_gui()
