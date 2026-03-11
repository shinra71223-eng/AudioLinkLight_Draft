# led_exec script (pyserial based)
import sys, os
import serial as _serial
import time as _time
import numpy as _np

# --- Configuration ---
COM_PORT    = 'COM17' # Adjust to match your ESP32 COM port
COM_BAUD    = 2000000
SOURCE_TOP  = 'led_source'
# For 4 sources, we define their names
SOURCES = ['led_source_u1', 'led_source', 'led_source_d1', 'led_source_USB']

# Total pixels for all 4 sources (assuming 88x10 for first 3 and 81x12 for last)
# Based on led_sender_pyserial_multi.py:
# Slave 1-3: 88x10 each (2640 bytes each)
# Master: 81x12 (2916 bytes)
# Total pixels = (880 * 3) + 972 = 3612
NUM_TOTAL_PIXELS = 3612
MIN_FRAME_TIME = 0.033 # ~30 FPS limit

_ser = None
_last_send = 0.0
_header = bytes([0x55, 0xAA, NUM_TOTAL_PIXELS & 0xFF, (NUM_TOTAL_PIXELS >> 8) & 0xFF])

def _open():
    global _ser
    if _ser is not None and _ser.is_open:
        return True
    try:
        s = _serial.Serial(COM_PORT, COM_BAUD, timeout=0)
        s.dtr = False
        s.rts = False
        _time.sleep(0.1)
        s.reset_input_buffer()
        _ser = s
        print(f'[LED] Opened {COM_PORT}')
        return True
    except Exception as e:
        print(f'[LED] Error opening {COM_PORT}: {e}')
        _ser = None
        return False

def _get_payload(top_name, rows, cols):
    expected = rows * cols * 3
    canvas = _np.zeros((rows, cols, 3), dtype=_np.float32)
    src = op(top_name)
    if src:
        pix = src.numpyArray(delayed=True)
        if pix is not None:
            h, w = pix.shape[:2]
            rh, rw = min(h, rows), min(w, cols)
            canvas[:rh, :rw, :3] = pix[:rh, :rw, :3]
    
    # Vertically flip (TD is bottom-up, LED usually top-down)
    canvas = canvas[::-1, :, :]
    
    rgb_u8 = (_np.clip(canvas * 255.0, 0, 255)).astype(_np.uint8)
    return rgb_u8.tobytes()

def onFrameStart(frame):
    global _last_send
    now = _time.perf_counter()
    if now - _last_send < MIN_FRAME_TIME:
        return
        
    if not _open():
        return
        
    # Build full payload
    # Note: Using the same dimensions as in led_sender_pyserial_multi.py
    data_u1   = _get_payload(SOURCES[0], 10, 88)
    data_none = _get_payload(SOURCES[1], 10, 88)
    data_d1   = _get_payload(SOURCES[2], 10, 88)
    data_usb  = _get_payload(SOURCES[3], 12, 81)
    
    full_payload = _header + data_u1 + data_none + data_d1 + data_usb
    
    try:
        _ser.write(full_payload)
        _ser.flush()
        # Drain any feedback/ACK
        if _ser.in_waiting > 100:
            _ser.read(_ser.in_waiting)
    except:
        _ser = None
        
    _last_send = now

def stop():
    global _ser
    if _ser:
        _ser.close()
    _ser = None
    me.par.active = False
    print('[LED] Stopped')
