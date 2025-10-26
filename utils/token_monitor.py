"""
Token Monitor Module
Background monitoring for automatic token refresh
"""

import threading
import time
import os
from datetime import datetime
from utils.token_manager import (
    get_token_expiration_time, is_token_expired, refresh_token_headless
)

token_monitor_active = False
token_monitor_thread = None

def token_monitor_loop(status_callback, email, password):
    """Background thread to monitor token expiration every 3 minutes"""
    global token_monitor_active

    print("\nToken monitor started - checking every 3 minutes")

    while token_monitor_active:
        try:
            AUTH_KEY = os.environ.get('AUTH_KEY', '')
            exp_time = get_token_expiration_time(AUTH_KEY)

            if exp_time:
                time_remaining = exp_time - datetime.now()
                hours = int(time_remaining.total_seconds() // 3600)
                minutes = int((time_remaining.total_seconds() % 3600) // 60)

                status_msg = f"Token expires in {hours}h {minutes}m"
                print(f"[TOKEN CHECK] {status_msg}")

                if status_callback:
                    status_callback(status_msg)

                # Check if expired or expiring soon
                if is_token_expired(AUTH_KEY):
                    print("\nTOKEN EXPIRED OR EXPIRING SOON - Auto-refreshing...")

                    if status_callback:
                        status_callback("Refreshing token...")

                    new_token = refresh_token_headless(email, password)

                    if new_token:
                        os.environ['AUTH_KEY'] = new_token
                        print("Token successfully refreshed!")

                        if status_callback:
                            status_callback("Token refreshed successfully!")
                    else:
                        print("Token refresh failed!")

                        if status_callback:
                            status_callback("Token refresh failed!")
            else:
                print("[TOKEN CHECK] Could not decode token")
                if status_callback:
                    status_callback("Token decode error")

            # Wait 3 minutes before next check
            time.sleep(180)

        except Exception as e:
            print(f"Token monitor error: {e}")
            import traceback
            traceback.print_exc()
            time.sleep(60)

def start_token_monitoring(status_callback, email, password):
    """Start the token monitoring thread"""
    global token_monitor_active, token_monitor_thread

    if token_monitor_active:
        return

    token_monitor_active = True
    token_monitor_thread = threading.Thread(
        target=token_monitor_loop,
        args=(status_callback, email, password),
        daemon=True
    )
    token_monitor_thread.start()
    print("Token monitoring started")

def stop_token_monitoring():
    """Stop the token monitoring thread"""
    global token_monitor_active
    token_monitor_active = False
    print("Token monitoring stopped")
