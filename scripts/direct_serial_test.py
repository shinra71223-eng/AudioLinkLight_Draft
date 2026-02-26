"""Direct pyserial test - bypasses TouchDesigner entirely"""
import serial
import time
import sys

PORT = 'COM6'
BAUD = 921600
NUM = 880

print(f"Opening {PORT} at {BAUD}...")
try:
    ser = serial.Serial(PORT, BAUD, timeout=2)
except Exception as e:
    print(f"FAILED to open: {e}")
    sys.exit(1)

print("Port opened. Waiting 2s for ESP32 boot...")
time.sleep(2.0)

# Build frame: 0x55 0xAA count_lo count_hi + RGB*880
buf = bytearray(4 + NUM * 3)
buf[0] = 0x55
buf[1] = 0xAA
buf[2] = NUM & 0xFF
buf[3] = (NUM >> 8) & 0xFF
# Fill with GREEN
for i in range(NUM):
    buf[4 + i*3]     = 0    # R
    buf[4 + i*3 + 1] = 200  # G
    buf[4 + i*3 + 2] = 0    # B

print(f"Sending {len(buf)} bytes...")
written = ser.write(buf)
print(f"Written: {written} bytes")
ser.flush()

print("Waiting 1s for response...")
time.sleep(1.0)

# Read any debug output
if ser.in_waiting:
    data = ser.read(ser.in_waiting)
    print(f"ESP32 says: {data.decode('utf-8', errors='replace')}")
else:
    print("No response from ESP32")

ser.close()
print("Done. LEDs should be GREEN if working.")
