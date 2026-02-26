# led_sender_pyserial.py
# ================================================================
# TouchDesigner Execute DAT - pyserial based LED sender
# ================================================================
# Serial DAT (sendBytes) does not work with ESP32-S3 USB-CDC.
# This script uses pyserial directly for reliable communication.
#
# Protocol: [0x55][0xAA][count_lo][count_hi][R0][G0][B0]...[Rn][Gn][Bn]
# count = 880 (88 cols x 10 rows)
# ================================================================

import sys, os

# Add pyserial from PlatformIO env
_pio_sp = os.path.expanduser('~/.platformio/penv/Lib/site-packages')
if _pio_sp not in sys.path:
    sys.path.insert(0, _pio_sp)

import serial as _serial
import time as _time
import numpy as _np

# ---- CONFIG ----
COM_PORT    = 'COM6'
COM_BAUD    = 921600
SOURCE_TOP  = '/AudioLinkLight_V01/TEST_SCREEN2/cyber_clock_v2'  # absolute path OK across bases
LED_COLS    = 88
LED_ROWS    = 10
NUM_LEDS    = LED_COLS * LED_ROWS  # 880
BRIGHTNESS  = 1.0                 # send full range; ESP32 FastLED.setBrightness() handles overall level
ACK_TIMEOUT = 0.060               # 60ms max wait for ACK (26ms show + 23ms TX + margin)
# ----------------

_ser = None
_waiting_ack  = False             # True = frame sent, waiting for ACK from ESP32
_ack_deadline = 0.0               # perf_counter deadline for ACK timeout
_header = bytes([0x55, 0xAA, NUM_LEDS & 0xFF, (NUM_LEDS >> 8) & 0xFF])

def _open():
    global _ser, _waiting_ack
    if _ser is not None and _ser.is_open:
        return True
    try:
        s = _serial.Serial()
        s.port = COM_PORT
        s.baudrate = COM_BAUD
        s.timeout = 0.1         # read timeout for ACK
        s.write_timeout = 2
        s.dtr = False
        s.rts = False
        s.open()
        _time.sleep(0.3)          # let USB-CDC stabilise
        if s.in_waiting:
            s.read(s.in_waiting)  # drain stale data
        _ser = s
        _waiting_ack = False
        print(f'[led_sender] opened {COM_PORT}')
        return True
    except Exception as e:
        print(f'[led_sender] open error: {e}')
        _ser = None
        return False

def _close():
    global _ser
    if _ser is not None:
        try:
            _ser.close()
        except:
            pass
        _ser = None
        print('[led_sender] closed')

def _send_frame(pixels):
    """Convert TOP numpyArray (float32 RGBA, shape HxWx4) to protocol bytes and send."""
    global _ser
    # pixels shape: (height, width, 4) float32 RGBA, values 0.0-1.0
    h, w = pixels.shape[:2]
    rh = min(h, LED_ROWS)
    rw = min(w, LED_COLS)

    # Slice to needed region, take RGB only (drop A), flip Y (TD is bottom-up)
    rgb = pixels[:rh, :rw, :3]
    rgb = rgb[::-1, :, :]               # flip rows (bottom-up → top-down)

    # Scale to 0-255, apply brightness, clip, convert to uint8
    rgb = (rgb * 255.0 * BRIGHTNESS)
    _np.clip(rgb, 0, 255, out=rgb)
    rgb_u8 = rgb.astype(_np.uint8)

    # Flatten to bytes: row-major R,G,B per pixel
    payload = rgb_u8.tobytes()

    # Pad if fewer pixels than NUM_LEDS
    expected = NUM_LEDS * 3
    if len(payload) < expected:
        payload += b'\x00' * (expected - len(payload))

    try:
        _ser.write(_header + payload)
        _ser.flush()
    except Exception as e:
        print(f'[led_sender] write error: {e}')
        _close()

def _check_ack():
    """Drain any bytes from ESP32 (ACK 'K' or garbage)."""
    if _ser is None or not _ser.is_open:
        return
    try:
        if _ser.in_waiting > 0:
            _ser.read(_ser.in_waiting)
    except:
        pass

# ---- Execute DAT callbacks ----

def onFrameStart(frame):
    global _waiting_ack, _ack_deadline
    if not _open():
        return

    now = _time.perf_counter()

    # Check for ACK — clears waiting_ack flag
    if _waiting_ack:
        try:
            if _ser.in_waiting > 0:
                data = _ser.read(_ser.in_waiting)
                if b'K' in data:
                    _waiting_ack = False
        except:
            pass
        # Timeout fallback: if ACK didn't arrive within ACK_TIMEOUT, send anyway
        if _waiting_ack and (now < _ack_deadline):
            return  # still waiting, skip this frame

    src = op(SOURCE_TOP)
    if src is None:
        return
    pix = src.numpyArray(delayed=False)
    if pix is None:
        return

    _send_frame(pix)
    _waiting_ack = True
    _ack_deadline = now + ACK_TIMEOUT

def onFrameEnd(frame):
    return

def onPlayStateChange(state):
    return

def onDeviceChange():
    return

def onProjectPreSave():
    return

def onProjectPostSave():
    return

# ---- Manual test functions ----

def test_solid(r=0, g=200, b=0):
    if not _open():
        return
    buf = bytearray(4 + NUM_LEDS * 3)
    buf[0], buf[1] = 0x55, 0xAA
    buf[2] = NUM_LEDS & 0xFF
    buf[3] = (NUM_LEDS >> 8) & 0xFF
    for i in range(NUM_LEDS):
        buf[4 + i*3]     = r
        buf[4 + i*3 + 1] = g
        buf[4 + i*3 + 2] = b
    try:
        _ser.write(bytes(buf))
        _ser.flush()
        print(f'[led_sender] test_solid R={r} G={g} B={b}')
    except Exception as e:
        print(f'[led_sender] error: {e}')
        _close()

def test_off():
    test_solid(0, 0, 0)

def stop():
    _close()
    me.par.active = False
    print('[led_sender] stopped')
