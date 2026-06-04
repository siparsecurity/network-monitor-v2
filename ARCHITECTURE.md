# Architecture

run_soc.py

├── event_server.py
├── network_scan.py
└── dashboard.py

## Components

### event_server.py

Receives and stores events.
Provides APIs for dashboard access.

### network_scan.py

Performs network discovery.
Tracks devices.
Detects ARP spoofing.
Generates events.

### dashboard.py

SOC-style monitoring dashboard.
Displays devices, alerts and statistics.

### run_soc.py

Starts and manages all services.
