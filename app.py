#!/usr/bin/env python3
from flask import Flask, render_template_string, jsonify, request
import requests
import time
import threading
import logging
import json

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# --- Configuration ---
EMAIL = "security@555capitolmall.com"
PASSWORD = "555_Security"
TOKEN_URL = "https://auth.metropolis.io/realms/metropolis/protocol/openid-connect/token"
API_BASE_URL = "https://specialist.api.metropolis.io/api/specialist"
CLIENT_ID = "metropolis-web-client"

# Preset Gates
GATES_CONFIG = [
    {"id": "5568", "name": "6th Street Exit", "site_id": "4005"},
    {"id": "5569", "name": "L Street Exit", "site_id": "4005"},
    {"id": "5565", "name": "Bank of America Exit", "site_id": "4007"},
]

# Global State
access_token = None
refresh_token = None
token_expiry_time = 0
token_lock = threading.Lock()

# Scanner State
scan_active = False
scan_logs = []
found_gates = []
scan_thread = None

# --- Auth Functions ---
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
        logging.error(f"Failed to get token: {e}")
        return False

def refresh_tokens():
    global access_token, refresh_token, token_expiry_time
    if not refresh_token:
        return get_new_tokens()
    
    payload = {
        'client_id': CLIENT_ID,
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token
    }
    try:
        response = requests.post(TOKEN_URL, data=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        with token_lock:
            access_token = data.get('access_token')
            token_expiry_time = time.time() + data.get('expires_in', 3600) - 60
            refresh_token = data.get('refresh_token', refresh_token)
        return True
    except Exception:
        return get_new_tokens()

def token_refresh_loop():
    if not get_new_tokens():
        logging.error("Could not get initial token")
    while True:
        if time.time() >= token_expiry_time:
            refresh_tokens()
        time.sleep(10)

threading.Thread(target=token_refresh_loop, daemon=True).start()

# --- Scanner Logic (Background Thread) ---
def run_scanner(site_id, start_id, end_id):
    global scan_active, scan_logs, found_gates
    scan_active = True
    scan_logs.append(f"Starting scan on Site {site_id} from {start_id} to {end_id}...")
    
    for lane_id in range(start_id, end_id + 1):
        if not scan_active:
            break
            
        with token_lock:
            current_token = access_token
            
        url = f"{API_BASE_URL}/site/{site_id}/lane/{lane_id}/open-gate"
        headers = {'Authorization': f'Bearer {current_token}', 'Content-Type': 'application/json'}
        
        try:
            resp = requests.post(url, headers=headers, timeout=3)
            
            # PARSE JSON TO CHECK SUCCESS
            try:
                data = resp.json()
                is_success = data.get('success') is True
            except:
                is_success = False

            if is_success:
                msg = f"✅ FOUND & OPENED: {lane_id}"
                scan_logs.append(msg)
                found_gates.append(lane_id)
            elif resp.status_code == 401:
                scan_logs.append("❌ Token Expired. Refreshing...")
                refresh_tokens()
            else:
                # If status is 200 but success is False, or 404
                pass 
                
        except Exception as e:
            pass 
            
        if lane_id % 10 == 0:
            scan_logs.append(f"Scanning... currently at {lane_id}")
            
        time.sleep(0.1)
        
    scan_logs.append("🎉 Scan Complete.")
    scan_active = False

# --- HTML Template ---
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Metropolis Master Control</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #2d3436; color: white; margin: 0; padding: 20px; }
        .container { max-width: 800px; margin: 0 auto; background: #1e272e; border-radius: 15px; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
        .header { background: #0984e3; padding: 20px; text-align: center; }
        .tabs { display: flex; background: #2d3436; border-bottom: 1px solid #636e72; }
        .tab { flex: 1; padding: 15px; text-align: center; cursor: pointer; background: #2d3436; transition: 0.3s; }
        .tab:hover { background: #353b48; }
        .tab.active { background: #1e272e; border-top: 3px solid #0984e3; font-weight: bold; }
        .content { padding: 30px; display: none; }
        .content.active { display: block; }
        
        .btn { width: 100%; padding: 15px; margin: 10px 0; border: none; border-radius: 8px; font-size: 1.1rem; cursor: pointer; color: white; transition: 0.2s; }
        .btn-gate { background: #00b894; }
        .btn-gate:hover { background: #00a884; }
        .btn-scan { background: #e17055; }
        .btn-stop { background: #d63031; }
        
        .log-window { background: #000; height: 300px; overflow-y: scroll; padding: 10px; font-family: monospace; border: 1px solid #636e72; margin-top: 15px; color: #00cec9; }
        .log-entry { margin-bottom: 5px; border-bottom: 1px solid #333; }
        
        .input-row { display: flex; gap: 10px; margin-bottom: 15px; }
        input { flex: 1; padding: 10px; border-radius: 5px; border: 1px solid #636e72; background: #353b48; color: white; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header"><h1>🚪 Gate Master</h1></div>
        <div class="tabs">
            <div class="tab active" onclick="setTab(0)">Control</div>
            <div class="tab" onclick="setTab(1)">Scanner</div>
        </div>

        <div class="content active" id="tab-0">
            <h3>Preset Gates</h3>
            {% for gate in gates %}
            <button class="btn btn-gate" onclick="openGate('{{gate.id}}', '{{gate.name}}', '{{gate.site_id}}')">
                Open {{ gate.name }}
            </button>
            {% endfor %}
            
            <h3 style="margin-top: 30px; border-top: 1px solid #444; padding-top: 20px;">Manual Override</h3>
            <div class="input-row">
                <input id="m-site" placeholder="Site ID">
                <input id="m-lane" placeholder="Lane ID">
            </div>
            <button class="btn" style="background: #6c5ce7;" onclick="manualOpen()">Execute Open Command</button>
            <div id="status" style="margin-top: 10px; text-align: center; color: #fab1a0;"></div>
        </div>

        <div class="content" id="tab-1">
            <h3>Range Scanner (4006)</h3>
            <div class="input-row">
                <input id="scan-site" value="4006" placeholder="Site ID">
                <input id="scan-start" value="5500" placeholder="Start ID">
                <input id="scan-end" value="6000" placeholder="End ID">
            </div>
            <div class="input-row">
                <button class="btn btn-scan" onclick="startScan()">Start Scan</button>
                <button class="btn btn-stop" onclick="stopScan()">Stop</button>
            </div>
            <div class="log-window" id="scan-logs">Waiting to start...</div>
        </div>
    </div>

    <script>
        function setTab(idx) {
            document.querySelectorAll('.tab').forEach((t, i) => t.classList.toggle('active', i===idx));
            document.querySelectorAll('.content').forEach((c, i) => c.classList.toggle('active', i===idx));
        }

        async function openGate(lane, name, site) {
            document.getElementById('status').innerText = "Sending command...";
            try {
                const res = await fetch('/api/open', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({lane_id: lane, site_id: site})
                });
                const data = await res.json();
                
                if (data.success) {
                    document.getElementById('status').innerText = "Success! Gate Open.";
                    document.getElementById('status').style.color = "#55efc4";
                } else {
                    document.getElementById('status').innerText = "Failed: " + (data.message || "Unknown error");
                    document.getElementById('status').style.color = "#ff7675";
                }
            } catch(e) { 
                document.getElementById('status').innerText = "Network Error"; 
            }
        }

        function manualOpen() {
            openGate(document.getElementById('m-lane').value, 'Manual', document.getElementById('m-site').value);
        }

        async function startScan() {
            const site = document.getElementById('scan-site').value;
            const start = document.getElementById('scan-start').value;
            const end = document.getElementById('scan-end').value;
            await fetch('/api/scan/start', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({site, start, end})
            });
        }

        async function stopScan() {
            await fetch('/api/scan/stop', {method: 'POST'});
        }

        setInterval(async () => {
            if(document.getElementById('tab-1').classList.contains('active')) {
                const res = await fetch('/api/scan/logs');
                const data = await res.json();
                const logDiv = document.getElementById('scan-logs');
                logDiv.innerHTML = data.logs.map(l => `<div class="log-entry">${l}</div>`).join('');
                if(data.active) logDiv.scrollTop = logDiv.scrollHeight;
            }
        }, 1000);
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
    url = f"{API_BASE_URL}/site/{data['site_id']}/lane/{data['lane_id']}/open-gate"
    headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'}
    
    try:
        r = requests.post(url, headers=headers, timeout=10)
        
        # Parse JSON safely
        try:
            api_resp = r.json()
            is_success = api_resp.get('success') is True
            msg = api_resp.get('message', '')
        except:
            api_resp = {}
            is_success = False
            msg = "Could not parse server response"

        # Return simplified status to frontend
        return jsonify({
            'success': is_success, 
            'message': msg,
            'raw': api_resp
        })

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/scan/start', methods=['POST'])
def start_scan_route():
    global scan_thread, scan_logs, found_gates
    data = request.json
    scan_logs = ["Initializing scan..."]
    found_gates = []
    
    scan_thread = threading.Thread(
        target=run_scanner, 
        args=(data['site'], int(data['start']), int(data['end']))
    )
    scan_thread.start()
    return jsonify({'success': True})

@app.route('/api/scan/stop', methods=['POST'])
def stop_scan_route():
    global scan_active
    scan_active = False
    return jsonify({'success': True})

@app.route('/api/scan/logs')
def get_logs():
    return jsonify({'logs': scan_logs, 'active': scan_active, 'found': found_gates})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
