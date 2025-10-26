"""
Gate Control Functions
All API interactions with Metropolis gates
"""

import requests
import json
import os

BASE_URL = "https://specialist.api.metropolis.io"

def get_auth_key():
    """Get current AUTH_KEY from environment"""
    return os.environ.get('AUTH_KEY', '')

def get_gates():
    """Fetch available gates"""
    url = f"{BASE_URL}/api/sites/4005/gates"
    headers = {
        "Authorization": f"Bearer {get_auth_key()}",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0",
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Error fetching gates: {e}")
    return None

def open_gate(lane_id, gate_name, site_id=None, visit_id=None):
    """Open a specific gate/lane"""
    site = site_id if site_id else "4005"
    endpoint = f"/api/specialist/site/{site}/lane/{lane_id}/open-gate"

    if visit_id:
        endpoint += f"?visitId={visit_id}"

    url = BASE_URL + endpoint
    headers = {
        "Authorization": f"Bearer {get_auth_key()}",
        "Accept": "*/*",
        "Content-Type": "application/json",
        "Origin": "https://specialist.metropolis.io",
        "Referer": "https://specialist.metropolis.io/",
        "User-Agent": "Mozilla/5.0",
    }

    try:
        print(f"Opening gate: POST {endpoint}")
        response = requests.post(url, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")

        if response.status_code in [200, 201, 204]:
            return True
        else:
            print(f"Error response: {response.text}")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def get_hanging_exits(site_id):
    """Get count of cars waiting at exit"""
    url = f"{BASE_URL}/api/specialist/site/{site_id}/event/hanging-exit/count"
    headers = {
        "Authorization": f"Bearer {get_auth_key()}",
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
        "Authorization": f"Bearer {get_auth_key()}",
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
        "Authorization": f"Bearer {get_auth_key()}",
        "Accept": "*/*",
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Error fetching occupancy: {e}")
    return None

def get_active_visits(site_id):
    """Get currently active visits (cars in garage/at gates)"""
    url = f"{BASE_URL}/api/specialist/site/{site_id}/visits/closed?count=50&minPaymentDueAgeSeconds=0&zoneIds={site_id}"
    headers = {
        "Authorization": f"Bearer {get_auth_key()}",
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
        print(f"Error getting visits: {e}")
    return None

def get_all_members(site_id):
    """Get all members/users with active visits or subscriptions"""
    url = f"{BASE_URL}/api/specialist/site/{site_id}/visits/closed?count=100&minPaymentDueAgeSeconds=0&zoneIds={site_id}"
    headers = {
        "Authorization": f"Bearer {get_auth_key()}",
        "Accept": "*/*",
    }
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
        print(f"Error getting members: {e}")
    return []
