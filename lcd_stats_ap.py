import time
import subprocess
from RPLCD.i2c import CharLCD

# ==========================================
# 1. INITIALIZE THE 2004 I2C LCD
# ==========================================
lcd = CharLCD(i2c_expander='PCF8574', address=0x27, port=1, cols=20, rows=4)
lcd.clear()

def get_ap_metrics():
    # 1. Extract the specific Access Point Gateway IP (wlan0)
    try:
        cmd = "ip -br address show wlan0 | awk '{print $3}' | cut -d/ -f1 | head -n1"
        IP = subprocess.check_output(cmd, shell=True).decode("utf-8").strip()
        if not IP:
            IP = "10.42.0.1"
    except Exception:
        IP = "10.42.0.1"

    # 2. Extract Active Connection Profile SSID cleanly via nmcli active connections
    try:
        cmd = "nmcli -t -f NAME connection show --active | grep -v -E 'lo|eth|enx|docker|veth' | head -n1"
        SSID = subprocess.check_output(cmd, shell=True).decode("utf-8").strip()
        if not SSID:
            SSID = "RaspAP"
    except Exception:
        SSID = "RaspAP"

    # 3. Count Active Clients via the Kernel ARP Table (Extremely reliable fallback)
    try:
        # Reads the system ARP table, filters out the header row, and filters specifically for wlan0 entries
        cmd = "cat /proc/net/arp | grep 'wlan0' | wc -l"
        clients = subprocess.check_output(cmd, shell=True).decode("utf-8").strip()
        if not clients or not clients.isdigit():
            clients = "0"
    except Exception:
        clients = "0"

    # 4. Read Live Transmission Traffic from the true wlan0 device pipeline
    try:
        cmd = "cat /proc/net/dev | grep 'wlan0:' | awk '{print $10}'"
        raw_bytes = subprocess.check_output(cmd, shell=True).decode("utf-8").strip()
        
        if raw_bytes and raw_bytes.isdigit():
            mb_sent = float(raw_bytes) / (1024 * 1024)
            DataTx = f"Tx: {mb_sent:.1f} MB"
        else:
            DataTx = "Tx: 0.0 MB"
    except Exception:
        DataTx = "Tx: 0.0 MB"

    return IP, SSID, clients, DataTx

# ==========================================
# 2. RUNTIME TELEMETRY REFRESH LOOP
# ==========================================
print("[*] ARP-Linked RaspAP Engine Active. Press Ctrl+C to terminate.")

try:
    while True:
        IP, SSID, clients, DataTx = get_ap_metrics()
        
        lcd.clear()
        
        # Row 0: Network Name
        lcd.cursor_pos = (0, 0)
        lcd.write_string(f"SSID: {SSID[:14]}")
        
        # Row 1: Access Point Gateway IP Address
        lcd.cursor_pos = (1, 0)
        lcd.write_string(f"IP: {IP[:16]}")
        
        # Row 2: Live Client Station Counter
        lcd.cursor_pos = (2, 0)
        lcd.write_string(f"STATIONS: {clients}")
        
        # Row 3: Transmitted Data Volume
        lcd.cursor_pos = (3, 0)
        lcd.write_string(f"{DataTx}")
        
        time.sleep(2.0)

except KeyboardInterrupt:
    lcd.clear()
    lcd.write_string("AP Monitor Closed\nStatus: Offline")
    print("\n[*] Layout closed cleanly.")
