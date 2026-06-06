from scapy.all import ARP, Ether, srp, conf
import netifaces
import ipaddress
import time
import requests
from collections import defaultdict
from datetime import datetime

# -----------------------------
# CONFIG
# -----------------------------
SCAN_INTERVAL      = 7        # seconds between scans
OFFLINE_THRESHOLD  = 3        # missed scans before DEVICE_OFFLINE event
SPOOF_WINDOW       = 60       # seconds: MAC must change 2+ times within this window to trigger alert

# -----------------------------
# EVENT SENDER
# -----------------------------
def send_event(event, ip, mac="", details="", risk=0):
    try:
        requests.post(
            "http://127.0.0.1:5050/push",
            json={
                "event":   event,
                "ip":      ip,
                "mac":     mac,
                "details": details,
                "risk":    risk
            },
            timeout=1
        )
    except:
        pass


# -----------------------------
# AUTO NETWORK DETECTION
# -----------------------------
iface = str(conf.iface)

ip_info = netifaces.ifaddresses(iface)[netifaces.AF_INET][0]
ip_addr = ip_info["addr"]
netmask = ip_info["netmask"]

network = ipaddress.IPv4Network(f"{ip_addr}/{netmask}", strict=False)
target  = str(network)

print(f"[+] IDS Running on {target}")
send_event("IDS_START", ip_addr, "", target, 0)


# -----------------------------
# SCAN FUNCTION
# -----------------------------
def scan():
    arp   = ARP(pdst=target)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    pkt   = ether / arp

    ans = srp(pkt, timeout=1, verbose=False)[0]

    devices = {}
    for _, r in ans:
        devices[r.psrc] = r.hwsrc

    return devices


# -----------------------------
# STATE
# -----------------------------
trusted      = scan()
miss_count   = defaultdict(int)   # ip -> consecutive missed scans
online_state = {}                  # ip -> True/False (True = currently online)

# mac change tracking for spoof detection
# ip -> list of (mac, timestamp) tuples — only last N entries kept
mac_change_log = defaultdict(list)

# per-ip spoof alert cooldown: ip -> timestamp of last alert sent
spoof_alerted_at = {}
SPOOF_ALERT_COOLDOWN = 120  # seconds before the same IP can trigger another spoof alert

print("\n[+] Initial Devices:")
for ip, mac in trusted.items():
    print(ip, "->", mac)
    send_event("INITIAL_DEVICE", ip, mac)
    online_state[ip] = True

print("\n[+] IDS Running...\n")


# -----------------------------
# MAIN LOOP
# -----------------------------
while True:
    time.sleep(SCAN_INTERVAL)
    current = scan()
    now     = time.time()

    # ----------------------------------------
    # NEW DEVICE DETECTION
    # ----------------------------------------
    for ip, mac in current.items():
        if ip not in trusted:
            print(f"[NEW DEVICE] {ip} -> {mac}")
            send_event("NEW_DEVICE", ip, mac, "new device detected", 5)

        trusted[ip]      = mac
        miss_count[ip]   = 0
        online_state[ip] = True

    # ----------------------------------------
    # OFFLINE DETECTION
    # ----------------------------------------
    for ip in list(trusted.keys()):
        if ip not in current:
            miss_count[ip] += 1

            if miss_count[ip] == OFFLINE_THRESHOLD:
                # Only fire the event once per offline transition
                if online_state.get(ip, True):
                    print(f"[OFFLINE] {ip} — missed {OFFLINE_THRESHOLD} scans")
                    send_event(
                        "DEVICE_OFFLINE",
                        ip,
                        trusted[ip],
                        f"missed {OFFLINE_THRESHOLD} consecutive scans",
                        0
                    )
                    online_state[ip] = False

    # ----------------------------------------
    # ARP SPOOF DETECTION
    # MAC randomization guard:
    # Only alert if the same IP changes MAC 2+ times
    # within SPOOF_WINDOW seconds.
    # ----------------------------------------
    for ip, mac in current.items():
        log = mac_change_log[ip]

        # Check if this MAC differs from the last recorded one
        if log and log[-1][0] != mac:
            log.append((mac, now))
        elif not log:
            log.append((mac, now))

        # Trim entries older than SPOOF_WINDOW
        mac_change_log[ip] = [(m, t) for m, t in log if now - t <= SPOOF_WINDOW]

        # Count distinct MACs seen in the window
        recent_macs = set(m for m, t in mac_change_log[ip])

        if len(recent_macs) >= 3:
            # Check cooldown to avoid spam
            last_alert = spoof_alerted_at.get(ip, 0)

            if now - last_alert > SPOOF_ALERT_COOLDOWN:
                print(f"[ALERT] ARP SPOOF detected: {ip} -> {recent_macs}")
                send_event(
                    "ARP_SPOOF",
                    ip,
                    mac,
                    f"MAC changed {len(recent_macs)} times in {SPOOF_WINDOW}s window: {recent_macs}",
                    20
                )
                spoof_alerted_at[ip] = now