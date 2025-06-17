# 👾 Network Tools
 
*Network Manager Python Script*

## 🌟 Features

Show full network configuration (ipconfig /all)
Set static IP, subnet, gateway, and DNS
Switch to DHCP (automatic IP)
Change DNS servers (Google, Cloudflare, OpenDNS, or custom)
Network diagnostics (ping, traceroute, flush DNS, reset TCP/IP stack)
Network reset (repairs Winsock, TCP/IP, renews IP, etc.)
Network speed test (requires internet access)
Scan local network for devices (shows IP, MAC, hostname, and vendor)
Export scan results to CSV

## 🖥️ Requirements
- Python 3.7+
- colorama (for colored output)
- speedtest-cli (auto-installs if missing)
  
## 🖥️ Steps
- Install Python 3 if not already installed: https://www.python.org/downloads/
- Install colorama (if not already)
- Run the script as Administrator (required for network changes)

## Troubleshooting
- The network scan downloads the IEEE OUI vendor list (oui.txt) on first run for MAC vendor lookup.
- For best results, run the script in a terminal with administrator privileges.
- The script is intended for Windows only.
