#!/usr/bin/env python3
import requests
import time
import sys

# --- CONFIGURATION ---
SITE_ID_TO_SCAN = "4006"
START_ID = 5500
END_ID = 6000
DELAY_BETWEEN_CHECKS = 0.1  # Seconds (prevent rate limiting/blocking)

# Auth Credentials
EMAIL = "security@555capitolmall.com"
PASSWORD = "555_Security"
CLIENT_ID = "metropolis-web-client"

# API Endpoints
TOKEN_URL = "https://auth.metropolis.io/realms/metropolis/protocol/openid-connect/token"
API_BASE_URL = "https://specialist.api.metropolis.io/api/specialist"

def get_access_token():
    """Authenticates and returns a valid access token."""
    print("🔑 Authenticating...", end=" ")
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
        print("Success!")
        return data['access_token']
    except Exception as e:
        print(f"\n❌ Auth Failed: {e}")
        sys.exit(1)

def scan_gates():
    token = get_access_token()
    valid_gates = []
    
    print(f"\n🔍 Starting Scan on Site {SITE_ID_TO_SCAN}")
    print(f"🎯 Range: {START_ID} - {END_ID}")
    print(f"⏱️  Delay: {DELAY_BETWEEN_CHECKS}s per request\n")
    print("-" * 50)

    try:
        for lane_id in range(START_ID, END_ID + 1):
            # Construct URL
            url = f"{API_BASE_URL}/site/{SITE_ID_TO_SCAN}/lane/{lane_id}/open-gate"
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }

            # Print current check (overwrite line to keep clean)
            sys.stdout.write(f"\r👉 Checking ID {lane_id}...")
            sys.stdout.flush()

            try:
                # We expect a 200 OK if the gate exists and opens
                # We expect a 404 or 400 if the ID is invalid
                response = requests.post(url, headers=headers, timeout=5)
                
                if response.status_code == 200:
                    print(f"\n✅ FOUND & OPENED: {lane_id}")
                    valid_gates.append(lane_id)
                elif response.status_code == 404:
                    # ID does not exist
                    pass
                elif response.status_code == 401:
                    print(f"\n❌ Token Expired. Stopping.")
                    break
                else:
                    # Some other error (500, 403, etc) - might be a valid gate but offline
                    print(f"\n⚠️  ID {lane_id}: Error {response.status_code} ({response.reason})")

            except requests.exceptions.RequestException as e:
                print(f"\n❌ Connection Error on {lane_id}: {e}")

            # Sleep to be safe
            time.sleep(DELAY_BETWEEN_CHECKS)

    except KeyboardInterrupt:
        print("\n\n🛑 Scan interrupted by user.")

    # --- SUMMARY ---
    print("\n" + "=" * 50)
    print("SCAN COMPLETE")
    print("=" * 50)
    
    if valid_gates:
        print(f"🎉 Found {len(valid_gates)} working gates:")
        print(valid_gates)
        
        # Save to file
        with open("valid_gates.txt", "w") as f:
            for gid in valid_gates:
                f.write(f"Site: {SITE_ID_TO_SCAN} | Gate ID: {gid}\n")
        print("\nResults saved to 'valid_gates.txt'")
    else:
        print("No working gates found in this range.")

if __name__ == "__main__":
    scan_gates()
