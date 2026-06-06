import subprocess
import time
import signal
import sys

print("[+] Starting SOC System...")

# -----------------------------
# 1. EVENT SERVER FIRST
# -----------------------------
event_server = subprocess.Popen(["python3", "event_server.py"])
time.sleep(2)

# -----------------------------
# 2. IDS (ROOT REQUIRED)
# -----------------------------
ids_process = subprocess.Popen(["sudo", "python3", "network_scan.py"])
time.sleep(3)

# -----------------------------
# 3. DASHBOARD
# -----------------------------
dashboard_process = subprocess.Popen(["python3", "dashboard.py"])

print("[+] SOC Running -> http://127.0.0.1:5000")


# -----------------------------
# CLEAN SHUTDOWN
# -----------------------------
def shutdown(sig, frame):
    print("\n[+] Stopping SOC...")

    event_server.terminate()
    ids_process.terminate()
    dashboard_process.terminate()

    try:
        event_server.wait(timeout=2)
        ids_process.wait(timeout=2)
        dashboard_process.wait(timeout=2)
    except:
        event_server.kill()
        ids_process.kill()
        dashboard_process.kill()

    sys.exit(0)


signal.signal(signal.SIGINT, shutdown)
signal.signal(signal.SIGTERM, shutdown)

# KEEP ALIVE
while True:
    time.sleep(1)