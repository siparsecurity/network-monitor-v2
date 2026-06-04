# Network Monitor v2 — Sipar Security

A lightweight, open-source network monitoring and threat detection platform featuring real-time device tracking, event logging, risk scoring, and a SOC-style dashboard.

![Status](https://img.shields.io/badge/status-development-orange)
![Python](https://img.shields.io/badge/python-3.10+-blue)
![License](https://img.shields.io/badge/license-MIT-green)

---

## Features

### Device Discovery

Discovers devices on your network using ARP scanning.

### Real-Time Tracking

Continuously monitors device activity and online/offline status.

### Event Logging

Records network events with timestamps for monitoring and analysis.

### Risk Scoring

Assigns risk levels to detected devices and suspicious activity.

### SOC Dashboard

Browser-based dashboard for monitoring devices, alerts, and statistics.

### ARP Spoofing Detection

Detects potential ARP spoofing attacks and generates alerts.

### Historical Event Storage

Stores event history for later review and investigation.

---

## Requirements

* Python 3.10+
* Linux (recommended)
* Root or Administrator privileges
* Network access for ARP scanning

---

## Installation

```bash
# Clone the repository
git clone https://github.com/sayedsubayyal/network-monitor-v2.git

cd network-monitor-v2

# Install dependencies
pip install -r requirements.txt
```

---

## Run

```bash
python3 run_soc.py
```

---

## Dashboard

Once running, open your browser:

```text
http://localhost:5000
```

The dashboard displays:

* Connected devices
* Device status
* Security alerts
* Event history
* Risk scores

---

## Project Structure

```text
network-monitor-v2/

├── run_soc.py
├── network_scan.py
├── event_server.py
├── dashboard.py
│
├── docs/
│   ├── ROADMAP.md
│   ├── CHANGELOG.md
│   ├── RELEASES.md
│   └── ARCHITECTURE.md
│
├── requirements.txt
├── LICENSE
└── README.md
```

---

## Roadmap

### Completed

* Device Discovery
* Real-Time Device Tracking
* Event Logging
* Risk Scoring
* Event Server
* SOC Dashboard
* ARP Spoof Detection
* Historical Event Storage

### Planned

* Alert Improvements
* Event Export
* Dashboard Enhancements
* Advanced Analytics
* Threat Intelligence Integration

---

## About

Built by Sipar Security — a cybersecurity company from Pakistan focused on practical, accessible security tools.

Website: siparsecurity.com (coming soon)

Email: [siparsecurity@gmail.com](mailto:siparsecurity@gmail.com)

LinkedIn: https://www.linkedin.com/company/126573957

GitHub: https://github.com/sayedsubayyal

---

## Status

Version 2.0 is currently under active development.

Core functionality has been implemented and the project is undergoing testing, optimization, and final refinement before public release.

---

## License

MIT License — see LICENSE for details.
