# led_sender_88x10.py (Optimized for UNIT1/2/3)
import sys, os

# Add pyserial from PlatformIO env
_pio_sp = os.path.expanduser('~/.platformio/penv/Lib/site-packages')
if _pio_sp not in sys.path:
    sys.path.insert(0, _pio_sp)

import serial as _serial
import time as _time
import numpy as _np

def get_par(name, default):
    p = getattr(parent().par, name, None)
    return p.eval() if p is not None else default

COM_PORT    = get_par('Comport', 'COM1')
COM_BAUD    = get_par('Baudrate', 2000000)
SOURCE_TOP  = get_par('Sourcetop', 'led_source_u1')
LED_COLS    = 88
LED_ROWS    = 10
NUM_LEDS    = 880 # 固定

_ser = None
_header = bytes([0x55, 0xAA, NUM_LEDS & 0xFF, (NUM_LEDS >> 8) & 0xFF])
_last_reset_state = 0 # リセットボタン状態管理

def _open():
    global _ser
    port = get_par('Comport', COM_PORT)
    baud = get_par('Baudrate', COM_BAUD)
    
    if _ser is not None:
        if _ser.is_open and _ser.port == port and _ser.baudrate == baud:
            return True
        _close()

    try:
        s = _serial.Serial()
        s.port = port
        s.baudrate = baud
        s.timeout = 0
        s.write_timeout = 2
        s.dtr = False
        s.rts = False
        s.open()
        _time.sleep(0.3)
        s.reset_input_buffer()
        _ser = s
        print(f'[LED_88x10] Opened {port}')
        return True
    except Exception as e:
        print(f'[LED_88x10] Open ERROR: {e}')
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

def onFrameStart(frame):
    global _last_reset_state
    
    # --- RESET_Button 連動 ---
    reset_btn = op('../../RESET_Button')
    if reset_btn:
        curr_reset = reset_btn.panel.state
        if curr_reset == 1 and _last_reset_state == 0:
            print(f'[LED_88x10] Manual Reset Triggered')
            _close() # 次の_open()で再接続される
        _last_reset_state = curr_reset

    if not _open():
        return

    src_name = get_par('Sourcetop', SOURCE_TOP)
    src = op(src_name)
    if src is None: return

    pix = src.numpyArray(delayed=True)
    if pix is None: return

    # 確実に 88x10 にクロップ/スライス
    h, w = pix.shape[:2]
    rh = min(h, LED_ROWS)
    rw = min(w, LED_COLS)
    
    rgb = pix[:rh, :rw, :3]
    
    # 0.0-1.0 -> 0-255
    rgb_u8 = (_np.clip(rgb * 255.0, 0, 255)).astype(_np.uint8)
    
    payload = rgb_u8.tobytes()
    
    # バイト数が足りない場合は埋める (ファームウェアの 2640 バイトチェックをパスするため)
    expected = NUM_LEDS * 3
    if len(payload) < expected:
        payload += b'\x00' * (expected - len(payload))
    elif len(payload) > expected:
        payload = payload[:expected]
        
    try:
        _ser.write(_header + payload)
        if _ser.in_waiting > 100:
             _ser.read(_ser.in_waiting)
    except Exception as e:
        print(f'[LED_88x10] Write ERROR: {e}')
        _close()

def stop():
    _close()
    me.par.active = False
    print('[LED_88x10] Stopped')
