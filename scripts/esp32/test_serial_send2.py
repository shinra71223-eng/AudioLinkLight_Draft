import serial
import time

COM_PORT = 'COM19'
COM_BAUD = 2000000
NUM_TOTAL_PIXELS = 3612
TEST_BRIGHTNESS = 10  # 0-255

try:
    print(f"Opening {COM_PORT}...")
    s = serial.Serial()
    s.port = COM_PORT
    s.baudrate = COM_BAUD
    s.timeout = 0
    s.dtr = False
    s.rts = False
    s.open()
    time.sleep(0.5)
    s.reset_input_buffer()
    
    print("Sending payload...")
    payload = bytearray([0x55, 0xAA, NUM_TOTAL_PIXELS & 0xFF, (NUM_TOTAL_PIXELS >> 8) & 0xFF])
    # Solid blue (dimmed)
    payload.extend(bytes([0, 0, TEST_BRIGHTNESS]) * NUM_TOTAL_PIXELS)
    
    s.write(bytes(payload))
    s.flush()
    print("Payload sent. Waiting for ACK ('K')...")
    
    start_time = time.time()
    ack_received = False
    while time.time() - start_time < 2.0:
        data = s.read(10)
        if b'K' in data:
            print(">>> SUCCESS: ACK 'K' received from ESP32-S3! System is working perfectly.")
            ack_received = True
            break
        elif data:
            print(f"Received unknown data: {data}")
        time.sleep(0.01)
        
    if not ack_received:
        print(">>> ERROR: No ACK received.")

    s.close()
    print("Done.")

except Exception as e:
    print(f"EXCEPTION: {e}")
