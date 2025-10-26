#!/usr/bin/env python3
"""
Metropolis Gate Opener - Web Application
Flask-based web interface for Render.com deployment
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import os
import json
import threading
import time
from datetime import datetime
from functools import wraps
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import utilities
from utils.gate_control import (
    get_gates, open_gate, get_hanging_exits, get_closed_visits,
    get_occupancy, get_active_visits, get_all_members
)
from utils.token_manager import (
    get_token_expiration_time, is_token_expired,
    refresh_token_headless, decode_jwt_payload
)
from utils.monitoring import start_member_monitoring, stop_member_monitoring
from utils.token_monitor import start_token_monitoring, stop_token_monitoring

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SESSION_TYPE'] = 'filesystem'

# Enable CORS
CORS(app)

# Initialize SocketIO for real-time updates (use threading for Render.com compatibility)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Global state
AUTH_KEY = os.environ.get('AUTH_KEY', '')
EMAIL = os.environ.get('METROPOLIS_EMAIL', 'security@555capitolmall.com')
PASSWORD = os.environ.get('METROPOLIS_PASSWORD', '555_Security')

# Storage files
MEMBERS_FILE = 'data/memberships.json'
BLACKLIST_FILE = 'data/blacklist.json'

# Ensure data directory exists
os.makedirs('data', exist_ok=True)

# Load members and blacklist
def load_members():
    if os.path.exists(MEMBERS_FILE):
        with open(MEMBERS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_members(members):
    with open(MEMBERS_FILE, 'w') as f:
        json.dump(members, f, indent=2)

def load_blacklist():
    if os.path.exists(BLACKLIST_FILE):
        with open(BLACKLIST_FILE, 'r') as f:
            return json.load(f)
    return []

def save_blacklist(blacklist):
    with open(BLACKLIST_FILE, 'w') as f:
        json.dump(blacklist, f, indent=2)

# Simple auth decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ==================== ROUTES ====================

@app.route('/')
def index():
    if 'logged_in' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        # Simple password check (use environment variable)
        if password == os.environ.get('DASHBOARD_PASSWORD', 'metropolis123'):
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        return render_template('login.html', error='Invalid password')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    token_info = None
    if AUTH_KEY:
        exp_time = get_token_expiration_time(AUTH_KEY)
        if exp_time:
            time_remaining = exp_time - datetime.now()
            hours = int(time_remaining.total_seconds() // 3600)
            minutes = int((time_remaining.total_seconds() % 3600) // 60)
            token_info = {
                'expires': exp_time.strftime('%Y-%m-%d %H:%M:%S'),
                'remaining': f"{hours}h {minutes}m",
                'is_expired': is_token_expired(AUTH_KEY)
            }

    return render_template('dashboard.html', token_info=token_info)

# ==================== API ENDPOINTS ====================

@app.route('/api/gates', methods=['GET'])
@login_required
def api_get_gates():
    """Get available gates"""
    gates = [
        {"id": "5568", "name": "6th Street Exit", "site_id": "4005"},
        {"id": "5569", "name": "L Street Exit", "site_id": "4005"},
        {"id": "5565", "name": "Bank of America Exit", "site_id": "4007"},
    ]
    return jsonify({'success': True, 'gates': gates})

@app.route('/api/gate/open', methods=['POST'])
@login_required
def api_open_gate():
    """Open a specific gate"""
    data = request.json
    lane_id = data.get('lane_id')
    gate_name = data.get('gate_name')
    site_id = data.get('site_id')
    visit_id = data.get('visit_id')

    success = open_gate(lane_id, gate_name, site_id=site_id, visit_id=visit_id)

    return jsonify({
        'success': success,
        'message': f"Gate {gate_name} {'opened' if success else 'failed to open'}"
    })

@app.route('/api/occupancy/<site_id>', methods=['GET'])
@login_required
def api_get_occupancy(site_id):
    """Get garage occupancy"""
    data = get_occupancy(site_id)
    return jsonify({'success': True, 'data': data})

@app.route('/api/visits/<site_id>', methods=['GET'])
@login_required
def api_get_visits(site_id):
    """Get recent visits"""
    count = request.args.get('count', 25, type=int)
    data = get_closed_visits(site_id, count)
    return jsonify({'success': True, 'data': data})

@app.route('/api/waiting/<site_id>', methods=['GET'])
@login_required
def api_get_waiting(site_id):
    """Get cars waiting at exit"""
    data = get_hanging_exits(site_id)
    return jsonify({'success': True, 'data': data})

@app.route('/api/members', methods=['GET'])
@login_required
def api_get_members():
    """Get member list"""
    members = load_members()
    return jsonify({'success': True, 'members': members})

@app.route('/api/members/add', methods=['POST'])
@login_required
def api_add_member():
    """Add a member plate"""
    data = request.json
    plate = data.get('plate', '').strip().upper()

    if not plate:
        return jsonify({'success': False, 'message': 'Plate required'}), 400

    members = load_members()
    if plate in members:
        return jsonify({'success': False, 'message': 'Plate already exists'}), 400

    members.append(plate)
    save_members(members)

    return jsonify({'success': True, 'message': f'Added {plate}'})

@app.route('/api/members/remove', methods=['POST'])
@login_required
def api_remove_member():
    """Remove a member plate"""
    data = request.json
    plate = data.get('plate', '').strip().upper()

    members = load_members()
    if plate not in members:
        return jsonify({'success': False, 'message': 'Plate not found'}), 404

    members.remove(plate)
    save_members(members)

    return jsonify({'success': True, 'message': f'Removed {plate}'})

@app.route('/api/blacklist', methods=['GET'])
@login_required
def api_get_blacklist():
    """Get blacklist"""
    blacklist = load_blacklist()
    return jsonify({'success': True, 'blacklist': blacklist})

@app.route('/api/blacklist/add', methods=['POST'])
@login_required
def api_add_blacklist():
    """Add to blacklist"""
    data = request.json
    plate = data.get('plate', '').strip().upper()

    if not plate:
        return jsonify({'success': False, 'message': 'Plate required'}), 400

    blacklist = load_blacklist()
    if plate in blacklist:
        return jsonify({'success': False, 'message': 'Plate already blacklisted'}), 400

    blacklist.append(plate)
    save_blacklist(blacklist)

    return jsonify({'success': True, 'message': f'Blacklisted {plate}'})

@app.route('/api/blacklist/remove', methods=['POST'])
@login_required
def api_remove_blacklist():
    """Remove from blacklist"""
    data = request.json
    plate = data.get('plate', '').strip().upper()

    blacklist = load_blacklist()
    if plate not in blacklist:
        return jsonify({'success': False, 'message': 'Plate not found'}), 404

    blacklist.remove(plate)
    save_blacklist(blacklist)

    return jsonify({'success': True, 'message': f'Removed {plate} from blacklist'})

@app.route('/api/token/status', methods=['GET'])
@login_required
def api_token_status():
    """Get token status"""
    if not AUTH_KEY:
        return jsonify({'success': False, 'message': 'No token set'})

    exp_time = get_token_expiration_time(AUTH_KEY)
    if not exp_time:
        return jsonify({'success': False, 'message': 'Could not decode token'})

    time_remaining = exp_time - datetime.now()
    hours = int(time_remaining.total_seconds() // 3600)
    minutes = int((time_remaining.total_seconds() % 3600) // 60)

    return jsonify({
        'success': True,
        'expires': exp_time.strftime('%Y-%m-%d %H:%M:%S'),
        'remaining': f"{hours}h {minutes}m",
        'is_expired': is_token_expired(AUTH_KEY)
    })

@app.route('/api/token/refresh', methods=['POST'])
@login_required
def api_token_refresh():
    """Manually refresh token"""
    global AUTH_KEY

    new_token = refresh_token_headless(EMAIL, PASSWORD)
    if new_token:
        AUTH_KEY = new_token
        os.environ['AUTH_KEY'] = new_token
        return jsonify({'success': True, 'message': 'Token refreshed successfully'})

    return jsonify({'success': False, 'message': 'Token refresh failed'}), 500

@app.route('/api/member-directory/<site_id>', methods=['GET'])
@login_required
def api_member_directory(site_id):
    """Get all members from a site"""
    members = get_all_members(site_id)
    return jsonify({'success': True, 'members': members})

# ==================== SOCKETIO EVENTS ====================

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('connected', {'data': 'Connected to server'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('start_monitoring')
def handle_start_monitoring():
    """Start auto-monitoring for members"""
    def status_callback(message):
        socketio.emit('monitoring_update', {'message': message})

    start_member_monitoring(status_callback, load_members, load_blacklist)
    emit('monitoring_started', {'success': True})

@socketio.on('stop_monitoring')
def handle_stop_monitoring():
    """Stop auto-monitoring"""
    stop_member_monitoring()
    emit('monitoring_stopped', {'success': True})

@socketio.on('start_token_monitor')
def handle_start_token_monitor():
    """Start token auto-monitoring"""
    def status_callback(message):
        socketio.emit('token_update', {'message': message})

    start_token_monitoring(status_callback, EMAIL, PASSWORD)
    emit('token_monitor_started', {'success': True})

@socketio.on('stop_token_monitor')
def handle_stop_token_monitor():
    """Stop token monitoring"""
    stop_token_monitoring()
    emit('token_monitor_stopped', {'success': True})

# ==================== HEALTH CHECK ====================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring"""
    status = {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'metropolis-gate-control',
        'async_mode': 'threading',
        'token_present': bool(AUTH_KEY),
        'python_version': os.sys.version
    }

    # Check token if present
    if AUTH_KEY:
        try:
            exp_time = get_token_expiration_time(AUTH_KEY)
            if exp_time:
                status['token_expires'] = exp_time.isoformat()
                status['token_valid'] = not is_token_expired(AUTH_KEY)
            else:
                status['token_valid'] = False
        except Exception as e:
            status['token_error'] = str(e)

    return jsonify(status), 200

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# ==================== MAIN ====================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=False)
