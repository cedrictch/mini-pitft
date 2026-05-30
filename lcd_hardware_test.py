import time
import RPi.GPIO as GPIO
from RPLCD.i2c import CharLCD

# ==========================================
# 1. INITIALIZE HARDWARE (2004 I2C LCD & GPIO)
# ==========================================
# Configure LCD on its validated 0x27 address
lcd = CharLCD(i2c_expander='PCF8574', address=0x27, port=1, cols=20, rows=4)
lcd.clear()

# Use Broadcom GPIO pin numbering layout
GPIO.setmode(GPIO.BCM)

# Map buttons matching original Mini PiTFT hardware pins
BUTTON_TOP = 23
BUTTON_BOTTOM = 24

# Initialize buttons with internal pull-up resistors 
# (This keeps them HIGH normally; pressing them pulls the signal LOW to GND)
GPIO.setup(BUTTON_TOP, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUTTON_BOTTOM, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# ==========================================
# 2. DEFINE CUSTOM TEXT SYMBOLS
# ==========================================
# Custom solid blocks to create a dynamic visual notification alert box
ALERT_BLOCK = (
    0b11111,
    0b10001,
    0b10101,
    0b10101,
    0b10101,
    0b10101,
    0b10001,
    0b11111
)
lcd.create_char(0, ALERT_BLOCK)
BOX = chr(0)

# Initialize standard state landing message
lcd.write_string(f"--- BUTTON TEST ----\n\n  Press a Button...\nStatus: WAITING")

print("[*] 2004 LCD Button Test Adapter Running. Press Ctrl+C to exit.")

# ==========================================
# 3. INTERACTIVE RUNTIME LOOP
# ==========================================
try:
    while True:
        # Read the electrical state of both input lines (False means button is down)
        top_pressed = not GPIO.input(BUTTON_TOP)
        bottom_pressed = not GPIO.input(BUTTON_BOTTOM)

        if top_pressed and bottom_pressed:
            lcd.clear()
            lcd.cursor_pos = (0, 0)
            lcd.write_string(f"{BOX*20}")
            lcd.cursor_pos = (1, 0)
            lcd.write_string(" STATUS: BOTH DOWN  ")
            lcd.cursor_pos = (2, 0)
            lcd.write_string(" EMULATED TFT COLOR ")
            lcd.cursor_pos = (3, 0)
            lcd.write_string(f"   >>> GREEN <<<    ")
            time.sleep(0.1) # Micro debounce filter

        elif top_pressed:
            lcd.clear()
            lcd.cursor_pos = (0, 0)
            lcd.write_string("--- BUTTON TEST ----")
            lcd.cursor_pos = (1, 0)
            lcd.write_string(f" [{BOX}] TOP BUTTON    ")
            lcd.cursor_pos = (2, 0)
            lcd.write_string(" EMULATED TFT COLOR ")
            lcd.cursor_pos = (3, 0)
            lcd.write_string("    >>> RED <<<     ")
            time.sleep(0.1)

        elif bottom_pressed:
            lcd.clear()
            lcd.cursor_pos = (0, 0)
            lcd.write_string("--- BUTTON TEST ----")
            lcd.cursor_pos = (1, 0)
            lcd.write_string(f" [{BOX}] BOTTOM BUTTON ")
            lcd.cursor_pos = (2, 0)
            lcd.write_string(" EMULATED TFT COLOR ")
            lcd.cursor_pos = (3, 0)
            lcd.write_string("    >>> BLUE <<<    ")
            time.sleep(0.1)

        # Small pacing latency to prevent pegged CPU load spikes
        time.sleep(0.05)

except KeyboardInterrupt:
    lcd.clear()
    lcd.write_string("System Shutdown\nStatus: Offline")
    GPIO.cleanup()
    print("\n[*] GPIO lines released and LCD state closed cleanly.")
