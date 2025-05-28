import os
import subprocess
import sys
import time
from datetime import datetime

from colorama import Fore

def run_cmd(cmd, show_output=True):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=not show_output, text=True)
        if show_output and result.stdout:
            print(result.stdout)
        if show_output and result.stderr:
            print(result.stderr)
        return result.returncode
    except Exception as e:
        print(f"Error running command: {e}")
        return 1

def pause():
    input("Press Enter to continue...")

def get_adapter():
    result = subprocess.run('netsh interface show interface', shell=True, capture_output=True, text=True)
    lines = result.stdout.splitlines()
    # Find header to determine column positions
    header_idx = None
    for idx, line in enumerate(lines):
        if 'Admin State' in line and 'State' in line and 'Interface Name' in line:
            header_idx = idx
            break
    if header_idx is not None:
        for line in lines[header_idx+1:]:
            if not line.strip():
                continue
            # Split by columns (fixed width)
            parts = line.split()
            # The adapter name may have spaces, so join the remaining parts
            if len(parts) >= 4 and parts[1] == 'Connected':
                # Adapter name is everything after the 3rd column
                adapter_name = ' '.join(parts[3:])
                return adapter_name
    return None

def show_config(adapter):
    print("*************** [ipconfig /all] ***************")
    run_cmd("ipconfig /all")
    print("**********************************************")
    pause()

def set_static_ip(adapter):
    print("====== [Set Static IP] ======")
    run_cmd(f'netsh interface ip show config name="{adapter}" | findstr "IP Address"', True)
    run_cmd(f'netsh interface ip show config name="{adapter}" | findstr "Subnet"', True)
    run_cmd(f'netsh interface ip show config name="{adapter}" | findstr "Gateway"', True)
    ip = input("Enter IP Address (e.g. 192.168.1.100): ")
    mask = input("Enter Subnet Mask (e.g. 255.255.255.0): ")
    gateway = input("Enter Gateway (e.g. 192.168.1.1): ")
    dns1 = input("Enter Primary DNS (e.g. 8.8.8.8): ")
    dns2 = input("Enter Secondary DNS (e.g. 8.8.4.4): ")
    print("Setting Static IP...")
    run_cmd(f'netsh interface ip set address name="{adapter}" static {ip} {mask} {gateway} 1')
    run_cmd(f'netsh interface ip set dns name="{adapter}" static {dns1} primary')
    run_cmd(f'netsh interface ip add dns name="{adapter}" {dns2} index=2')
    print("Static IP configured!")
    pause()

def set_dhcp(adapter):
    print("====== [Set DHCP] ======")
    print("Configuring adapter for automatic IP...")
    run_cmd(f'netsh interface ip set address name="{adapter}" dhcp')
    run_cmd(f'netsh interface ip set dns name="{adapter}" dhcp')
    print("DHCP enabled! Your network will assign IP automatically.")
    pause()

def change_dns(adapter):
    print("====== [Change DNS Only] ======")
    run_cmd(f'netsh interface ip show config name="{adapter}" | findstr "DNS"', True)
    print("1. Google DNS (8.8.8.8, 8.8.4.4)")
    print("2. Cloudflare DNS (1.1.1.1, 1.0.0.1)")
    print("3. OpenDNS (208.67.222.222, 208.67.220.220)")
    print("4. Custom DNS")
    print("5. Back to Menu")
    choice = input("Choose DNS (1-5): ")
    if choice == "1":
        run_cmd(f'netsh interface ip set dns name="{adapter}" static 8.8.8.8 primary')
        run_cmd(f'netsh interface ip add dns name="{adapter}" 8.8.4.4 index=2')
        print("Google DNS applied!")
    elif choice == "2":
        run_cmd(f'netsh interface ip set dns name="{adapter}" static 1.1.1.1 primary')
        run_cmd(f'netsh interface ip add dns name="{adapter}" 1.0.0.1 index=2')
        print("Cloudflare DNS applied!")
    elif choice == "3":
        run_cmd(f'netsh interface ip set dns name="{adapter}" static 208.67.222.222 primary')
        run_cmd(f'netsh interface ip add dns name="{adapter}" 208.67.220.220 index=2')
        print("OpenDNS applied!")
    elif choice == "4":
        primary = input("Enter Primary DNS: ")
        secondary = input("Enter Secondary DNS: ")
        run_cmd(f'netsh interface ip set dns name="{adapter}" static {primary} primary')
        run_cmd(f'netsh interface ip add dns name="{adapter}" {secondary} index=2')
        print("Custom DNS applied!")
    pause()

def diagnostics():
    print(Fore.CYAN +  "====== [Network Diagnostics] ======")
    print("1. Ping Test (8.8.8.8)")
    print("2. Traceroute Test")
    print("3. Flush DNS Cache")
    print("4. Reset TCP/IP Stack")
    print("5. Back to Menu")
    choice = input("Choose (1-5): ")
    if choice == "1":
        run_cmd("ping 8.8.8.8 -n 4")
    elif choice == "2":
        run_cmd("tracert 8.8.8.8")
    elif choice == "3":
        run_cmd("ipconfig /flushdns")
        print("DNS cache flushed!")
    elif choice == "4":
        run_cmd("netsh int ip reset")
        print("TCP/IP stack reset!")
    pause()

def network_reset():
    print("====== [Network Reset] ======")
    print("This will reset all network settings.")
    print("Your network connections may be temporarily interrupted.")
    print()
    print("1. Proceed with Reset")
    print("2. Back to Menu")
    choice = input("Choose (1-2): ")
    if choice == "1":
        print("Resetting network components...")
        run_cmd("netsh winsock reset")
        run_cmd("netsh int ip reset")
        run_cmd("ipconfig /flushdns")
        run_cmd("ipconfig /release")
        run_cmd("ipconfig /renew")
        print("Network reset complete!")
        print("You may need to restart your computer for changes to take effect.")
    pause()

def list_adapters():
    result = subprocess.run('netsh interface show interface', shell=True, capture_output=True, text=True)
    lines = result.stdout.splitlines()
    header_idx = None
    for idx, line in enumerate(lines):
        if 'Admin State' in line and 'State' in line and 'Interface Name' in line:
            header_idx = idx
            break
    adapters = []
    if header_idx is not None:
        for line in lines[header_idx+1:]:
            if not line.strip():
                continue
            parts = line.split()
            if len(parts) >= 4:
                # Adapter name is everything after the 3rd column
                adapter_name = ' '.join(parts[3:])
                state = parts[1]
                adapters.append((adapter_name, state))
    return adapters

def check_dns_connectivity():
    import socket
    try:
        # Try to resolve a common domain
        socket.gethostbyname('www.google.com')
        return True
    except Exception:
        return False

def speed_test():
    print("====== [Network Speed Test] ======")
    if not check_dns_connectivity():
        print("DNS resolution failed. Please check your internet connection or DNS settings before running the speed test.")
        pause()
        return
    try:
        import speedtest
    except ImportError:
        print("speedtest module not found. Installing now...")
        run_cmd("pip install speedtest-cli")
        try:
            import speedtest
        except ImportError:
            print("Failed to import speedtest after installation. Please restart the script.")
            pause()
            return
    try:
        st = speedtest.Speedtest()
        print("Finding best server...")
        st.get_best_server()
        print("Testing download speed...")
        download = st.download() / 1_000_000  # Mbps
        print("Testing upload speed...")
        upload = st.upload() / 1_000_000  # Mbps
        print(f"Download speed: {download:.2f} Mbps")
        print(f"Upload speed: {upload:.2f} Mbps")
        print(f"Ping: {st.results.ping:.2f} ms")
    except Exception as e:
        print(f"Speed test failed: {e}")
    pause()

def scan_network():
    import socket
    import threading
    import csv
    import re
    print("====== [Network Scan: Hostname, IP, MAC, Vendor] ======")
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        subnet = '.'.join(local_ip.split('.')[:3])
        print(f"Scanning subnet: {subnet}.0/24")
    except Exception as e:
        print(f"Could not determine local subnet: {e}")
        pause()
        return
    # Download OUI vendor list if not present
    oui_file = "oui.txt"
    if not os.path.exists(oui_file):
        print("Downloading MAC vendor list (IEEE OUI)...")
        import urllib.request
        try:
            urllib.request.urlretrieve(
                "https://standards-oui.ieee.org/oui/oui.txt", oui_file)
            print("OUI vendor list downloaded.")
        except Exception as e:
            print(f"Failed to download OUI list: {e}")
            oui_file = None
    # Parse OUI file for vendor lookup
    oui_dict = {}
    if oui_file and os.path.exists(oui_file):
        with open(oui_file, encoding="utf-8", errors="ignore") as f:
            for line in f:
                if '(hex)' in line:
                    parts = line.split('(hex)')
                    mac = parts[0].strip().replace('-', ':').upper()
                    vendor = parts[1].strip()
                    oui_dict[mac] = vendor
    def lookup_vendor(mac):
        if not oui_dict:
            return "-"
        mac_prefix = ':'.join(mac.upper().split(':')[:3])
        return oui_dict.get(mac_prefix, "-")
    def ping_and_collect(ip):
        subprocess.run(f"ping -n 1 -w 100 {ip}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("Pinging all addresses in subnet to update ARP table (parallel)...")
    threads = []
    for i in range(1, 255):
        ip = f"{subnet}.{i}"
        t = threading.Thread(target=ping_and_collect, args=(ip,))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
    print("Collecting ARP table...")
    arp_result = subprocess.run("arp -a", shell=True, capture_output=True, text=True)
    lines = arp_result.stdout.splitlines()
    print(f"{'IP Address':<16} {'MAC Address':<20} {'Host Name':<30} {'Vendor'}")
    print("-"*90)
    results = []
    mac_regex = re.compile(r"([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})")
    for line in lines:
        if '-' in line and '.' in line:
            parts = line.split()
            if len(parts) >= 2 and mac_regex.match(parts[1]):
                ip_addr = parts[0]
                mac_addr = parts[1].replace('-', ':').upper()
                try:
                    host = socket.gethostbyaddr(ip_addr)[0]
                except:
                    host = "-"
                vendor = lookup_vendor(mac_addr)
                print(f"{ip_addr:<16} {mac_addr:<20} {host:<30} {vendor}")
                results.append((ip_addr, mac_addr, host, vendor))
    print("\nWould you like to export the results to CSV?")
    export = input("Type 'y' to export, anything else to skip: ").strip().lower()
    if export == 'y':
        filename = f"network_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["IP Address", "MAC Address", "Host Name", "Vendor"])
            writer.writerows(results)
        print(f"Results exported to {filename}")
    pause()

def main():
    from colorama import Fore, Back, Style
    while True:
        adapters = list_adapters()
        if not adapters:
            print("No network adapters found.")
            pause()
            continue
        print(Fore.CYAN +  "_____________________________________")
        print(Fore.CYAN +  "_____________┳┓┏┓┳┳┓┏┓┓┏_____________")
        print(Fore.CYAN +  "_____________┃┃┣ ┃┃┃┃┃┗┫_____________")
        print(Fore.CYAN +  "_____________┛┗┗┛┛ ┗┣┛┗┛_____________")
        print(Fore.CYAN +  "Network Management tool Python script")
        print(Fore.CYAN +  "_____________________________________")
        print("Available Network Adapters:")
        for idx, (name, state) in enumerate(adapters):
            print(f"{idx+1}. {name} [{state}]")
        try:
            choice = int(input("Select adapter number to manage (or 0 to refresh): "))
        except ValueError:
            print("Invalid input.")
            pause()
            continue
        if choice == 0:
            continue
        if 1 <= choice <= len(adapters):
            adapter = adapters[choice-1][0]
        else:
            print("Invalid choice.")
            pause()
            continue
        print(f"Current Adapter: [{adapter}]")
        print(Fore.CYAN +  "_____________________________________________________________")
        print("0. Show Full Network Config (ipconfig /all)")
        print("1. Set Static IP + DNS (Manual)")
        print("2. Set DHCP (Automatic IP)")
        print("3. Change DNS Only")
        print("6. Ping Test and Diagnostics")
        print("7. Scan Network (Show Hostname, IP, MAC)")
        print("10. Network Reset (Repair)")
        print("11. Speed Test")
        print("12. Exit")
        print("_____________________________________________________________")
        menu_choice = input("Choose (0-12): ")
        if menu_choice == "0":
            show_config(adapter)
        elif menu_choice == "1":
            set_static_ip(adapter)
        elif menu_choice == "2":
            set_dhcp(adapter)
        elif menu_choice == "3":
            change_dns(adapter)
        elif menu_choice == "6":
            diagnostics()
        elif menu_choice == "7":
            scan_network()
        elif menu_choice == "10":
            network_reset()
        elif menu_choice == "11":
            speed_test()
        elif menu_choice == "12":
            sys.exit(0)
        else:
            print("Invalid choice.")
            pause()

if __name__ == "__main__":
    if os.name != "nt":
        print("This script is intended for Windows only.")
        sys.exit(1)
    main()