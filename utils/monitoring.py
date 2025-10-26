"""
Member Monitoring Module
Background monitoring for auto-opening gates for members
"""

import threading
import time
from utils.gate_control import get_active_visits, open_gate

monitoring_active = False
monitoring_thread = None

def monitor_and_auto_open(status_callback, get_members_func, get_blacklist_func):
    """Background thread to monitor for member vehicles and auto-open gates"""
    global monitoring_active

    last_opened = {}

    while monitoring_active:
        try:
            member_plates = get_members_func()
            blacklist_plates = get_blacklist_func()

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

                                status_callback(f"BLOCKED: {plate} ({user_name}) - ON BLACKLIST!")
                                print(f"[BLOCKED] Blacklisted plate detected: {plate}")

                                last_opened[visit_id] = time.time()

                        # Check if plate is in member list
                        elif plate and plate in [p.upper() for p in member_plates]:
                            if visit_id and visit_id not in last_opened:
                                user = transaction.get('user', {})
                                user_name = f"{user.get('firstName', '')} {user.get('lastName', '')}".strip()

                                status_callback(f"AUTO-OPEN: {plate} ({user_name}) at site {site_id}")
                                print(f"[AUTO-OPEN] Detected member: {plate} - Transaction ID: {visit_id} - Lane: {lane_id}")

                                if lane_id:
                                    open_gate(str(lane_id), f"Auto Lane {lane_id}", site_id=site_id, visit_id=visit_id)
                                else:
                                    default_lane = "5568" if site_id == "4005" else "5565"
                                    open_gate(default_lane, "Default Gate", site_id=site_id, visit_id=visit_id)

                                last_opened[visit_id] = time.time()

                # Clean up old entries
                current_time = time.time()
                last_opened = {k: v for k, v in last_opened.items() if current_time - v < 600}

            time.sleep(3)

        except Exception as e:
            print(f"Monitor error: {e}")
            import traceback
            traceback.print_exc()
            time.sleep(5)

def start_member_monitoring(status_callback, get_members_func, get_blacklist_func):
    """Start the monitoring thread"""
    global monitoring_active, monitoring_thread

    if monitoring_active:
        return

    monitoring_active = True
    monitoring_thread = threading.Thread(
        target=monitor_and_auto_open,
        args=(status_callback, get_members_func, get_blacklist_func),
        daemon=True
    )
    monitoring_thread.start()
    print("Member monitoring started")

def stop_member_monitoring():
    """Stop the monitoring thread"""
    global monitoring_active
    monitoring_active = False
    print("Member monitoring stopped")
