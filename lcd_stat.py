import time
import subprocess
from RPLCD.i2c import CharLCD

# Initialize the 2004 I2C LCD
# (Verify your exact I2C address using 'i2cdetect -y 1', usually 0x27 or 0x3f)
lcd = CharLCD(i2c_expander='PCF8574', address=0x27, port=1, cols=20, rows=4)
lcd.clear()

def get_system_metrics():
    # Shell scripts for system monitoring (derived from standard telemetry hooks)
    cmd = "hostname -I | cut -d' ' -f1"
    IP = subprocess.check_output(cmd, shell=True).decode("utf-8").strip()
    
    cmd = "top -bn1 | grep 'Cpu(s)' | awk '{print $2 + $4}'"
    CPU = subprocess.check_output(cmd, shell=True).decode("utf-8").strip()
    
    cmd = "free -m | awk 'NR==2{printf \"Mem: %s/%sMB %.0f%%\", $3,$2,$3*100/$2 }'"
    MemUsage = subprocess.check_output(cmd, shell=True).decode("utf-8").strip()
    
    cmd = "df -h | awk '$NF==\"/\"{printf \"Disk: %s/%s (%s)\", $3,$2,$5}'"
    Disk = subprocess.check_output(cmd, shell=True).decode("utf-8").strip()
    
    return IP, CPU, MemUsage, Disk

print("[*] LCD Metric Alignment Engine running. Press Ctrl+C to stop.")

try:
    while True:
        IP, CPU, MemUsage, Disk = get_system_metrics()
        
        # Clear screen for fresh data frame write
        lcd.clear()
        
        # Format metrics explicitly to fit the 20-character width constraint
        lcd.cursor_pos = (0, 0)
        lcd.write_string(f"IP: {IP[:16]}")
        
        lcd.cursor_pos = (1, 0)
        lcd.write_string(f"CPU Load: {CPU[:5]}%")
        
        lcd.cursor_pos = (2, 0)
        lcd.write_string(f"{MemUsage[:20]}")
        
        lcd.cursor_pos = (3, 0)
        lcd.write_string(f"{Disk[:20]}")
        
        # Balance data updates with a 2-second sleep cycle
        time.sleep(2.0)

except KeyboardInterrupt:
    lcd.clear()
    lcd.write_string("Monitor Stopped\nStatus: Offline")
    print("\n[*] LCD Monitor terminated safely.")

