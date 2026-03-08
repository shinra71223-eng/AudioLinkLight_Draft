# led_sender_pyserial.py
# ================================================================
# TouchDesigner Execute DAT - March 8th Logic Baseline (2Mbps)
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
COM_PORT    = 'COM17'             # Port for single unit
COM_BAUD    = 2000000
SOURCE_TOP  = 'led_source'
LED_COLS    = 88
LED_ROWS    = 10
NUM_LEDS    = LED_COLS * LED_ROWS
# ----------------

_ser = None
# 0x55 0xAA + 2 bytes for length
_header = bytes([0x55, 0xAA, NUM_LEDS & 0xFF, (NUM_LEDS >> 8) & 0xFF])

def _open():
    global _ser
    if _ser is not None and _ser.is_open:
        return True
    try:
        s = _serial.Serial()
        s.port = COM_PORT
        s.baudrate = COM_BAUD
        s.timeout = 0
        s.write_timeout = 2
        s.dtr = False
        s.rts = False
        s.open()
        _time.sleep(0.3)
        s.reset_input_buffer()
        _ser = s
        print(f'[led] opened {COM_PORT} at {COM_BAUD} (3/8 Logic Port)')
        return True
    except Exception as e:
        print(f'[led] open ERROR: {e}')
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

def _send_frame(pixels):
    global _ser
    # 3月8日版のESP32側ロジック (y_img = 9 - y_physical) は、
    # TDのTOPメモリ並び (Bottom-to-Top) をそのまま受け取る前提。
    # そのため Python 側での上下反転は不要。
    
    h, w = pixels.shape[:2]
    rh = min(h, LED_ROWS)
    rw = min(w, LED_COLS)
    
    # Extract RGB
    rgb = pixels[:rh, :rw, :3]
    
    rgb = (rgb * 255.0)
    _np.clip(rgb, 0, 255, out=rgb)
    rgb_u8 = rgb.astype(_np.uint8)
    
    payload = rgb_u8.tobytes()
    expected = NUM_LEDS * 3
    if len(payload) < expected:
        payload += b'\x00' * (expected - len(payload))
    elif len(payload) > expected:
        payload = payload[:expected]
        
    try:
        _ser.write(_header + payload)
        # 溜まっている ACK ('K') を適宜掃き出す
        if _ser.in_waiting > 100:
             _ser.read(_ser.in_waiting)
    except Exception as e:
        print(f'[led] write ERROR: {e}')
        _close()

def onFrameStart(frame):
    if not _open():
        return
    src = op(SOURCE_TOP)
    if src is None:
        return
    # numpyArray() はデフォルトで [0,0] が左下
    pix = src.numpyArray(delayed=True)
    if pix is None:
        return
    _send_frame(pix)

def stop():
    _close()
    me.par.active = False
    print('[led] stopped')
