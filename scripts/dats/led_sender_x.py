# led_exec_x script (Generic version)
import sys, os

# Add pyserial from PlatformIO env
_pio_sp = os.path.expanduser('~/.platformio/penv/Lib/site-packages')
if _pio_sp not in sys.path:
    sys.path.insert(0, _pio_sp)

import serial as _serial
import time as _time
import numpy as _np

# ---- CONFIG (Read from parent parameters if available, else use defaults) ----
# parent().par.Comport, parent().par.Baudrate, parent().par.Sourcetop などを想定
def get_par(name, default):
    p = getattr(parent().par, name, None)
    return p.eval() if p is not None else default

COM_PORT    = get_par('Comport', 'COM21')
COM_BAUD    = get_par('Baudrate', 2000000)
SOURCE_TOP  = get_par('Sourcetop', 'led_source')

# LED Dimensions (Defaults to 88x10)
LED_COLS    = get_par('Ledcols', 88)
LED_ROWS    = get_par('Ledrows', 10)
NUM_LEDS    = LED_COLS * LED_ROWS
# ----------------

_ser = None
_last_send = 0.0
_header = bytes([0x55, 0xAA, NUM_LEDS & 0xFF, (NUM_LEDS >> 8) & 0xFF])
_last_reset_state = 0 # リセットボタン状態管理

def _open():
    global _ser
    port = get_par('Comport', COM_PORT)
    baud = get_par('Baudrate', COM_BAUD)
    
    if _ser is not None:
        if _ser.is_open and _ser.port == port and _ser.baudrate == baud:
            return True
        _close() # Re-open if config changed

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
        # UIへのフィードバック用（もしノードがあれば）
        parent().store('status', f'Connected {port}')
        print(f'[LED_X] Opened {port} at {baud}')
        return True
    except Exception as e:
        parent().store('status', f'Error: {e}')
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
    global _last_send, _ser, _last_reset_state
    
    # --- RESET_Button 連動 ---
    reset_btn = op('../../RESET_Button')
    if reset_btn:
        curr_reset = reset_btn.panel.state
        if curr_reset == 1 and _last_reset_state == 0:
            print(f'[LED_X] Manual Reset Triggered')
            _close()
        _last_reset_state = curr_reset

    # 30FPS制限
    now = _time.perf_counter()
    if now - _last_send < 0.033:
        return

    src_name = get_par('Sourcetop', SOURCE_TOP)
    src = op(src_name)
    if src is None:
        return

    # TDのTOPデータ (左下原点) をそのまま取得
    pix = src.numpyArray(delayed=True)
    if pix is None:
        return

    # 0.0-1.0 -> 0-255変換
    rgb_u8 = (_np.clip(pix * 255.0, 0, 255)).astype(_np.uint8)
    
    # RGBA -> RGB
    if rgb_u8.shape[2] > 3:
        rgb_u8 = rgb_u8[:, :, :3]
        
    payload = rgb_u8.tobytes()

    if not _open():
        return
        
    try:
        # ヘッダー作成 (NUM_LEDSが変わる可能性があるため毎回計算)
        cols = get_par('Ledcols', LED_COLS)
        rows = get_par('Ledrows', LED_ROWS)
        n = cols * rows
        h = bytes([0x55, 0xAA, n & 0xFF, (n >> 8) & 0xFF])
        
        _ser.write(h + payload)
        _ser.flush()
        
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
