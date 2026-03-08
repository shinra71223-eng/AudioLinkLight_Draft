import serial
import time

COM_PORT = 'COM19'
COM_BAUD = 2000000
NUM_TOTAL_PIXELS = 3612

try:
    print(f"Turning OFF LEDs on {COM_PORT}...")
    s = serial.Serial()
    s.port = COM_PORT
    s.baudrate = COM_BAUD
    s.timeout = 0.5
    s.open()
    time.sleep(0.5)
    s.reset_input_buffer()
    
    # 完全に消灯する（オール0）
    payload = bytearray([0x55, 0xAA, NUM_TOTAL_PIXELS & 0xFF, (NUM_TOTAL_PIXELS >> 8) & 0xFF])
    payload.extend(b'\x00\x00\x00' * NUM_TOTAL_PIXELS)
    
    s.write(bytes(payload))
    s.flush()
    print("OFF signal sent.")
    s.close()

except Exception as e:
    print(f"EXCEPTION: {e}")
