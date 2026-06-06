from flask import Flask
import requests

app = Flask(__name__)

EVENT_SERVER_EVENTS  = "http://127.0.0.1:5050/events"
EVENT_SERVER_DEVICES = "http://127.0.0.1:5050/devices"

ALERT_EVENTS = {"NEW_DEVICE", "ARP_SPOOF", "DEVICE_OFFLINE", "PORT_SCAN"}

@app.route("/")
def home():

    try:
        events  = requests.get(EVENT_SERVER_EVENTS,  timeout=3).json()
        devices = requests.get(EVENT_SERVER_DEVICES, timeout=3).json()
    except:
        return """
        <!DOCTYPE html>
        <html>
        <head><title>SOC Dashboard</title></head>
        <body style="background:#0b1220;color:white;font-family:Arial;margin:40px;">
            <h1 style="color:#38bdf8;">SOC Dashboard</h1>
            <p style="color:#ef4444;">Cannot connect to Event Server on port 5050.
            Make sure event_server.py is running.</p>
        </body>
        </html>
        """

    # ----------------------------------------
    # STATS
    # ----------------------------------------
    total_devices  = len(devices)
    total_events   = len(events)
    online_count   = sum(1 for d in devices.values() if d.get("status") == "ONLINE")
    offline_count  = sum(1 for d in devices.values() if d.get("status") == "OFFLINE")
    critical_count = sum(1 for d in devices.values() if d.get("risk", 0) >= 20)

    alerts = [e for e in events if e.get("event") in ALERT_EVENTS]

    # ----------------------------------------
    # DEVICE TABLE ROWS
    # ----------------------------------------
    device_rows = ""
    for ip, info in devices.items():
        risk   = info.get("risk", 0)
        status = info.get("status", "ONLINE")

        if risk >= 20:
            risk_class = "risk-high"
        elif risk >= 5:
            risk_class = "risk-medium"
        else:
            risk_class = "risk-low"

        status_badge = (
            '<span class="badge-online">ONLINE</span>'
            if status == "ONLINE"
            else '<span class="badge-offline">OFFLINE</span>'
        )

        device_rows += f"""
        <tr>
            <td>{ip}</td>
            <td class="mono">{info.get("mac", "")}</td>
            <td>{status_badge}</td>
            <td>{info.get("first_seen", "—")}</td>
            <td>{info.get("last_seen",  "—")}</td>
            <td class="{risk_class}">{risk}</td>
        </tr>
        """

    # ----------------------------------------
    # ALERT ROWS
    # ----------------------------------------
    alert_rows = ""
    for e in reversed(alerts[-30:]):
        event_type = e.get("event", "")

        if event_type == "ARP_SPOOF":
            label_class = "label-critical"
        elif event_type == "NEW_DEVICE":
            label_class = "label-warn"
        elif event_type == "DEVICE_OFFLINE":
            label_class = "label-offline"
        else:
            label_class = "label-info"

        alert_rows += f"""
        <tr>
            <td>{e.get("timestamp", "")}</td>
            <td><span class="event-label {label_class}">{event_type}</span></td>
            <td>{e.get("ip", "")}</td>
            <td class="mono">{e.get("mac", "")}</td>
            <td>{e.get("details", "")}</td>
            <td>{e.get("risk", 0)}</td>
        </tr>
        """

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Sipar Security</title>
        <meta http-equiv="refresh" content="5">
        <style>

            * {{ box-sizing: border-box; margin: 0; padding: 0; }}

            body {{
                background: #0b1220;
                color: #e2e8f0;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 14px;
                padding: 24px;
            }}

            /* ---- HEADER ---- */
            .header {{
                display: flex;
                align-items: center;
                justify-content: space-between;
                margin-bottom: 24px;
                border-bottom: 1px solid #1e293b;
                padding-bottom: 16px;
            }}

            .header h1 {{
                color: #38bdf8;
                font-size: 22px;
                letter-spacing: 1px;
            }}

            .header .subtitle {{
                color: #64748b;
                font-size: 12px;
                margin-top: 4px;
            }}

            .live-dot {{
                width: 10px;
                height: 10px;
                background: #22c55e;
                border-radius: 50%;
                display: inline-block;
                margin-right: 6px;
                animation: pulse 1.5s infinite;
            }}

            @keyframes pulse {{
                0%, 100% {{ opacity: 1; }}
                50%        {{ opacity: 0.3; }}
            }}

            /* ---- STAT CARDS ---- */
            .stats {{
                display: grid;
                grid-template-columns: repeat(5, 1fr);
                gap: 12px;
                margin-bottom: 24px;
            }}

            .stat-card {{
                background: #1e293b;
                border-radius: 10px;
                padding: 16px;
                text-align: center;
                border-top: 3px solid #334155;
            }}

            .stat-card.online  {{ border-top-color: #22c55e; }}
            .stat-card.offline {{ border-top-color: #64748b; }}
            .stat-card.alert   {{ border-top-color: #ef4444; }}
            .stat-card.events  {{ border-top-color: #38bdf8; }}
            .stat-card.devices {{ border-top-color: #a78bfa; }}

            .stat-value {{
                font-size: 28px;
                font-weight: bold;
                color: white;
            }}

            .stat-label {{
                font-size: 11px;
                color: #64748b;
                text-transform: uppercase;
                letter-spacing: 1px;
                margin-top: 4px;
            }}

            /* ---- SECTION ---- */
            .section {{
                background: #1e293b;
                border-radius: 10px;
                padding: 20px;
                margin-bottom: 20px;
            }}

            .section h2 {{
                color: #94a3b8;
                font-size: 13px;
                text-transform: uppercase;
                letter-spacing: 1px;
                margin-bottom: 16px;
                border-bottom: 1px solid #334155;
                padding-bottom: 10px;
            }}

            /* ---- TABLES ---- */
            table {{
                width: 100%;
                border-collapse: collapse;
            }}

            th {{
                background: #0f172a;
                color: #64748b;
                padding: 10px 12px;
                text-align: left;
                font-size: 11px;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}

            td {{
                padding: 10px 12px;
                border-bottom: 1px solid #0f172a;
                color: #cbd5e1;
            }}

            tr:last-child td {{ border-bottom: none; }}

            tr:hover td {{ background: #0f172a; }}

            .mono {{ font-family: monospace; font-size: 12px; color: #94a3b8; }}

            /* ---- STATUS BADGES ---- */
            .badge-online {{
                background: #14532d;
                color: #22c55e;
                padding: 2px 10px;
                border-radius: 12px;
                font-size: 11px;
                font-weight: bold;
                letter-spacing: 1px;
            }}

            .badge-offline {{
                background: #1e293b;
                color: #64748b;
                padding: 2px 10px;
                border-radius: 12px;
                font-size: 11px;
                font-weight: bold;
                letter-spacing: 1px;
                border: 1px solid #334155;
            }}

            /* ---- RISK COLORS ---- */
            .risk-low    {{ color: #22c55e; font-weight: bold; }}
            .risk-medium {{ color: #facc15; font-weight: bold; }}
            .risk-high   {{ color: #ef4444; font-weight: bold; }}

            /* ---- EVENT LABELS ---- */
            .event-label {{
                padding: 2px 8px;
                border-radius: 4px;
                font-size: 11px;
                font-weight: bold;
                letter-spacing: 0.5px;
            }}

            .label-critical {{ background: #450a0a; color: #ef4444; }}
            .label-warn     {{ background: #422006; color: #fb923c; }}
            .label-offline  {{ background: #1e293b; color: #94a3b8; border: 1px solid #334155; }}
            .label-info     {{ background: #0c1a2e; color: #38bdf8; }}

            /* ---- EMPTY STATE ---- */
            .empty {{
                text-align: center;
                color: #334155;
                padding: 30px;
                font-size: 13px;
            }}

        </style>
    </head>
    <body>

    <!-- HEADER -->
    <div class="header">
        <div>
            <h1>SIPAR SECURITY</h1>
            <div class="subtitle">Network Intrusion Detection System</div>
        </div>
        <div style="color:#64748b; font-size:12px;">
            <span class="live-dot"></span> Live — refreshes every 10s
        </div>
    </div>

    <!-- STAT CARDS -->
    <div class="stats">
        <div class="stat-card devices">
            <div class="stat-value">{total_devices}</div>
            <div class="stat-label">Total Devices</div>
        </div>
        <div class="stat-card online">
            <div class="stat-value">{online_count}</div>
            <div class="stat-label">Online</div>
        </div>
        <div class="stat-card offline">
            <div class="stat-value">{offline_count}</div>
            <div class="stat-label">Offline</div>
        </div>
        <div class="stat-card alert">
            <div class="stat-value">{critical_count}</div>
            <div class="stat-label">Critical</div>
        </div>
        <div class="stat-card events">
            <div class="stat-value">{total_events}</div>
            <div class="stat-label">Total Events</div>
        </div>
    </div>

    <!-- DEVICE TABLE -->
    <div class="section">
        <h2>Device Inventory</h2>
        <table>
            <tr>
                <th>IP Address</th>
                <th>MAC Address</th>
                <th>Status</th>
                <th>First Seen</th>
                <th>Last Seen</th>
                <th>Risk</th>
            </tr>
            {'<tr><td colspan="6" class="empty">No devices discovered yet.</td></tr>' if not device_rows else device_rows}
        </table>
    </div>

    <!-- ALERTS TABLE -->
    <div class="section">
        <h2>Security Alerts — Last 30</h2>
        <table>
            <tr>
                <th>Timestamp</th>
                <th>Event</th>
                <th>IP</th>
                <th>MAC</th>
                <th>Details</th>
                <th>Risk</th>
            </tr>
            {'<tr><td colspan="6" class="empty">No security alerts recorded.</td></tr>' if not alert_rows else alert_rows}
        </table>
    </div>

    </body>
    </html>
    """

    return html


if __name__ == "__main__":
    print("[+] Dashboard running at http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=False)