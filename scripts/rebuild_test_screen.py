# rebuild_test_screen.py
# ================================================================
# TEST_SCREEN BASE を完全リビルドする
# ================================================================
# 【実行方法】TD Textport (Alt+T) で:
#   exec(open(r'C:\Users\shin_\OneDrive\ドキュメント\AntiGravity\AudioLinkLight\scripts\rebuild_test_screen.py').read())
#
# 【作成されるノード構成】
#
#   [Null TOP: led_source] ← 送信先(差し替え可)
#      ├─ [Constant TOP: pat_solid]     単色テスト用 (88×10)
#      ├─ [Noise TOP: pat_noise]        アニメテスト用 (88×10)
#      ├─ [Ramp TOP: pat_ramp]          グラデテスト用 (88×10)
#      └─ [Switch TOP: pat_switch]      パターン切替 → Null
#
#   [Serial DAT: serial_out]            COM5 / 921600 / binary
#   [Execute DAT: led_exec]             フレーム毎送信ロジック
#   [Text DAT: instructions]            操作メモ
#
# ================================================================

TARGET_BASE = '/AudioLinkLight_V01/TEST_SCREEN'
COM_PORT    = 'COM6'
BAUD        = 921600
LED_COLS    = 88
LED_ROWS    = 10
BRIGHTNESS  = 1.0   # 0.0〜1.0

# ─────────────────────────────────────────────────────────────────
# ノード間隔用ヘルパー
# ─────────────────────────────────────────────────────────────────
_COL = 200   # X 間隔
_ROW = 150   # Y 間隔

def _pos(col, row):
    return col * _COL - 400, row * _ROW - 200

# ─────────────────────────────────────────────────────────────────
def _clear_base(base):
    """BASE 内の全子ノードを削除"""
    for ch in list(base.findChildren(depth=1)):
        try:
            ch.destroy()
        except Exception as e:
            print(f"  [WARN] {ch.name} 削除失敗: {e}")

# ─────────────────────────────────────────────────────────────────
def rebuild():
    base = op(TARGET_BASE)
    if base is None:
        print(f"[ERROR] {TARGET_BASE} が見つかりません")
        for c in op('/').findChildren(name='TEST_SCREEN', recurse=True):
            print(f"  候補: {c.path}")
        return

    print(f"Rebuilding: {base.path}")
    _clear_base(base)
    print("  既存ノード削除完了")

    # ── Serial DAT ──────────────────────────────────────────────
    s = base.create(serialDAT, 'serial_out')
    s.par.port      = COM_PORT
    s.par.baudrate  = BAUD
    s.par.databits  = 8
    s.par.parity    = 'none'
    s.par.stopbits  = 1
    s.par.active    = True
    s.nodeX, s.nodeY = _pos(3, 2)
    print("  + serial_out (Serial DAT)")

    # ── テスト画像 TOP群 (88×10) ─────────────────────────────────

    # 単色 Constant TOP
    cs = base.create(constantTOP, 'pat_solid')
    cs.par.resolutionw  = LED_COLS
    cs.par.resolutionh  = LED_ROWS
    cs.par.colorr       = 0.3
    cs.par.colorg       = 0.0
    cs.par.colorb       = 0.5
    cs.nodeX, cs.nodeY  = _pos(0, 0)
    print("  + pat_solid (Constant TOP)")

    # Noise TOP
    nt = base.create(noiseTOP, 'pat_noise')
    nt.par.resolutionw  = LED_COLS
    nt.par.resolutionh  = LED_ROWS
    nt.par.period       = 0.4
    nt.nodeX, nt.nodeY  = _pos(1, 0)
    print("  + pat_noise (Noise TOP)")

    # Ramp TOP (水平グラデーション)
    rp = base.create(rampTOP, 'pat_ramp')
    rp.par.resolutionw  = LED_COLS
    rp.par.resolutionh  = LED_ROWS
    rp.nodeX, rp.nodeY  = _pos(2, 0)
    print("  + pat_ramp (Ramp TOP)")

    # Switch TOP (0=solid / 1=noise / 2=ramp)
    sw = base.create(switchTOP, 'pat_switch')
    sw.par.resolutionw = LED_COLS
    sw.par.resolutionh  = LED_ROWS
    sw.par.index        = 0
    sw.inputConnectors[0].connect(cs)
    sw.inputConnectors[1].connect(nt)
    sw.inputConnectors[2].connect(rp)
    sw.nodeX, sw.nodeY  = _pos(1, 1)
    print("  + pat_switch (Switch TOP  0=solid / 1=noise / 2=ramp)")

    # Level TOP (輝度調整)
    lv = base.create(levelTOP, 'brightness')
    lv.par.resolutionw  = LED_COLS
    lv.par.resolutionh  = LED_ROWS
    lv.par.opacity      = BRIGHTNESS
    lv.inputConnectors[0].connect(sw)
    lv.nodeX, lv.nodeY  = _pos(2, 1)
    print("  + brightness (Level TOP)")

    # Null TOP: led_source（送信元）
    nl = base.create(nullTOP, 'led_source')
    nl.par.resolutionw  = LED_COLS
    nl.par.resolutionh  = LED_ROWS
    nl.inputConnectors[0].connect(lv)
    nl.nodeX, nl.nodeY  = _pos(3, 1)
    print("  + led_source (Null TOP  ← 送信元)")

    # ── Execute DAT (フレーム毎 RGB 送信) ───────────────────────
    ex_code = _exec_script()
    ex = base.create(executeDAT, 'led_exec')
    ex.par.framestart   = True
    ex.par.active       = True
    ex.clear()
    ex.write(ex_code)
    ex.nodeX, ex.nodeY  = _pos(3, 3)
    print("  + led_exec (Execute DAT  frameStart=ON)")

    # ── Text DAT: 操作メモ ────────────────────────────────────
    td_note = base.create(textDAT, 'instructions')
    td_note.clear()
    td_note.write(
        "=== TEST_SCREEN LED テスト操作メモ ===\n"
        "\n"
        "【パターン切替】\n"
        "  op('pat_switch').par.index = 0   # 単色 (pat_solid)\n"
        "  op('pat_switch').par.index = 1   # ノイズアニメ (pat_noise)\n"
        "  op('pat_switch').par.index = 2   # グラデーション (pat_ramp)\n"
        "\n"
        "【単色カラー変更】\n"
        "  s = op('pat_solid')\n"
        "  s.par.colorr = 0.3; s.par.colorg = 0.0; s.par.colorb = 0.5\n"
        "\n"
        "【輝度調整】\n"
        "  op('brightness').par.opacity = 0.5   # 0.0〜1.0\n"
        "\n"
        "【手動テスト (Textport)】\n"
        "  op('led_exec').run('test_solid', 80, 0, 80)  # 全LED 紫\n"
        "  op('led_exec').run('test_off')               # 消灯\n"
        "  op('led_exec').run('test_column', 0, 80)     # 列0 を白点灯\n"
        "\n"
        "【シリアル接続確認】\n"
        "  op('serial_out').par.active  → True なら接続中\n"
    )
    td_note.nodeX, td_note.nodeY = _pos(0, 3)
    print("  + instructions (Text DAT)")

    print()
    print("=" * 50)
    print("TEST_SCREEN リビルド完了！")
    print()
    print("すぐテストするには Textport で:")
    print(f"  op('{TARGET_BASE}/led_exec').run('test_solid', 80, 0, 80)")
    print(f"  op('{TARGET_BASE}/led_exec').run('test_off')")


# ─────────────────────────────────────────────────────────────────
def _exec_script():
    return '''\
# led_exec  ── Execute DAT (TEST_SCREEN/led_exec)
# フレーム毎に led_source の RGB を ESP32 へ送信する
# ================================================================
# プロトコル: [0x55][0xAA][count_lo][count_hi][R0][G0][B0]...
# count = 880 (88col × 10row)
# index   0..439  → ledsA (GPIO4 / 上5行)
# index 440..879  → ledsB (GPIO5 / 下5行)
# ================================================================

SERIAL_OP  = 'serial_out'
SOURCE_TOP = 'led_source'
LED_COLS   = 88
LED_ROWS   = 10
NUM_LEDS   = LED_COLS * LED_ROWS   # 880

def onFrameStart(frame):
    serial = op(SERIAL_OP)
    src    = op(SOURCE_TOP)
    if serial is None or src is None:
        return
    if not serial.par.active:
        return

    pix = src.numpyArray(delayed=False)
    if pix is None:
        return

    buf = bytearray(4 + NUM_LEDS * 3)
    buf[0] = 0x55
    buf[1] = 0xAA
    buf[2] = NUM_LEDS & 0xFF
    buf[3] = (NUM_LEDS >> 8) & 0xFF

    h = min(pix.shape[0], LED_ROWS)
    w = min(pix.shape[1], LED_COLS)
    pos = 4
    for row in range(LED_ROWS):
        for col in range(LED_COLS):
            if row < h and col < w:
                p = pix[row, col]
                buf[pos]     = int(min(255, p[0] * 255))
                buf[pos + 1] = int(min(255, p[1] * 255))
                buf[pos + 2] = int(min(255, p[2] * 255))
            pos += 3

    serial.sendBytes(bytes(buf))


# ── 手動テスト関数 ───────────────────────────────────────────────
def test_solid(r=80, g=80, b=80):
    """全 LED を単色で点灯させるテスト"""
    serial = op(SERIAL_OP)
    if serial is None or not serial.par.active:
        print("[test_solid] serial_out が接続されていません")
        return
    buf = bytearray(4 + NUM_LEDS * 3)
    buf[0], buf[1] = 0x55, 0xAA
    buf[2], buf[3] = NUM_LEDS & 0xFF, (NUM_LEDS >> 8) & 0xFF
    for i in range(NUM_LEDS):
        buf[4 + i * 3]     = r
        buf[4 + i * 3 + 1] = g
        buf[4 + i * 3 + 2] = b
    serial.sendBytes(bytes(buf))
    print(f"[test_solid] R={r} G={g} B={b}  ({NUM_LEDS} LEDs)")


def test_off():
    """全 LED 消灯"""
    test_solid(0, 0, 0)
    print("[test_off] All LEDs OFF")


def test_column(col_idx=0, brightness=80):
    """指定列 (0〜87) の10 LED だけ点灯 (白)"""
    serial = op(SERIAL_OP)
    if serial is None or not serial.par.active:
        print("[test_column] serial_out が接続されていません")
        return
    if col_idx < 0 or col_idx >= LED_COLS:
        print(f"[test_column] col_idx は 0〜{LED_COLS-1} で指定してください")
        return
    buf = bytearray(4 + NUM_LEDS * 3)
    buf[0], buf[1] = 0x55, 0xAA
    buf[2], buf[3] = NUM_LEDS & 0xFF, (NUM_LEDS >> 8) & 0xFF
    for row in range(LED_ROWS):
        i = row * LED_COLS + col_idx
        buf[4 + i * 3]     = brightness
        buf[4 + i * 3 + 1] = brightness
        buf[4 + i * 3 + 2] = brightness
    serial.sendBytes(bytes(buf))
    print(f"[test_column] col={col_idx}  brightness={brightness}")


def test_scan(delay_ms=100):
    """列スキャンテスト (列0→87 順に白点灯) ― ノンブロッキング版は非対応のため1回分のみ"""
    print("[test_scan] Textport から連続実行してください")
    print("  for c in range(88): op('led_exec').run('test_column', c); __import__('time').sleep(0.1)")
'''

# ─────────────────────────────────────────────────────────────────
rebuild()
