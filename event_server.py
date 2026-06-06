from flask import Flask, jsonify, request
from collections import deque
from datetime import datetime
import json
import os

app = Flask(__name__)

# -----------------------------
# CONFIG
# -----------------------------
LOG_FILE = "soc_events.jsonl"

events = deque(maxlen=500)
devices = {}

# -----------------------------
# DEVICE STATE HELPER
# -----------------------------
def update_device_state(ip, mac, event_type, risk, timestamp):
    """
    Update device record on every incoming event.
    - first_seen is set once and never overwritten.
    - last_seen is always updated.
    - risk is cumulative (adds up across events).
    - status stays ONLINE until offline logic sets it (Layer 2.2 Step 2).
    """
    if ip not in devices:
        devices[ip] = {
            "mac": mac,
            "first_seen": timestamp,
            "last_seen": timestamp,
            "status": "ONLINE",
            "risk": risk
        }
    else:
        existing = devices[ip]

        # Update MAC if it changed (most recent wins)
        if mac:
            existing["mac"] = mac

        # last_seen always updated
        existing["last_seen"] = timestamp

        # Accumulate risk
        existing["risk"] = existing.get("risk", 0) + risk

        # Status: if a device reappears after being marked OFFLINE, bring it back
        if existing["status"] == "OFFLINE" and event_type not in ("DEVICE_OFFLINE",):
            existing["status"] = "ONLINE"

# -----------------------------
# LOAD OLD EVENTS ON STARTUP
# -----------------------------
if os.path.exists(LOG_FILE):
    try:
        with open(LOG_FILE, "r") as f:
            for line in f:
                line = line.strip()

                if not line:
                    continue

                data = json.loads(line)
                events.append(data)

                ip        = data.get("ip", "")
                mac       = data.get("mac", "")
                event_type = data.get("event", "")
                risk      = data.get("risk", 0)
                timestamp = data.get("timestamp", "")

                if ip:
                    update_device_state(ip, mac, event_type, risk, timestamp)

        print(f"[+] Loaded {len(events)} historical events")
        print(f"[+] Reconstructed {len(devices)} device records")

    except Exception as e:
        print(f"[!] Error loading logs: {e}")

# -----------------------------
# RECEIVE EVENTS FROM IDS
# -----------------------------
@app.route("/push", methods=["POST"])
def push_event():

    data = request.json or {}

    data["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    events.append(data)

    ip         = data.get("ip", "")
    mac        = data.get("mac", "")
    event_type = data.get("event", "")
    risk       = data.get("risk", 0)
    timestamp  = data["timestamp"]

    if ip:
        update_device_state(ip, mac, event_type, risk, timestamp)

    # Save permanently
    try:
        with open(LOG_FILE, "a") as f:
            f.write(json.dumps(data) + "\n")
    except Exception as e:
        print(f"[!] Log write error: {e}")

    return {"status": "ok"}

# -----------------------------
# EVENTS API
# -----------------------------
@app.route("/events")
def get_events():
    return jsonify(list(events))

# -----------------------------
# DEVICES API
# -----------------------------
@app.route("/devices")
def get_devices():
    return jsonify(devices)

# -----------------------------
# LOG FILE API
# -----------------------------
@app.route("/logs")
def get_logs():
    try:
        data = []
        with open(LOG_FILE, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    data.append(json.loads(line))
        return jsonify(data)
    except:
        return jsonify([])

# -----------------------------
# STATS API
# -----------------------------
@app.route("/stats")
def get_stats():
    online_count   = sum(1 for d in devices.values() if d.get("status") == "ONLINE")
    offline_count  = sum(1 for d in devices.values() if d.get("status") == "OFFLINE")
    critical_count = sum(1 for d in devices.values() if d.get("risk", 0) >= 20)

    alert_types    = {"NEW_DEVICE", "ARP_SPOOF", "DEVICE_OFFLINE", "PORT_SCAN"}
    alert_count    = sum(1 for e in events if e.get("event") in alert_types)

    top_risk = sorted(
        [{"ip": ip, "risk": d.get("risk", 0)} for ip, d in devices.items()],
        key=lambda x: x["risk"],
        reverse=True
    )[:5]

    return jsonify({
        "total_devices":  len(devices),
        "online":         online_count,
        "offline":        offline_count,
        "critical":       critical_count,
        "total_events":   len(events),
        "total_alerts":   alert_count,
        "top_risk_devices": top_risk
    })

# -----------------------------
# STATUS PAGE
# -----------------------------
@app.route("/")
def home():
    online  = sum(1 for d in devices.values() if d.get("status") == "ONLINE")
    offline = sum(1 for d in devices.values() if d.get("status") == "OFFLINE")

    return f"""
    <h2>SOC Event Server Running</h2>

    <p>Total Events : {len(events)}</p>
    <p>Total Devices: {len(devices)}</p>
    <p>Online        : {online}</p>
    <p>Offline       : {offline}</p>

    <ul>
        <li><a href="/events">/events</a></li>
        <li><a href="/devices">/devices</a></li>
        <li><a href="/logs">/logs</a></li>
        <li><a href="/stats">/stats</a></li>
    </ul>
    """

# -----------------------------
# START SERVER
# -----------------------------
if __name__ == "__main__":
    print("[+] Event Server running on http://127.0.0.1:5050")
    app.run(host="127.0.0.1", port=5050, debug=False)