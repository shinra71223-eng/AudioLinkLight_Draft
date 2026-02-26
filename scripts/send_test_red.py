import time

s = op('/AudioLinkLight_V01/TEST_SCREEN/serial_out')
if not s.par.active:
    s.par.active = True
    time.sleep(2.0)  # Wait for ESP32 to reboot after DTR reset

num = 880
buf = bytearray(4 + num * 3)
buf[0], buf[1] = 0x55, 0xAA
buf[2], buf[3] = num & 0xFF, (num >> 8) & 0xFF
# Bright green - clearly different from dark-red waiting state
for i in range(num):
    buf[4 + i*3]   = 0    # R
    buf[4 + i*3+1] = 200  # G
    buf[4 + i*3+2] = 0    # B

result = s.sendBytes(bytes(buf))
print('sendBytes returned:', result, '  -> LEDs should turn bright GREEN if OK')
