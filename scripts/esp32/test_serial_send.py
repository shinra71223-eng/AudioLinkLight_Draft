import serial
import time

COM_PORT = 'COM19'
COM_BAUD = 2000000
NUM_TOTAL_PIXELS = 3612

try:
    print(f"Opening {COM_PORT} at {COM_BAUD} baud...")
    s = serial.Serial()
    s.port = COM_PORT
    s.baudrate = COM_BAUD
    s.timeout = 0.5
    # For ESP32-S3 USB-CDC, DTR/RTS control the connection/reset behavior
    s.dtr = True
    s.rts = True
    s.open()
    time.sleep(0.5)
    s.dtr = False
    s.rts = False
    time.sleep(1.0)
    s.reset_input_buffer()
    
    print("Reading initial output before sending payload...")
    start_time = time.time()
    while time.time() - start_time < 3.0:
        data = s.readline()
        if data:
            print(f"ESP32 INIT: {data.decode('utf-8', errors='replace').strip()}")
            
    print("Sending payload...")
    payload = bytearray([0x55, 0xAA, NUM_TOTAL_PIXELS & 0xFF, (NUM_TOTAL_PIXELS >> 8) & 0xFF])
    payload.extend(b'\x00\x40\x00' * NUM_TOTAL_PIXELS) # Dark green
    
    s.write(bytes(payload))
    s.flush()
    print("Payload sent. Monitoring serial output for 5 seconds...")
    
    start_time = time.time()
    while time.time() - start_time < 5.0:
        data = s.readline()
        if data:
            print(f"ESP32 RUN: {data.decode('utf-8', errors='replace').strip()}")
            
    s.close()
    print("Done.")

except Exception as e:
    print(f"EXCEPTION: {e}")
