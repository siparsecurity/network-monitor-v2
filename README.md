# Sipar Security — Network Monitor v2
███████╗██╗██████╗  █████╗ ██████╗     ███████╗███████╗ ██████╗
██╔════╝██║██╔══██╗██╔══██╗██╔══██╗    ██╔════╝██╔════╝██╔════╝
███████╗██║██████╔╝███████║██████╔╝    ███████╗█████╗  ██║
╚════██║██║██╔═══╝ ██╔══██║██╔══██╗    ╚════██║██╔══╝  ██║
███████║██║██║     ██║  ██║██║  ██║    ███████║███████╗╚██████╗
╚══════╝╚═╝╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝    ╚══════╝╚══════╝ ╚═════╝

![Version](https://img.shields.io/badge/version-v0.2--layer2-brightgreen)
![Status](https://img.shields.io/badge/status-publicly%20released-brightgreen)
![Python](https://img.shields.io/badge/python-3.10+-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-Linux-orange)
![Made in Pakistan](https://img.shields.io/badge/made%20in-Pakistan%20🇵🇰-009900)

---

## Overview

**Sipar Security Network Monitor v2** is a Python-based SOC-grade network
monitoring and intrusion detection system. It performs continuous ARP-based
network scanning, maintains a persistent device intelligence database, detects
threats in real time, and presents everything through a dark SOC-style web
dashboard — all running locally on your machine.

Built for home users, IT administrators, and small businesses who need
real network visibility without an enterprise budget.

---

## Architecture
┌─────────────────────────────────────────────────────┐
│                   run_soc.py                        │
│            [ Process Orchestrator ]                 │
└──────────┬──────────────┬──────────────┬────────────┘
│              │              │
▼              ▼              ▼
┌──────────────┐ ┌────────────┐ ┌───────────────┐
│network_scan  │ │event_server│ │  dashboard.py │
│    .py       │ │    .py     │ │               │
│              │ │            │ │  localhost     │
│ ARP Scanner  │ │ Flask API  │ │  :5000        │
│ Threat Det.  │ │ JSONL Log  │ │               │
│ MAC History  │ │ /push      │ │  SOC UI       │
│              │ │ /events    │ │               │
└──────┬───────┘ │ /devices   │ └───────┬───────┘
│         │ /stats     │         │
│         │ /logs      │         │
└────────▶│            │◀────────┘
│ :5050      │
└────────────┘
│
▼
soc_events.jsonl
[ Persistent Log File ]

---

## Version 2.0 — Device Intelligence

### What's new in v2.0

| Module | Feature | Detail |
|---|---|---|
| `network_scan.py` | Device schema | first_seen, last_seen, status, cumulative risk |
| `network_scan.py` | Offline detection | DEVICE_OFFLINE fires after 3 consecutive missed scans |
| `network_scan.py` | ARP spoof cooldown | Prevents repeated alerts for the same incident |
| `network_scan.py` | MAC randomization | 60s window filters out phone MAC rotation false positives |
| `network_scan.py` | Scan timing | 7s interval · 1s ARP timeout |
| `event_server.py` | Persistent logging | All events written to soc_events.jsonl |
| `event_server.py` | State reconstruction | Full device state rebuilt from disk on every restart |
| `event_server.py` | /stats endpoint | Returns top risk devices and system summary |
| `dashboard.py` | Device table | Online/Offline badges · First Seen · Last Seen · Risk |
| `dashboard.py` | Stat cards | Total Devices · Online · Offline · Critical · Total Events |
| `dashboard.py` | Alerts panel | Filtered — only NEW_DEVICE · ARP_SPOOF · PORT_SCAN |
| `dashboard.py` | Refresh rate | 5s auto-refresh |

---

## Requirements
Python     3.10+
OS         Linux (recommended) / Windows
Privileges Root or Administrator — required for ARP scanning
Network    Active interface with LAN access

### Dependencies
flask
scapy
netifaces
requests

---

## Installation

```bash
# Clone the repository
git clone https://github.com/siparsecurity/network-monitor-v2.git
cd network-monitor-v2

# Install dependencies
sudo pip install -r requirements.txt
```

---

## Usage

```bash
# Start all 3 processes at once
sudo python3 run_soc.py
```

```bash
# Or run individually
sudo python3 event_server.py    # Start event API first
sudo python3 network_scan.py    # Start scanner second  
sudo python3 dashboard.py       # Start dashboard third
```

### Access the dashboard
http://localhost:5000

### API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/events` | GET | All events from current session |
| `/devices` | GET | Current device state |
| `/stats` | GET | Summary + top risk devices |
| `/logs` | GET | Full persistent log from disk |
| `/push` | POST | Receive event from scanner |

---

## Event Types

| Event | Risk | Trigger |
|---|---|---|
| `IDS_START` | 0 | System startup |
| `INITIAL_DEVICE` | 0 | Device found on first scan |
| `NEW_DEVICE` | 5 | Unknown device joins network |
| `DEVICE_OFFLINE` | 2 | Device missed 3 consecutive scans |
| `ARP_SPOOF` | 20 | IP changes MAC address |

---

## Project Structure
network-monitor-v2/
│
├── run_soc.py              # Entry point — orchestrates all processes
├── network_scan.py         # ARP scan engine + threat detection logic
├── event_server.py         # Flask event API + persistent JSONL logging
├── dashboard.py            # SOC-style web dashboard
│
├── requirements.txt        # Python dependencies
├── LICENSE                 # MIT License
├── README.md               # This file
│
├── CHANGELOG.md            # Full version history
├── RELEASES.md             # All releases with download links
├── ROADMAP.md              # Planned features
└── ARCHITECTURE.md         # System design and data flow

---

## Roadmap

| Version | Codename | Status | Key Features |
|---|---|---|---|
| v0.1 | Foundation | ✅ Released | ARP scan, event logging, basic dashboard |
| v0.2 | Device Intelligence | ✅ Released | Offline detection, device schema, /stats API |
| v0.3 | Alerts | 🔜 Planned | Email/SMS alerts, CSV export, port scan detection |
| v1.0 | Public Release | 🔜 2026 | Installer, full docs, cross-platform |

---

## Security Notice

This tool is built for **authorized network monitoring only.**
Only run it on networks you own or have explicit permission to monitor.
Unauthorized network scanning may violate local laws.

---

## About

**Sipar Security** is a cybersecurity company from Pakistan building
open-source network security tools for everyone.

| | |
|---|---|
| 🌐 Website | [siparsecurity.github.io](https://siparsecurity.github.io) |
| 📧 Email | [siparsecurity@gmail.com](mailto:siparsecurity@gmail.com) |
| 💼 LinkedIn | [linkedin.com/company/siparsecurity](https://linkedin.com/company/siparsecurity) |
| ⭐ GitHub | [github.com/siparsecurity](https://github.com/siparsecurity) |

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

*Built with Python · Powered by Scapy · Made in Pakistan 🇵🇰*
