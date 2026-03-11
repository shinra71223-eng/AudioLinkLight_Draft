# led_sender_pyserial_multi.py
# ================================================================
# TouchDesigner Execute DAT - 4-Unit Wireless System (Master Relay)
# ================================================================
# Protocol: [0x55][0xAA][count_lo][count_hi] + 10836 bytes of pixel data
# Data layout: Slave1(2640) + Slave2(2640) + Slave3(2640) + Master(2916)
# ================================================================

import sys, os

_pio_sp = os.path.expanduser('~/.platformio/penv/Lib/site-packages')
if _pio_sp not in sys.path:
    sys.path.insert(0, _pio_sp)

import serial as _serial
import time as _time
import numpy as _np

COM_PORT    = 'COM8'
COM_BAUD    = 2000000

# ソースとなるTOPノード名
SOURCE_U1   = 'led_source_u1'
SOURCE_NONE = 'led_source'
SOURCE_D1   = 'led_source_d1'
SOURCE_USB  = 'led_source_USB'

# 子機設定
SLAVE_COLS  = 88
SLAVE_ROWS  = 10
SLAVE_BYTES = SLAVE_COLS * SLAVE_ROWS * 3  # 2640

# 親機設定
MASTER_COLS = 81
MASTER_ROWS = 12
MASTER_BYTES = MASTER_COLS * MASTER_ROWS * 3  # 2916

TOTAL_DATA_BYTES = (SLAVE_BYTES * 3) + MASTER_BYTES  # 10836
NUM_TOTAL_PIXELS = TOTAL_DATA_BYTES // 3
MIN_FRAME_TIME = 0.033  # 33ms (approx 30FPS) Throttling
# ----------------

_ser = None
_last_send   = 0.0
_send_count  = 0
_fail_count  = 0
_header = bytes([0x55, 0xAA, NUM_TOTAL_PIXELS & 0xFF, (NUM_TOTAL_PIXELS >> 8) & 0xFF])

def _open():
    global _ser, _fail_count
    # 設定が変わっていたら一度閉じる
    if _ser is not None:
        if _ser.port != COM_PORT or _ser.baudrate != COM_BAUD:
            print(f'[led_multi] CONFIG CHANGE: closing to re-open with {COM_BAUD}')
            _close()

    if _ser is not None and _ser.is_open:
        return True
    try:
        s = _serial.Serial()
        s.port = COM_PORT
        s.baudrate = COM_BAUD
        s.timeout = 0.1            # 100ms search window for diagnostics
        s.write_timeout = 0        # Non-blocking write
        s.dtr = False
        s.rts = False
        s.open()
        _time.sleep(0.3)
        s.reset_input_buffer()
        s.reset_output_buffer()
        _ser = s
        _fail_count = 0
        print(f'[led_multi] opened {COM_PORT} ({_CODE_SIG})')
        return True
    except Exception as e:
        import serial.tools.list_ports
        ports = [p.device for p in serial.tools.list_ports.comports()]
        print(f'[led_multi] open ERROR on {COM_PORT}: {e}')
        print(f'[led_multi] AVAILABLE PORTS: {ports}')
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

def _drain():
    try:
        return _ser.read(256)
    except:
        return b''

def _get_top_payload(top_name, target_rows, target_cols):
    """
    指定されたTOPからピクセルを取得し、(target_rows x target_cols x 3)バイトの完全なデータにする。
    サイズが満たない場合は黒(0)で隙間を埋め、大きい場合は切り捨てることで、文字の斜めズレ(Skew)を防ぐ。
    """
    expected_bytes = target_rows * target_cols * 3
    
    # 完全な黒のキャンバス（target_rows × target_cols × 3）を用意
    canvas = _np.zeros((target_rows, target_cols, 3), dtype=_np.float32)

    src = op(top_name)
    if src is not None:
        pix = src.numpyArray(delayed=True)
        if pix is not None:
            h, w = pix.shape[:2]
            rh = min(h, target_rows)
            rw = min(w, target_cols)
            # 画像の有効部分だけをキャンバスの左上に貼り付け
            canvas[:rh, :rw, :] = pix[:rh, :rw, :3]
            
    # Y軸を反転（TDの座標系→LEDの物理配置）
    canvas = canvas[::-1, :, :]
    
    # 0-255スケールに変換してバイト列化
    canvas = (canvas * 255.0)
    _np.clip(canvas, 0, 255, out=canvas)
    rgb_u8 = canvas.astype(_np.uint8)
    
    return rgb_u8.tobytes()

def onFrameStart(frame):
    global _last_send, _send_count, _fail_count
    
    t0 = _time.perf_counter()
    if not _open():
        return

    now = _time.perf_counter()
    t_open = (now - t0) * 1000

    # Throttling
    if now - _last_send < MIN_FRAME_TIME:
        return

    _drain()
    t_drain = (_time.perf_counter() - now) * 1000

    # 4つのTOPからそれぞれ画像を取得
    t_proc_start = _time.perf_counter()
    data_u1   = _get_top_payload(SOURCE_U1, SLAVE_ROWS, SLAVE_COLS)
    data_none = _get_top_payload(SOURCE_NONE, SLAVE_ROWS, SLAVE_COLS)
    data_d1   = _get_top_payload(SOURCE_D1, SLAVE_ROWS, SLAVE_COLS)
    data_usb  = _get_top_payload(SOURCE_USB, MASTER_ROWS, MASTER_COLS)
    
    full_payload = _header + data_u1 + data_none + data_d1 + data_usb

    try:
        # シンプルに送信して完了（ACK待ちはしない）
        _ser.write(full_payload)
        _ser.flush()
        pass
    
    # 診断結果を30フレームごとに表示
    if _send_count % 30 == 0:
        total_cycle = (now - _last_send) * 1000 if _last_send > 0 else 0
        fps = 1000.0 / total_cycle if total_cycle > 0 else 0
        print(f"--- RESTORED BASELINE (2Mbps) ---")
        print(f"  FPS: {fps:.1f}")
        print(f"  Status: Running (Non-blocking)")
        print(f"----------------------------------------")
    
    _last_send = now
    _send_count += 1

def stop():
    _close()
    me.par.active = False
    print('[led_multi] stopped')
