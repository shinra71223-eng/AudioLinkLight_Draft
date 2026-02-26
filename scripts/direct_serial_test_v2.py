"""Direct pyserial test v2 - no DTR reset, detailed diagnostics"""
import serial
import time
import sys

PORT = 'COM6'
BAUD = 921600

print(f"Opening {PORT} (no DTR reset)...")
try:
    ser = serial.Serial()
    ser.port = PORT
    ser.baudrate = BAUD
    ser.timeout = 2
    ser.write_timeout = 2
    ser.dtr = False
    ser.rts = False
    ser.open()
except Exception as e:
    print(f"FAILED: {e}")
    sys.exit(1)

print(f"Port opened. DSR={ser.dsr}, CTS={ser.cts}, CD={ser.cd}")

# Drain any pending data
if ser.in_waiting:
    old = ser.read(ser.in_waiting)
    print(f"Drained {len(old)} bytes: {old[:50]}")

# Small test first: 1 LED green (7 bytes)
print("\n--- Test 1: 1 LED (7 bytes) ---")
small = bytes([0x55, 0xAA, 1, 0, 0, 200, 0])
w = ser.write(small)
ser.flush()
print(f"Written: {w}")
time.sleep(0.5)

# Full test: 880 LEDs green (2644 bytes)
print("\n--- Test 2: 880 LEDs (2644 bytes) ---")
NUM = 880
buf = bytearray(4 + NUM * 3)
buf[0], buf[1] = 0x55, 0xAA
buf[2], buf[3] = NUM & 0xFF, (NUM >> 8) & 0xFF
for i in range(NUM):
    buf[4 + i*3]     = 0
    buf[4 + i*3 + 1] = 200
    buf[4 + i*3 + 2] = 0

w = ser.write(buf)
ser.flush()
print(f"Written: {w}")
time.sleep(1.0)

# Check response
if ser.in_waiting:
    data = ser.read(ser.in_waiting)
    print(f"ESP32 response: {data.decode('utf-8', errors='replace')}")
else:
    print("No response from ESP32")

ser.close()
print("\nDone. Check LEDs.")
