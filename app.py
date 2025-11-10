#!/usr/bin/env python3
from flask import Flask, render_template_string, jsonify, request
import requests
import time
import threading
import logging
from datetime import datetime

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# --- Configuration ---
EMAIL = "security@555capitolmall.com"
PASSWORD = "555_Security"
TOKEN_URL = "https://auth.metropolis.io/realms/metropolis/protocol/openid-connect/token"
API_BASE_URL = "https://specialist.api.metropolis.io/api/specialist"
CLIENT_ID = "metropolis-web-client"

GATES_CONFIG = [
    {"id": "5568", "name": "6th Street Exit", "site_id": "4005"},
    {"id": "5569", "name": "L Street Exit", "site_id": "4005"},
    {"id": "5565", "name": "Bank of America Exit", "site_id": "4007"},
]

# Global token management
access_token = None
refresh_token = None
token_expiry_time = 0
token_lock = threading.Lock()

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
        logging.info("Token acquired successfully")
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
        logging.info("Token refreshed successfully")
        return True
    except Exception as e:
        logging.error(f"Token refresh failed: {e}")
        return get_new_tokens()

def token_refresh_loop():
    """Continuously refresh tokens in background, even when no one is using the site"""
    if not get_new_tokens():
        logging.error("Could not get initial token")
    
    while True:
        try:
            # Check if token is expired or about to expire
            if time.time() >= token_expiry_time:
                logging.info("Token expired or expiring soon, refreshing...")
                refresh_tokens()
            time.sleep(10)  # Check every 10 seconds
        except Exception as e:
            logging.error(f"Error in token refresh loop: {e}")
            time.sleep(30)  # Wait longer on error before retrying

# Start token refresh thread
threading.Thread(target=token_refresh_loop, daemon=True).start()

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Metropolis Control Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }

        .container {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            max-width: 800px;
            width: 100%;
            overflow: hidden;
        }

        .header {
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }

        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
            font-weight: 600;
        }

        .header .subtitle {
            opacity: 0.9;
            font-size: 1.1rem;
        }

        .tabs {
            display: flex;
            background: #f8f9fa;
            border-bottom: 2px solid #e9ecef;
        }

        .tab {
            flex: 1;
            padding: 20px;
            text-align: center;
            cursor: pointer;
            font-weight: 600;
            font-size: 1.1rem;
            color: #6c757d;
            transition: all 0.3s ease;
            border-bottom: 3px solid transparent;
        }

        .tab:hover {
            background: #e9ecef;
            color: #495057;
        }

        .tab.active {
            color: #667eea;
            background: white;
            border-bottom: 3px solid #667eea;
        }

        .tab-content {
            display: none;
            padding: 40px;
            animation: fadeIn 0.5s ease;
        }

        .tab-content.active {
            display: block;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .gate-button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 20px 30px;
            margin: 15px 0;
            border-radius: 12px;
            font-size: 1.2rem;
            font-weight: 600;
            cursor: pointer;
            width: 100%;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }

        .gate-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
        }

        .gate-button:active {
            transform: translateY(0);
        }

        .gate-button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }

        .clock {
            font-size: 3rem;
            font-weight: 700;
            color: #667eea;
            text-align: center;
            margin: 20px 0;
            font-family: 'Courier New', monospace;
        }

        /* Watch Design */
        .watch-container {
            display: flex;
            justify-content: center;
            align-items: center;
            margin: 30px 0;
        }

        .watch {
            position: relative;
            width: 250px;
            height: 250px;
            border-radius: 50%;
            background: linear-gradient(145deg, #ffffff, #e6e6e6);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2),
                        inset 0 -5px 10px rgba(0, 0, 0, 0.1);
            border: 8px solid #333;
            transition: all 0.5s ease;
        }

        .watch.expired {
            border-color: #dc3545;
            box-shadow: 0 10px 30px rgba(220, 53, 69, 0.5),
                        inset 0 -5px 10px rgba(220, 53, 69, 0.3);
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.05); }
        }

        .watch-face {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 90%;
            height: 90%;
            border-radius: 50%;
            background: white;
            box-shadow: inset 0 2px 10px rgba(0, 0, 0, 0.1);
        }

        .watch-center {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 20px;
            height: 20px;
            background: #333;
            border-radius: 50%;
            z-index: 10;
        }

        .watch-hand {
            position: absolute;
            bottom: 50%;
            left: 50%;
            transform-origin: bottom center;
            background: #333;
            border-radius: 10px;
        }

        .hour-hand {
            width: 6px;
            height: 60px;
            margin-left: -3px;
            background: #333;
        }

        .minute-hand {
            width: 4px;
            height: 80px;
            margin-left: -2px;
            background: #555;
        }

        .watch-mark {
            position: absolute;
            width: 2px;
            height: 10px;
            background: #333;
            left: 50%;
            margin-left: -1px;
            top: 5px;
            transform-origin: center 107px;
        }

        .watch-number {
            position: absolute;
            font-size: 14px;
            font-weight: bold;
            color: #333;
        }

        .watch-label {
            text-align: center;
            margin-top: 20px;
            font-size: 1.2rem;
            font-weight: 600;
            color: #495057;
            transition: color 0.3s ease;
        }

        .watch-label.expired {
            color: #dc3545;
            animation: blink 1s infinite;
        }

        @keyframes blink {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }

        .watch-time {
            font-size: 1.4rem;
            margin-top: 5px;
            color: #667eea;
        }

        .watch-time.expired {
            color: #dc3545;
            font-weight: bold;
        }

        /* Expired Token Modal */
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.7);
            z-index: 1000;
            animation: fadeIn 0.3s ease;
        }

        .modal.show {
            display: flex;
            justify-content: center;
            align-items: center;
        }

        .modal-content {
            background: white;
            padding: 40px;
            border-radius: 20px;
            text-align: center;
            max-width: 500px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
            animation: slideDown 0.3s ease;
        }

        @keyframes slideDown {
            from { transform: translateY(-50px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }

        .modal-icon {
            font-size: 5rem;
            margin-bottom: 20px;
            animation: shake 0.5s ease;
        }

        @keyframes shake {
            0%, 100% { transform: translateX(0); }
            25% { transform: translateX(-10px); }
            75% { transform: translateX(10px); }
        }

        .modal-title {
            font-size: 2rem;
            color: #dc3545;
            margin-bottom: 15px;
            font-weight: 700;
        }

        .modal-message {
            font-size: 1.2rem;
            color: #495057;
            margin-bottom: 30px;
            line-height: 1.6;
        }

        .modal-button {
            background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
            color: white;
            border: none;
            padding: 18px 40px;
            border-radius: 12px;
            font-size: 1.3rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(220, 53, 69, 0.4);
        }

        .modal-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(220, 53, 69, 0.6);
        }

        .info-card {
            background: #f8f9fa;
            border-radius: 12px;
            padding: 20px;
            margin: 20px 0;
            border-left: 4px solid #667eea;
        }

        .info-card h3 {
            color: #495057;
            margin-bottom: 10px;
            font-size: 1rem;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .info-card p {
            color: #212529;
            font-size: 1.1rem;
            font-weight: 600;
        }

        .refresh-button {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 12px;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            width: 100%;
            margin-top: 20px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(245, 87, 108, 0.4);
        }

        .refresh-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(245, 87, 108, 0.6);
        }

        .status-bar {
            background: #212529;
            color: white;
            padding: 15px 30px;
            text-align: center;
            font-size: 0.95rem;
            animation: slideUp 0.5s ease;
        }

        @keyframes slideUp {
            from { transform: translateY(100%); }
            to { transform: translateY(0); }
        }

        .status-bar.success {
            background: #28a745;
        }

        .status-bar.error {
            background: #dc3545;
        }

        @media (max-width: 600px) {
            .header h1 {
                font-size: 1.8rem;
            }
            
            .clock {
                font-size: 2rem;
            }
            
            .tab {
                font-size: 0.9rem;
                padding: 15px 10px;
            }

            .watch {
                width: 200px;
                height: 200px;
            }

            .modal-content {
                margin: 20px;
                padding: 30px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚪 Metropolis Control</h1>
            <p class="subtitle">Gate Management Dashboard</p>
        </div>

        <div class="tabs">
            <div class="tab active" onclick="switchTab(0)">Gate Control</div>
            <div class="tab" onclick="switchTab(1)">System Status</div>
        </div>

        <div class="tab-content active" id="gate-control">
            <h2 style="margin-bottom: 30px; color: #495057;">Gate Operations</h2>
            {% for gate in gates %}
            <button class="gate-button" onclick="openGate('{{ gate.id }}', '{{ gate.name }}', '{{ gate.site_id }}')">
                🚗 Open {{ gate.name }}
            </button>
            {% endfor %}
        </div>

        <div class="tab-content" id="system-status">
            <h2 style="margin-bottom: 20px; color: #495057; text-align: center;">System Status</h2>
            <div class="clock" id="clock">00:00:00</div>
            
            <div class="watch-container">
                <div>
                    <div class="watch" id="token-watch">
                        <div class="watch-face">
                            <div class="watch-hand hour-hand" id="hour-hand"></div>
                            <div class="watch-hand minute-hand" id="minute-hand"></div>
                            <div class="watch-center"></div>
                        </div>
                    </div>
                    <div class="watch-label" id="watch-label">
                        Token Expires At
                        <div class="watch-time" id="watch-time">Loading...</div>
                    </div>
                </div>
            </div>
            
            <button class="refresh-button" onclick="manualRefresh()">
                🔄 Manual Token Refresh
            </button>
        </div>

        <div class="status-bar" id="status-bar">
            Ready
        </div>
    </div>

    <!-- Expired Token Modal -->
    <div class="modal" id="expired-modal">
        <div class="modal-content">
            <div class="modal-icon">⚠️</div>
            <div class="modal-title">Token Expired!</div>
            <div class="modal-message">
                Your access token has expired.<br>
                Please refresh to continue using the exit doors.
            </div>
            <button class="modal-button" onclick="refreshFromModal()">
                🔄 Click to Refresh Token
            </button>
        </div>
    </div>

    <script>
        let currentTab = 0;
        let tokenExpired = false;

        function switchTab(index) {
            const tabs = document.querySelectorAll('.tab');
            const contents = document.querySelectorAll('.tab-content');
            
            tabs.forEach((tab, i) => {
                if (i === index) {
                    tab.classList.add('active');
                    contents[i].classList.add('active');
                } else {
                    tab.classList.remove('active');
                    contents[i].classList.remove('active');
                }
            });
            currentTab = index;
        }

        function updateClock() {
            const now = new Date();
            const hours = String(now.getHours()).padStart(2, '0');
            const minutes = String(now.getMinutes()).padStart(2, '0');
            const seconds = String(now.getSeconds()).padStart(2, '0');
            document.getElementById('clock').textContent = `${hours}:${minutes}:${seconds}`;
        }

        function updateWatchHands(expiryDate) {
            const hours = expiryDate.getHours() % 12;
            const minutes = expiryDate.getMinutes();
            
            const hourDegrees = (hours * 30) + (minutes * 0.5);
            const minuteDegrees = minutes * 6;
            
            document.getElementById('hour-hand').style.transform = `rotate(${hourDegrees}deg)`;
            document.getElementById('minute-hand').style.transform = `rotate(${minuteDegrees}deg)`;
        }

        function updateStatus(message, type = 'info') {
            const statusBar = document.getElementById('status-bar');
            statusBar.textContent = message;
            statusBar.className = 'status-bar';
            if (type === 'success') {
                statusBar.classList.add('success');
            } else if (type === 'error') {
                statusBar.classList.add('error');
            }
        }

        function showExpiredModal() {
            document.getElementById('expired-modal').classList.add('show');
        }

        function hideExpiredModal() {
            document.getElementById('expired-modal').classList.remove('show');
        }

        async function refreshFromModal() {
            hideExpiredModal();
            await manualRefresh();
        }

        async function openGate(laneId, laneName, siteId) {
            if (tokenExpired) {
                showExpiredModal();
                return;
            }

            const button = event.target;
            button.disabled = true;
            updateStatus(`Opening ${laneName}...`);
            
            try {
                const response = await fetch('/api/open-gate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        lane_id: laneId,
                        lane_name: laneName,
                        site_id: siteId
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    updateStatus(`✓ ${laneName} opened successfully!`, 'success');
                } else {
                    updateStatus(`✗ Failed to open ${laneName}: ${data.error}`, 'error');
                }
            } catch (error) {
                updateStatus(`✗ Network error: ${error.message}`, 'error');
            } finally {
                button.disabled = false;
            }
        }

        async function manualRefresh() {
            updateStatus('Refreshing token...');
            try {
                const response = await fetch('/api/refresh-token', {
                    method: 'POST'
                });
                const data = await response.json();
                
                if (data.success) {
                    updateStatus('✓ Token refreshed successfully!', 'success');
                    tokenExpired = false;
                    updateTokenInfo();
                } else {
                    updateStatus('✗ Token refresh failed', 'error');
                }
            } catch (error) {
                updateStatus(`✗ Error: ${error.message}`, 'error');
            }
        }

        async function updateTokenInfo() {
            try {
                const response = await fetch('/api/token-status');
                const data = await response.json();
                
                if (data.expiry_time) {
                    const expiryDate = new Date(data.expiry_time * 1000);
                    const now = new Date();
                    
                    // Check if token is expired
                    if (now >= expiryDate) {
                        tokenExpired = true;
                        document.getElementById('token-watch').classList.add('expired');
                        document.getElementById('watch-label').classList.add('expired');
                        document.getElementById('watch-time').classList.add('expired');
                        document.getElementById('watch-label').innerHTML = 'TOKEN EXPIRED!<br><div class="watch-time expired">Refresh Required</div>';
                        showExpiredModal();
                    } else {
                        tokenExpired = false;
                        document.getElementById('token-watch').classList.remove('expired');
                        document.getElementById('watch-label').classList.remove('expired');
                        document.getElementById('watch-time').classList.remove('expired');
                        
                        const timeString = expiryDate.toLocaleTimeString('en-US', {
                            hour: '2-digit',
                            minute: '2-digit',
                            second: '2-digit'
                        });
                        
                        document.getElementById('watch-label').innerHTML = 
                            'Token Expires At<div class="watch-time" id="watch-time">' + timeString + '</div>';
                        
                        updateWatchHands(expiryDate);
                    }
                } else {
                    document.getElementById('watch-label').innerHTML = 
                        'Token Status<div class="watch-time">Not Available</div>';
                }
            } catch (error) {
                console.error('Error updating token info:', error);
            }
        }

        // Update clock every second
        setInterval(updateClock, 1000);
        updateClock();

        // Update token info every 5 seconds
        setInterval(updateTokenInfo, 5000);
        updateTokenInfo();
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, gates=GATES_CONFIG)

@app.route('/api/open-gate', methods=['POST'])
def open_gate():
    data = request.json
    lane_id = data.get('lane_id')
    lane_name = data.get('lane_name')
    site_id = data.get('site_id')
    
    with token_lock:
        current_token = access_token
        current_expiry = token_expiry_time
    
    # Check if token is expired
    if time.time() >= current_expiry:
        return jsonify({'success': False, 'error': 'Token expired'}), 401
    
    if not current_token:
        return jsonify({'success': False, 'error': 'No token available'}), 401
    
    headers = {
        'Authorization': f'Bearer {current_token}',
        'Content-Type': 'application/json'
    }
    
    url = f"{API_BASE_URL}/site/{site_id}/lane/{lane_id}/open-gate"
    
    try:
        response = requests.post(url, headers=headers, timeout=15)
        response.raise_for_status()
        return jsonify({'success': True, 'message': f'{lane_name} opened successfully'})
    except requests.exceptions.HTTPError as e:
        return jsonify({'success': False, 'error': f'HTTP {e.response.status_code}'}), 500
    except requests.exceptions.RequestException as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/refresh-token', methods=['POST'])
def manual_refresh():
    success = refresh_tokens()
    return jsonify({'success': success})

@app.route('/api/token-status')
def token_status():
    with token_lock:
        expiry = token_expiry_time
    
    return jsonify({
        'expiry_time': expiry + 60 if expiry > 0 else None,
        'refresh_time': expiry if expiry > 0 else None
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
