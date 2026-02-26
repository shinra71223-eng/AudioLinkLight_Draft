# TD Textport test using pyserial directly (bypasses Serial DAT)
import sys, os
# Add pyserial from PlatformIO's Python environment
pio_sp = os.path.expanduser('~/.platformio/penv/Lib/site-packages')
if pio_sp not in sys.path:
    sys.path.insert(0, pio_sp)
import serial
import time

# Close TD Serial DAT first
s = op('/AudioLinkLight_V01/TEST_SCREEN/serial_out')
s.par.active = False

# Open via pyserial
ser = serial.Serial()
ser.port = 'COM6'
ser.baudrate = 921600
ser.timeout = 2
ser.write_timeout = 2
ser.dtr = False
ser.rts = False
ser.open()

# Send 880 LEDs green
NUM = 880
buf = bytearray(4 + NUM * 3)
buf[0], buf[1] = 0x55, 0xAA
buf[2], buf[3] = NUM & 0xFF, (NUM >> 8) & 0xFF
for i in range(NUM):
    buf[4 + i*3 + 1] = 200  # G

w = ser.write(buf)
ser.flush()
print('pyserial write:', w)

time.sleep(0.5)
ser.close()
print('Done - LEDs should be GREEN')
