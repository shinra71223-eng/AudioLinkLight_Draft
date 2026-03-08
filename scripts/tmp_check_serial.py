import serial
import time

PORT = 'COM8'
BAUD = 2000000

print(f"Opening {PORT} at {BAUD}...")
try:
    with serial.Serial(PORT, BAUD, timeout=1) as ser:
        print("Listening for 5 seconds...")
        end_time = time.time() + 10
        while time.time() < end_time:
            line = ser.readline()
            if line:
                print(f"RECV: {line.decode().strip()}")
except Exception as e:
    print(f"ERROR: {e}")
