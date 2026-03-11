# serial_send_led.py
# ================================================================
# TouchDesigner Execute DAT — フレーム毎に LED RGB データをシリアル送信
# ================================================================
# 【設置方法】
#   1. Execute DAT を作成し、このスクリプトを貼り付ける
#   2. Execute DAT の "Frame Start" チェックを ON にする
#   3. 下記 CONFIG を環境に合わせて編集する
#
# 【必要 OP】
#   - Serial DAT  : 名前 "serial_out"  COM6 / 921600 baud / Binary
#   - Source TOP  : 名前 "led_source"  88px × 10px  (RGB 色情報)
#
# 【プロトコル】
#   [0x55][0xAA][count_lo][count_hi][R0][G0][B0]...[R879][G879][B879]
#   count = 880  (固定)
#   ledsA(GPIO4) → index   0..439   (上 5 行)
#   ledsB(GPIO5) → index 440..879   (下 5 行)
# ================================================================

# ───────── CONFIG ──────────────────────────────────────────────
SERIAL_OP   = 'serial_out'   # Serial DAT の名前
SOURCE_TOP  = 'led_source'   # 88×10 の TOP 名
LED_COLS    = 88             # 列数
LED_ROWS    = 10             # 行数
BRIGHTNESS  = 1.0            # 0.0 〜 1.0 のスケール (テスト時は低めに)
MAGIC       = bytes([0x55, 0xAA])
# ───────────────────────────────────────────────────────────────

import struct

def _pack_frame(pixels):
    """pixels: numpy array (height, width, 4) float32 0..1 → bytes"""
    num_leds = LED_COLS * LED_ROWS  # 880
    h, w = pixels.shape[:2]
    buf = bytearray(4 + num_leds * 3)

    # Header
    buf[0] = 0x55
    buf[1] = 0xAA
    buf[2] = num_leds & 0xFF
    buf[3] = (num_leds >> 8) & 0xFF

    # RGB data: row-major (row0 = cols 0..87, row1 = cols 0..87, ...)
    pos = 4
    for row in range(min(h, LED_ROWS)):
        for col in range(min(w, LED_COLS)):
            r = int(min(255, max(0, pixels[row, col, 0] * 255 * BRIGHTNESS)))
            g = int(min(255, max(0, pixels[row, col, 1] * 255 * BRIGHTNESS)))
            b = int(min(255, max(0, pixels[row, col, 2] * 255 * BRIGHTNESS)))
            buf[pos]     = r
            buf[pos + 1] = g
            buf[pos + 2] = b
            pos += 3

    return bytes(buf)


# ── Execute DAT コールバック ──────────────────────────────────
def onFrameStart(frame):
    serial = op(SERIAL_OP)
    src    = op(SOURCE_TOP)

    if serial is None or src is None:
        return
    if not serial.par.active:
        return

    # numpyArray は遅延評価; delayed=False で確実に取得
    pix = src.numpyArray(delayed=False)
    if pix is None:
        return

    data = _pack_frame(pix)
    serial.sendBytes(data)


# ── 手動テスト用: Textport から run('serial_send_led', 'test_solid') で実行可 ──
def test_solid(r=80, g=0, b=80):
    """全LEDを単色で点灯するテスト (Textport から呼び出し可能)"""
    serial = op(SERIAL_OP)
    if serial is None:
        print(f"[ERROR] Serial DAT '{SERIAL_OP}' が見つかりません")
        return
    if not serial.par.active:
        print(f"[ERROR] Serial DAT '{SERIAL_OP}' がアクティブではありません")
        return

    num_leds = LED_COLS * LED_ROWS
    buf = bytearray(4 + num_leds * 3)
    buf[0], buf[1] = 0x55, 0xAA
    buf[2] = num_leds & 0xFF
    buf[3] = (num_leds >> 8) & 0xFF
    for i in range(num_leds):
        buf[4 + i*3]     = r
        buf[4 + i*3 + 1] = g
        buf[4 + i*3 + 2] = b

    serial.sendBytes(bytes(buf))
    print(f"[serial_send_led] test_solid sent: R={r} G={g} B={b}  ({num_leds} LEDs)")


def test_off():
    """全LED消灯"""
    test_solid(0, 0, 0)
    print("[serial_send_led] All LEDs OFF")
