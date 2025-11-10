from flask import Flask, render_template_string, jsonify, request
import requests
import json
import threading
import time
import os
import base64
import re
from datetime import datetime
from io import BytesIO
import atexit

# Selenium for token refresh
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.chrome.options import Options
    HAS_SELENIUM = True
except:
    HAS_SELENIUM = False
    print("Warning: Selenium not available. Auto token refresh disabled.")

app = Flask(__name__)

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

# Background services - ALWAYS RUNNING
monitoring_active = True  # Always True - runs forever
monitoring_thread = None
token_monitor_active = True  # Always True - runs forever
token_monitor_thread = None

# Status tracking
current_status = {
    "monitoring": "STARTING...", 
    "token_monitor": "STARTING...", 
    "last_action": "System initializing...",
    "monitoring_cycles": 0,
    "token_checks": 0,
    "gates_opened": 0,
    "vehicles_blocked": 0
}

def log(msg):
    """Timestamped logging"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {msg}")

def load_members():
    global member_plates
    if os.path.exists(MEMBERS_FILE):
        try:
            with open(MEMBERS_FILE, 'r') as f:
                member_plates = json.load(f)
            log(f"✅ Loaded {len(member_plates)} member plates")
        except Exception as e:
            log(f"❌ Error loading members: {e}")
            member_plates = []
    else:
        member_plates = []
        log("📝 No existing members file - starting fresh")

def save_members():
    try:
        with open(MEMBERS_FILE, 'w') as f:
            json.dump(member_plates, f, indent=2)
        log(f"💾 Saved {len(member_plates)} member plates")
    except Exception as e:
        log(f"❌ Error saving members: {e}")

def load_blacklist():
    global blacklist_plates
    if os.path.exists(BLACKLIST_FILE):
        try:
            with open(BLACKLIST_FILE, 'r') as f:
                blacklist_plates = json.load(f)
            log(f"✅ Loaded {len(blacklist_plates)} blacklisted plates")
        except Exception as e:
            log(f"❌ Error loading blacklist: {e}")
            blacklist_plates = []
    else:
        blacklist_plates = []
        log("📝 No existing blacklist file - starting fresh")

def save_blacklist():
    try:
        with open(BLACKLIST_FILE, 'w') as f:
            json.dump(blacklist_plates, f, indent=2)
        log(f"💾 Saved {len(blacklist_plates)} blacklisted plates")
    except Exception as e:
        log(f"❌ Error saving blacklist: {e}")

def decode_jwt_payload(token):
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
        log(f"❌ JWT decode error: {e}")
        return None

def is_token_expired(token):
    payload = decode_jwt_payload(token)
    if not payload:
        return True
    exp = payload.get('exp')
    if not exp:
        return True
    current_time = time.time()
    return current_time >= (exp - 300)

def get_token_expiration_time(token):
    payload = decode_jwt_payload(token)
    if not payload:
        return None
    exp = payload.get('exp')
    if not exp:
        return None
    return datetime.fromtimestamp(exp)

def open_gate(lane_id, gate_name, site_id=None, visit_id=None):
    global AUTH_KEY
    site = site_id if site_id else SITE_ID
    endpoint = f"/api/specialist/site/{site}/lane/{lane_id}/open-gate"
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
        log(f"🚪 Opening gate: {gate_name} (Lane {lane_id}, Site {site})")
        response = requests.post(url, headers=headers, timeout=10)

        if response.status_code in [200, 201, 204]:
            log(f"✅ Gate {gate_name} opened successfully!")
            current_status["last_action"] = f"Opened {gate_name}"
            current_status["gates_opened"] += 1
            return True
        else:
            log(f"❌ Failed to open gate: Status {response.status_code}")
            return False
    except Exception as e:
        log(f"❌ Error opening gate: {e}")
        return False

def get_active_visits(site_id):
    global AUTH_KEY
    url = f"{BASE_URL}/api/specialist/site/{site_id}/visits/closed?count=50&minPaymentDueAgeSeconds=0&zoneIds={site_id}"
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
                return [t for t in transactions if 'VEND_GATE' in t.get('availableActionsForSpecialist', [])]
    except Exception as e:
        log(f"❌ Error getting visits: {e}")
    return None

def monitor_and_auto_open():
    """CONTINUOUS monitoring - runs FOREVER in background"""
    global monitoring_active, AUTH_KEY
    last_opened = {}
    cycle = 0

    log("🚀 MONITORING STARTED - Running continuously forever...")
    current_status["monitoring"] = "ACTIVE - Running 24/7"

    while True:  # ALWAYS runs - no condition check
        try:
            cycle += 1
            current_status["monitoring_cycles"] = cycle
            
            if cycle % 20 == 0:  # Log every 60 seconds (20 cycles * 3 sec)
                log(f"💓 Monitoring heartbeat - Cycle {cycle} - Members: {len(member_plates)}, Blacklist: {len(blacklist_plates)}")

            for site_id in ["4005", "4007"]:
                transactions = get_active_visits(site_id)

                if transactions:
                    for transaction in transactions:
                        vehicle = transaction.get('vehicle', {})
                        license_plate_obj = vehicle.get('licensePlate', {}) if vehicle else {}
                        plate = license_plate_obj.get('text', '').upper() if license_plate_obj else ''
                        visit_id = transaction.get('id')
                        
                        images = transaction.get('images', {})
                        exit_event = images.get('exitEvent') if images else None
                        site_equipment = exit_event.get('siteEquipment') if exit_event else None
                        lane_id = site_equipment.get('laneId') if site_equipment else None

                        # CHECK BLACKLIST FIRST
                        if plate and plate in [p.upper() for p in blacklist_plates]:
                            if visit_id and visit_id not in last_opened:
                                user = transaction.get('user', {})
                                user_name = f"{user.get('firstName', '')} {user.get('lastName', '')}".strip()
                                msg = f"🚫 BLOCKED: {plate} ({user_name}) - ON BLACKLIST!"
                                log(msg)
                                current_status["last_action"] = msg
                                current_status["vehicles_blocked"] += 1
                                last_opened[visit_id] = time.time()
                        
                        # Check if plate is in member list
                        elif plate and plate in [p.upper() for p in member_plates]:
                            if visit_id and visit_id not in last_opened:
                                user = transaction.get('user', {})
                                user_name = f"{user.get('firstName', '')} {user.get('lastName', '')}".strip()
                                msg = f"✅ AUTO-OPEN: {plate} ({user_name}) at site {site_id}"
                                log(msg)
                                current_status["last_action"] = msg

                                if lane_id:
                                    open_gate(str(lane_id), f"Auto Lane {lane_id}", site_id=site_id, visit_id=visit_id)
                                else:
                                    default_lane = "5568" if site_id == "4005" else "5565"
                                    open_gate(default_lane, "Default Gate", site_id=site_id, visit_id=visit_id)

                                last_opened[visit_id] = time.time()

                current_time = time.time()
                last_opened = {k: v for k, v in last_opened.items() if current_time - v < 600}

            time.sleep(3)  # Check every 3 seconds

        except Exception as e:
            log(f"❌ Monitor error: {e}")
            import traceback
            traceback.print_exc()
            time.sleep(5)

def refresh_token_headless():
    global AUTH_KEY

    if not HAS_SELENIUM:
        log("❌ Selenium not available - cannot refresh token")
        return None

    log("="*60)
    log("🔄 REFRESHING TOKEN (Headless Mode)")
    log("="*60)

    try:
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--log-level=3')

        driver = webdriver.Chrome(options=options)
        driver.get(LOGIN_URL)

        log("📱 Navigating to login page...")
        time.sleep(3)

        try:
            log("📧 Logging in...")
            email_field = driver.find_element(By.ID, "username")
            email_field.send_keys(EMAIL)
            time.sleep(1)

            password_field = driver.find_element(By.ID, "password")
            password_field.send_keys(PASSWORD)
            password_field.send_keys(Keys.RETURN)

            log("🔐 Waiting for authentication...")
            time.sleep(5)

        except Exception as e:
            log(f"⚠️ Login error: {e}")
            driver.quit()
            return None

        log("💉 Injecting token interceptor...")

        intercept_script = """
        window.capturedToken = null;

        const originalFetch = window.fetch;
        window.fetch = function(...args) {
            const [url, config] = args;

            if (config && config.headers) {
                const auth = config.headers['Authorization'] || config.headers['authorization'];
                if (auth && auth.startsWith('Bearer ')) {
                    window.capturedToken = auth.replace('Bearer ', '');
                    console.log('✅ Captured token from fetch!');
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
                console.log('✅ Captured token from XHR!');
            }

            return originalSetHeader.apply(this, arguments);
        };

        console.log('🎣 Token interceptor installed!');
        """

        driver.execute_script(intercept_script)
        log("✅ Interceptor installed!")

        log("⏳ Waiting for API call to capture token...")
        token = None

        for i in range(30):
            time.sleep(1)
            token = driver.execute_script("return window.capturedToken;")

            if token:
                log(f"✅ TOKEN CAPTURED! (after {i+1} seconds)")
                break

            if i == 5:
                log("   Refreshing page to trigger API calls...")
                driver.refresh()
                time.sleep(2)
                driver.execute_script(intercept_script)

        driver.quit()

        if token:
            log(f"✅ SUCCESS! Token refreshed!")
            log(f"Token preview: {token[:50]}...")
            AUTH_KEY = token

            with open('auth_token.txt', 'w') as f:
                f.write(token)

            log("="*60)
            current_status["last_action"] = "Token refreshed successfully"
            return token
        else:
            log("❌ No token captured after 30 seconds")
            log("="*60)
            return None

    except Exception as e:
        log(f"❌ Token refresh error: {e}")
        import traceback
        traceback.print_exc()
        try:
            driver.quit()
        except:
            pass
        return None

def token_monitor_loop():
    """CONTINUOUS token monitoring - runs FOREVER in background"""
    global token_monitor_active, AUTH_KEY
    check_count = 0

    log("🔐 TOKEN MONITOR STARTED - Running continuously forever...")
    current_status["token_monitor"] = "ACTIVE - Running 24/7"

    while True:  # ALWAYS runs - no condition check
        try:
            check_count += 1
            current_status["token_checks"] = check_count
            
            exp_time = get_token_expiration_time(AUTH_KEY)

            if exp_time:
                time_remaining = exp_time - datetime.now()
                hours = int(time_remaining.total_seconds() // 3600)
                minutes = int((time_remaining.total_seconds() % 3600) // 60)

                status_msg = f"Token expires in {hours}h {minutes}m (Check #{check_count})"
                log(f"🔐 {status_msg}")
                current_status["token_monitor"] = status_msg

                if is_token_expired(AUTH_KEY):
                    log("⚠️ TOKEN EXPIRED OR EXPIRING SOON - Auto-refreshing...")
                    current_status["last_action"] = "Refreshing token..."

                    new_token = refresh_token_headless()

                    if new_token:
                        AUTH_KEY = new_token
                        log("✅ Token successfully refreshed!")
                        current_status["last_action"] = "Token refreshed successfully"
                    else:
                        log("❌ Token refresh failed!")
                        current_status["last_action"] = "Token refresh failed"
            else:
                log("❌ Could not decode token")
                current_status["token_monitor"] = "Token decode error"

            time.sleep(180)  # Check every 3 minutes

        except Exception as e:
            log(f"❌ Token monitor error: {e}")
            import traceback
            traceback.print_exc()
            time.sleep(60)

def get_hanging_exits(site_id):
    global AUTH_KEY
    url = f"{BASE_URL}/api/specialist/site/{site_id}/event/hanging-exit/count"
    headers = {"Authorization": f"Bearer {AUTH_KEY}", "Accept": "*/*"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        log(f"❌ Error fetching hanging exits: {e}")
    return None

def get_closed_visits(site_id, count=25):
    global AUTH_KEY
    url = f"{BASE_URL}/api/specialist/site/{site_id}/visits/closed?count={count}&minPaymentDueAgeSeconds=180&zoneIds={site_id}"
    headers = {"Authorization": f"Bearer {AUTH_KEY}", "Accept": "*/*"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        log(f"❌ Error fetching closed visits: {e}")
    return None

def get_occupancy(site_id):
    global AUTH_KEY
    url = f"{BASE_URL}/api/site/{site_id}/occupancy"
    headers = {"Authorization": f"Bearer {AUTH_KEY}", "Accept": "*/*"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        log(f"❌ Error fetching occupancy: {e}")
    return None

def get_all_members(site_id):
    global AUTH_KEY
    url = f"{BASE_URL}/api/specialist/site/{site_id}/visits/closed?count=100&minPaymentDueAgeSeconds=0&zoneIds={site_id}"
    headers = {"Authorization": f"Bearer {AUTH_KEY}", "Accept": "*/*"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('data'):
                transactions = data['data'].get('transactions', [])
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
        log(f"❌ Error getting members: {e}")
    return []

# API Endpoints
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/status')
def status():
    exp_time = get_token_expiration_time(AUTH_KEY)
    token_status = "Unknown"
    if exp_time:
        time_remaining = exp_time - datetime.now()
        hours = int(time_remaining.total_seconds() // 3600)
        minutes = int((time_remaining.total_seconds() % 3600) // 60)
        token_status = f"{hours}h {minutes}m remaining"
        if is_token_expired(AUTH_KEY):
            token_status = "EXPIRED/EXPIRING SOON"
    
    return jsonify({
        "monitoring": current_status["monitoring"],
        "token_monitor": current_status["token_monitor"],
        "token_status": token_status,
        "last_action": current_status.get("last_action", "None"),
        "members_count": len(member_plates),
        "blacklist_count": len(blacklist_plates),
        "monitoring_cycles": current_status.get("monitoring_cycles", 0),
        "token_checks": current_status.get("token_checks", 0),
        "gates_opened": current_status.get("gates_opened", 0),
        "vehicles_blocked": current_status.get("vehicles_blocked", 0),
        "uptime": "RUNNING 24/7"
    })

@app.route('/health')
def health():
    """Health check endpoint for Render.com"""
    return jsonify({
        "status": "healthy",
        "monitoring": "ACTIVE",
        "token_monitor": "ACTIVE",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/open_gate', methods=['POST'])
def api_open_gate():
    data = request.json
    lane_id = data.get('lane_id')
    gate_name = data.get('gate_name')
    site_id = data.get('site_id', SITE_ID)
    
    result = open_gate(lane_id, gate_name, site_id=site_id)
    return jsonify({"success": result})

@app.route('/api/open_all_gates', methods=['POST'])
def api_open_all_gates():
    gates = [
        ("5568", "6th Street Exit", "4005"),
        ("5569", "L Street Exit", "4005"),
        ("5565", "Bank of America Exit", "4007"),
    ]
    for lane_id, name, site in gates:
        open_gate(lane_id, name, site_id=site)
    return jsonify({"success": True})

@app.route('/api/members')
def api_members():
    return jsonify({"members": member_plates})

@app.route('/api/members/add', methods=['POST'])
def api_add_member():
    plate = request.json.get('plate', '').strip().upper()
    if plate and plate not in member_plates:
        member_plates.append(plate)
        save_members()
        log(f"➕ Added member: {plate}")
        return jsonify({"success": True})
    return jsonify({"success": False})

@app.route('/api/members/remove', methods=['POST'])
def api_remove_member():
    plate = request.json.get('plate', '').strip().upper()
    if plate in member_plates:
        member_plates.remove(plate)
        save_members()
        log(f"➖ Removed member: {plate}")
        return jsonify({"success": True})
    return jsonify({"success": False})

@app.route('/api/blacklist')
def api_blacklist():
    return jsonify({"blacklist": blacklist_plates})

@app.route('/api/blacklist/add', methods=['POST'])
def api_add_blacklist():
    plate = request.json.get('plate', '').strip().upper()
    if plate and plate not in blacklist_plates:
        blacklist_plates.append(plate)
        save_blacklist()
        log(f"🚫 Added to blacklist: {plate}")
        return jsonify({"success": True})
    return jsonify({"success": False})

@app.route('/api/blacklist/remove', methods=['POST'])
def api_remove_blacklist():
    plate = request.json.get('plate', '').strip().upper()
    if plate in blacklist_plates:
        blacklist_plates.remove(plate)
        save_blacklist()
        log(f"✅ Removed from blacklist: {plate}")
        return jsonify({"success": True})
    return jsonify({"success": False})

@app.route('/api/waiting_cars')
def api_waiting_cars():
    results = {}
    for site_id in ["4005", "4007"]:
        data = get_hanging_exits(site_id)
        results[site_id] = data
    return jsonify(results)

@app.route('/api/visits')
def api_visits():
    results = {}
    for site_id in ["4005", "4007"]:
        data = get_closed_visits(site_id, count=10)
        results[site_id] = data
    return jsonify(results)

@app.route('/api/occupancy')
def api_occupancy():
    results = {}
    for site_id in ["4005", "4007"]:
        data = get_occupancy(site_id)
        results[site_id] = data
    return jsonify(results)

@app.route('/api/member_directory')
def api_member_directory():
    results = {}
    for site_id in ["4005", "4007"]:
        members = get_all_members(site_id)
        results[site_id] = members
    return jsonify(results)

@app.route('/api/refresh_token', methods=['POST'])
def api_refresh_token():
    new_token = refresh_token_headless()
    return jsonify({"success": new_token is not None})

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Metropolis Parking Management</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: Arial, sans-serif; 
            background: #1a1a1a; 
            color: white; 
            padding: 20px;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 10px;
        }
        .header h1 { font-size: 28px; margin-bottom: 10px; }
        .live-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            background: #4CAF50;
            border-radius: 50%;
            animation: pulse 2s infinite;
            margin-right: 8px;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.3; }
        }
        .status-bar {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        .status-item {
            padding: 15px;
            background: #2a2a2a;
            border-radius: 10px;
            font-size: 13px;
            border-left: 4px solid #4CAF50;
        }
        .status-item strong {
            display: block;
            font-size: 18px;
            margin-top: 5px;
            color: #4CAF50;
        }
        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        .tab {
            padding: 12px 20px;
            background: #2a2a2a;
            border: none;
            color: white;
            cursor: pointer;
            border-radius: 5px;
            font-size: 14px;
            transition: background 0.3s;
        }
        .tab:hover { background: #3a3a3a; }
        .tab.active { background: #1E88E5; }
        .tab-content {
            display: none;
            padding: 20px;
            background: #2a2a2a;
            border-radius: 10px;
        }
        .tab-content.active { display: block; }
        .btn {
            padding: 12px 24px;
            margin: 5px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            font-weight: bold;
            transition: transform 0.2s;
        }
        .btn:hover { transform: scale(1.05); }
        .btn-primary { background: #1E88E5; color: white; }
        .btn-success { background: #4CAF50; color: white; }
        .btn-danger { background: #F44336; color: white; }
        .gate-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        .gate-btn {
            padding: 20px;
            background: #1E88E5;
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
        }
        .gate-btn:hover {
            background: #1976D2;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(30,136,229,0.4);
        }
        .input-group {
            display: flex;
            gap: 10px;
            margin: 15px 0;
            align-items: center;
        }
        input[type="text"] {
            padding: 10px;
            border: 2px solid #3a3a3a;
            background: #1a1a1a;
            color: white;
            border-radius: 5px;
            font-size: 14px;
        }
        .list-box {
            background: #1a1a1a;
            border: 2px solid #3a3a3a;
            border-radius: 5px;
            padding: 15px;
            max-height: 400px;
            overflow-y: auto;
            margin: 15px 0;
        }
        .list-item {
            padding: 10px;
            margin: 5px 0;
            background: #2a2a2a;
            border-radius: 5px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .data-display {
            background: #1a1a1a;
            border: 2px solid #3a3a3a;
            border-radius: 5px;
            padding: 15px;
            max-height: 500px;
            overflow-y: auto;
            margin: 15px 0;
            font-family: 'Courier New', monospace;
            font-size: 12px;
            white-space: pre-wrap;
        }
        .alert {
            padding: 15px;
            margin: 15px 0;
            border-radius: 5px;
            font-weight: bold;
        }
        .alert-success { background: #4CAF50; }
        .alert-danger { background: #F44336; }
        .alert-info {
            background: #1E88E5;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }
        .card {
            background: #3a3a3a;
            border-radius: 10px;
            padding: 20px;
            margin: 15px 0;
        }
        @media (max-width: 768px) {
            .gate-grid { grid-template-columns: 1fr; }
            .tabs { flex-direction: column; }
            .status-bar { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚗 Metropolis Parking Management</h1>
        <p><span class="live-indicator"></span>Real-time Gate Control & Monitoring System</p>
        <p style="margin-top: 10px; font-size: 14px; opacity: 0.9;">🤖 Auto-Monitoring ALWAYS Active (24/7/365)</p>
    </div>

    <div class="status-bar" id="statusBar">
        <div class="status-item">⏰ Loading...</div>
    </div>

    <div class="alert-info">
        <strong>🚀 SYSTEM STATUS: ALWAYS RUNNING</strong><br>
        Background services are ALWAYS active - monitoring runs 24/7 regardless of website visitors. 
        The system continuously scans for member vehicles every 3 seconds and checks token expiration every 3 minutes.
    </div>

    <div class="tabs">
        <button class="tab active" onclick="showTab('gates')">Gate Controls</button>
        <button class="tab" onclick="showTab('members')">Members</button>
        <button class="tab" onclick="showTab('blacklist')">Blacklist</button>
        <button class="tab" onclick="showTab('waiting')">Waiting Cars</button>
        <button class="tab" onclick="showTab('visits')">Recent Visits</button>
        <button class="tab" onclick="showTab('occupancy')">Occupancy</button>
        <button class="tab" onclick="showTab('directory')">Directory</button>
        <button class="tab" onclick="showTab('emergency')">Emergency</button>
    </div>

    <div id="gates" class="tab-content active">
        <h2>🚧 Gate Controls</h2>
        <div class="gate-grid">
            <button class="gate-btn" onclick="openGate('5568', '6th Street Exit', '4005')">
                Open 6th Street Exit<br><small>(Site 4005)</small>
            </button>
            <button class="gate-btn" onclick="openGate('5569', 'L Street Exit', '4005')">
                Open L Street Exit<br><small>(Site 4005)</small>
            </button>
            <button class="gate-btn" onclick="openGate('5565', 'Bank of America Exit', '4007')">
                Open Bank of America Exit<br><small>(Site 4007)</small>
            </button>
        </div>
    </div>

    <div id="members" class="tab-content">
        <h2>👥 Member Management</h2>
        <div class="alert-info">
            Members are automatically detected and gates open without any action needed.
        </div>
        <div class="input-group">
            <label>License Plate:</label>
            <input type="text" id="memberPlate" placeholder="ABC123">
            <button class="btn btn-success" onclick="addMember()">Add Member</button>
        </div>
        <div class="list-box" id="membersList"></div>
    </div>

    <div id="blacklist" class="tab-content">
        <h2>🚫 Blacklist Management</h2>
        <div class="alert alert-danger">
            ⚠️ Blacklisted vehicles will be BLOCKED even if they're members
        </div>
        <div class="input-group">
            <label>License Plate:</label>
            <input type="text" id="blacklistPlate" placeholder="ABC123">
            <button class="btn btn-danger" onclick="addToBlacklist()">Add to Blacklist</button>
        </div>
        <div class="list-box" id="blacklistList"></div>
    </div>

    <div id="waiting" class="tab-content">
        <h2>🚗 Cars Waiting at Exit</h2>
        <button class="btn btn-primary" onclick="loadWaitingCars()">Refresh</button>
        <div class="data-display" id="waitingData">Click Refresh to load data...</div>
    </div>

    <div id="visits" class="tab-content">
        <h2>📋 Recent Visits</h2>
        <button class="btn btn-primary" onclick="loadVisits()">Refresh</button>
        <div class="data-display" id="visitsData">Click Refresh to load data...</div>
    </div>

    <div id="occupancy" class="tab-content">
        <h2>📊 Garage Occupancy</h2>
        <button class="btn btn-primary" onclick="loadOccupancy()">Refresh</button>
        <div class="data-display" id="occupancyData">Click Refresh to load data...</div>
    </div>

    <div id="directory" class="tab-content">
        <h2>📖 Member Directory</h2>
        <button class="btn btn-primary" onclick="loadDirectory()">Refresh</button>
        <div class="data-display" id="directoryData">Click Refresh to load data...</div>
    </div>

    <div id="emergency" class="tab-content">
        <h2>🚨 Emergency Controls</h2>
        <div class="alert alert-danger">
            ⚠️ WARNING: This will open ALL gates at ALL sites simultaneously
        </div>
        <button class="btn btn-danger" onclick="openAllGates()" style="width: 100%; padding: 30px; font-size: 20px; margin: 20px 0;">
            🚨 OPEN ALL GATES 🚨
        </button>
    </div>

    <script>
        function showTab(tabName) {
            document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
        }

        async function updateStatus() {
            try {
                const res = await fetch('/api/status');
                const data = await res.json();
                document.getElementById('statusBar').innerHTML = `
                    <div class="status-item">
                        <span>🤖 Monitoring</span>
                        <strong>${data.monitoring}</strong>
                    </div>
                    <div class="status-item">
                        <span>🔐 Token Monitor</span>
                        <strong>${data.token_monitor}</strong>
                    </div>
                    <div class="status-item">
                        <span>⏰ Token Status</span>
                        <strong>${data.token_status}</strong>
                    </div>
                    <div class="status-item">
                        <span>👥 Members</span>
                        <strong>${data.members_count}</strong>
                    </div>
                    <div class="status-item">
                        <span>🚫 Blacklist</span>
                        <strong>${data.blacklist_count}</strong>
                    </div>
                    <div class="status-item">
                        <span>🔄 Monitor Cycles</span>
                        <strong>${data.monitoring_cycles}</strong>
                    </div>
                    <div class="status-item">
                        <span>🔐 Token Checks</span>
                        <strong>${data.token_checks}</strong>
                    </div>
                    <div class="status-item">
                        <span>🚪 Gates Opened</span>
                        <strong>${data.gates_opened}</strong>
                    </div>
                    <div class="status-item">
                        <span>🚫 Vehicles Blocked</span>
                        <strong>${data.vehicles_blocked}</strong>
                    </div>
                    <div class="status-item" style="grid-column: 1 / -1;">
                        <span>📝 Last Action</span>
                        <strong>${data.last_action}</strong>
                    </div>
                `;
            } catch (e) {
                console.error('Status update failed:', e);
            }
        }

        async function openGate(laneId, gateName, siteId) {
            const res = await fetch('/api/open_gate', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({lane_id: laneId, gate_name: gateName, site_id: siteId})
            });
            const data = await res.json();
            alert(data.success ? `${gateName} opened!` : 'Failed to open gate');
            updateStatus();
        }

        async function openAllGates() {
            if (!confirm('Open ALL gates at BOTH sites?')) return;
            await fetch('/api/open_all_gates', {method: 'POST'});
            alert('All gates opened!');
            updateStatus();
        }

        async function loadMembers() {
            const res = await fetch('/api/members');
            const data = await res.json();
            const html = data.members.map(p => `
                <div class="list-item">
                    <span>${p}</span>
                    <button class="btn btn-danger" onclick="removeMember('${p}')">Remove</button>
                </div>
            `).join('');
            document.getElementById('membersList').innerHTML = html || '<p>No members</p>';
        }

        async function addMember() {
            const plate = document.getElementById('memberPlate').value.trim().toUpperCase();
            if (!plate) return alert('Enter a plate');
            await fetch('/api/members/add', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({plate})
            });
            document.getElementById('memberPlate').value = '';
            loadMembers();
            updateStatus();
        }

        async function removeMember(plate) {
            await fetch('/api/members/remove', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({plate})
            });
            loadMembers();
            updateStatus();
        }

        async function loadBlacklist() {
            const res = await fetch('/api/blacklist');
            const data = await res.json();
            const html = data.blacklist.map(p => `
                <div class="list-item" style="background: #4a2a2a;">
                    <span style="color: #F44336; font-weight: bold;">${p}</span>
                    <button class="btn btn-success" onclick="removeFromBlacklist('${p}')">Remove</button>
                </div>
            `).join('');
            document.getElementById('blacklistList').innerHTML = html || '<p>No blacklisted plates</p>';
        }

        async function addToBlacklist() {
            const plate = document.getElementById('blacklistPlate').value.trim().toUpperCase();
            if (!plate) return alert('Enter a plate');
            if (!confirm(`Add ${plate} to blacklist? This vehicle will be auto-denied!`)) return;
            await fetch('/api/blacklist/add', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({plate})
            });
            document.getElementById('blacklistPlate').value = '';
            loadBlacklist();
            updateStatus();
        }

        async function removeFromBlacklist(plate) {
            await fetch('/api/blacklist/remove', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({plate})
            });
            loadBlacklist();
            updateStatus();
        }

        async function loadWaitingCars() {
            document.getElementById('waitingData').innerHTML = 'Loading...';
            const res = await fetch('/api/waiting_cars');
            const data = await res.json();
            document.getElementById('waitingData').innerHTML = JSON.stringify(data, null, 2);
        }

        async function loadVisits() {
            document.getElementById('visitsData').innerHTML = 'Loading...';
            const res = await fetch('/api/visits');
            const data = await res.json();
            document.getElementById('visitsData').innerHTML = JSON.stringify(data, null, 2);
        }

        async function loadOccupancy() {
            document.getElementById('occupancyData').innerHTML = 'Loading...';
            const res = await fetch('/api/occupancy');
            const data = await res.json();
            document.getElementById('occupancyData').innerHTML = JSON.stringify(data, null, 2);
        }

        async function loadDirectory() {
            document.getElementById('directoryData').innerHTML = 'Loading...';
            const res = await fetch('/api/member_directory');
            const data = await res.json();
            let output = '';
            for (const [siteId, members] of Object.entries(data)) {
                const siteName = siteId === '4005' ? '555 Capitol Mall' : 'Bank of America';
                output += `\n${'='.repeat(80)}\n${siteName} (Site ${siteId}) - ${members.length} Members\n${'='.repeat(80)}\n\n`;
                members.forEach((m, i) => {
                    const user = m.user;
                    const vehicle = m.vehicle;
                    const plate = vehicle.licensePlate?.text || 'N/A';
                    const state = vehicle.licensePlate?.state?.name || '';
                    const make = vehicle.make?.name || 'Unknown';
                    const model = vehicle.model?.name || 'Unknown';
                    const color = vehicle.color || 'Unknown';
                    const name = `${user.firstName || ''} ${user.lastName || ''}`.trim();
                    output += `[${i+1}] ${name}\n    Phone: ${user.phoneNumber || 'N/A'}\n    Vehicle: ${color} ${make} ${model}\n    Plate: ${plate} (${state})\n\n`;
                });
            }
            document.getElementById('directoryData').innerHTML = output || 'No members found';
        }

        // Auto-update status every 3 seconds for real-time monitoring
        setInterval(updateStatus, 3000);
        
        // Initial load
        updateStatus();
        loadMembers();
        loadBlacklist();
    </script>
</body>
</html>
'''

def start_background_services():
    """Start all background services immediately on server startup"""
    global monitoring_thread, token_monitor_thread
    
    log("\n" + "="*80)
    log("🚀 STARTING BACKGROUND SERVICES (24/7 MODE)")
    log("="*80)
    
    # Start member/blacklist monitoring thread
    monitoring_thread = threading.Thread(target=monitor_and_auto_open, daemon=True, name="MonitoringThread")
    monitoring_thread.start()
    log("✅ Vehicle monitoring thread started (runs every 3 seconds)")
    
    # Start token monitoring thread
    if HAS_SELENIUM:
        token_monitor_thread = threading.Thread(target=token_monitor_loop, daemon=True, name="TokenMonitorThread")
        token_monitor_thread.start()
        log("✅ Token monitoring thread started (checks every 3 minutes)")
    else:
        log("⚠️  Selenium not available - token auto-refresh disabled")
        log("   (Token will need to be manually updated)")
    
    log("="*80)
    log("✅ ALL BACKGROUND SERVICES RUNNING")
    log("   - These services run CONTINUOUSLY 24/7")
    log("   - No user interaction required")
    log("   - Monitoring happens even with 0 website visitors")
    log("="*80 + "\n")

# Ensure threads are daemon so they don't prevent shutdown
def cleanup():
    log("🛑 Server shutting down - background threads will terminate")

atexit.register(cleanup)

if __name__ == '__main__':
    log("\n" + "="*80)
    log("METROPOLIS PARKING MANAGEMENT SYSTEM - WEB VERSION")
    log("="*80)
    log(f"Auth Key: {AUTH_KEY[:50]}...")
    log(f"Sites: 4005 (555 Capitol Mall), 4007 (Bank of America)")
    log("="*80 + "\n")
    
    # Load persistent data
    load_members()
    load_blacklist()
    
    # Start background services IMMEDIATELY
    start_background_services()
    
    # Small delay to let threads initialize
    time.sleep(2)
    
    log("\n🌐 Starting Flask web server...")
    log("   Web interface available for viewing status and manual controls")
    log("   Background monitoring runs independently of web traffic\n")
    
    # Run Flask app
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
