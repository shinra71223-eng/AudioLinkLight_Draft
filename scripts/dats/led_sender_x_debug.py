# led_exec_x script (Debug version)
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

COM_PORT    = get_par('Comport', 'COM8')
COM_BAUD    = get_par('Baudrate', 2000000)
SOURCE_TOP  = get_par('Sourcetop', 'led_source_USB')

_ser = None
_last_send = 0.0

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
        print(f'[LED_X] Opened {port}')
        return True
    except Exception as e:
        print(f'[LED_X] Open ERROR: {e}')
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
    global _last_send, _ser
    
    # 30FPS制限
    now = _time.perf_counter()
    if now - _last_send < 0.033:
        return

    src_name = get_par('Sourcetop', SOURCE_TOP)
    src = op(src_name)
    
    f_int = int(frame)
    
    if src is None:
        if f_int % 60 == 0:
            print(f'[LED_X] ERROR: Source TOP "{src_name}" NOT FOUND')
        return

    cols = get_par('Ledcols', 81)
    rows = get_par('Ledrows', 12)
    if src.width != cols or src.height != rows:
        if f_int % 60 == 0:
            print(f'[LED_X] WARNING: Res mismatch! TOP:{src.width}x{src.height} vs Expected:{cols}x{rows}')

    pix = src.numpyArray(delayed=True)
    if pix is None:
        return

    rgb_u8 = (_np.clip(pix * 255.0, 0, 255)).astype(_np.uint8)
    if rgb_u8.shape[2] > 3:
        rgb_u8 = rgb_u8[:, :, :3]
    payload = rgb_u8.tobytes()

    if not _open():
        return
        
    try:
        n = cols * rows
        h = bytes([0x55, 0xAA, n & 0xFF, (n >> 8) & 0xFF])
        _ser.write(h + payload)
        _ser.flush()
        
        if f_int % 60 == 0:
            print(f'[LED_X] Sending {len(payload)} bytes to {get_par("Comport", "COM8")}')
        
        if _ser.in_waiting > 100:
             _ser.read(_ser.in_waiting)
    except Exception as e:
        print(f'[LED_X] Write ERROR: {e}')
        _close()
    
    _last_send = now

def stop():
    _close()
    me.par.active = False
    print('[LED_X] Stopped')
