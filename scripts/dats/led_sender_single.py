# led_exec script (pyserial based - single source version)
import sys, os

# Add pyserial from PlatformIO env
_pio_sp = os.path.expanduser('~/.platformio/penv/Lib/site-packages')
if _pio_sp not in sys.path:
    sys.path.insert(0, _pio_sp)

import serial as _serial
import time as _time
import numpy as _np

# ---- CONFIG ----
COM_PORT    = 'COM21'             # 自動検出されたポートに変更
COM_BAUD    = 2000000
SOURCE_TOP  = 'led_source'
LED_COLS    = 88
LED_ROWS    = 10
NUM_LEDS    = LED_COLS * LED_ROWS # 880
# ----------------

_ser = None
_last_send = 0.0
_header = bytes([0x55, 0xAA, NUM_LEDS & 0xFF, (NUM_LEDS >> 8) & 0xFF]) # [0x55, 0xAA, 0x70, 0x03]

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
        print(f'[LED] Opened {COM_PORT} at {COM_BAUD}')
        return True
    except Exception as e:
        print(f'[LED] Open ERROR: {e}')
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
    
    # 30FPS制限 (33ms間隔)
    now = _time.perf_counter()
    if now - _last_send < 0.033:
        return

    src = op(SOURCE_TOP)
    if src is None:
        return

    # TDのTOPデータ (左下原点) をそのまま取得
    pix = src.numpyArray(delayed=True)
    if pix is None:
        return

    # 0.0-1.0 -> 0-255変換
    # マッピング（Y反転・ジグザグ）はESP32側で行う
    rgb_u8 = (_np.clip(pix * 255.0, 0, 255)).astype(_np.uint8)
    
    # チャンネル削除 (RGBAならRGBに制限)
    if rgb_u8.shape[2] > 3:
        rgb_u8 = rgb_u8[:, :, :3]
        
    payload = rgb_u8.tobytes()

    if not _open():
        return
        
    try:
        # ヘッダー + データ送信
        # ※データサイズが 2640 バイト (NUM_LEDS * 3) になっている必要があります
        _ser.write(_header + payload)
        _ser.flush()
        
        # 溜まっているデータを掃除
        if _ser.in_waiting > 100:
             _ser.read(_ser.in_waiting)
    except Exception as e:
        print(f'[LED] Write ERROR: {e}')
        _close()
    
    _last_send = now

def stop():
    _close()
    me.par.active = False
    print('[LED] Stopped')
