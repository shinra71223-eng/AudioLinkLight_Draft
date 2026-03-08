import serial
import serial.tools.list_ports
import time

print("Scanning for ESP32 Heartbeat...")
ports = serial.tools.list_ports.comports()
for port in ports:
    print(f"Testing {port.device} ({port.description})...")
    try:
        with serial.Serial(port.device, 4000000, timeout=1) as ser:
            time.sleep(1.5) # Wait for heartbeat
            res = ser.read(100).decode(errors='ignore')
            if "STATUS:ALIVE" in res or "DIAG:START" in res:
                print(f"MATCH FOUND: {port.device} is active!")
            else:
                print(f"  No heartbeat on {port.device}")
    except Exception as e:
        print(f"  Could not open {port.device}: {e}")
