# setup_td_serial_test.py
# ================================================================
# TouchDesigner Textport から実行するセットアップスクリプト
# LED シリアル制御テスト用ノード群を自動生成する
# ================================================================
# 【使い方】
#   1. TouchDesigner の Textport を開く (Alt+T)
#   2. 以下のコマンドを入力:
#        run('/project1', open('scripts/setup_td_serial_test.py').read())
#      または File > Load Text で直接実行
# ================================================================

import json

TARGET_COMP = '/project1'   # ノードを作成するコンポーネント
SERIAL_PORT = 'COM6'
SERIAL_BAUD = 921600
LED_COLS    = 88
LED_ROWS    = 10

def setup():
    root = op(TARGET_COMP)
    if root is None:
        print(f"[ERROR] {TARGET_COMP} が見つかりません")
        return

    created = []

    # ── 1. Serial DAT ─────────────────────────────────────────
    s_dat = root.findChildren(type=serialDAT, name='serial_out')
    if not s_dat:
        s_dat = root.create(serialDAT, 'serial_out')
    else:
        s_dat = s_dat[0]
    s_dat.par.port       = SERIAL_PORT
    s_dat.par.baudrate   = SERIAL_BAUD
    s_dat.par.databits   = 8
    s_dat.par.parity     = 'none'
    s_dat.par.stopbits   = 1
    s_dat.par.active     = True
    s_dat.par.mode       = 'binary'   # バイナリモード重要！
    s_dat.nodeX, s_dat.nodeY = -300, 200
    created.append('serial_out (Serial DAT)')

    # ── 2. led_source TOP (Noise TOP 88×10 テスト用) ───────────
    n_top = root.findChildren(type=noiseTOP, name='led_source')
    if not n_top:
        n_top = root.create(noiseTOP, 'led_source')
    else:
        n_top = n_top[0]
    n_top.par.resolutionw = LED_COLS
    n_top.par.resolutionh = LED_ROWS
    n_top.par.period      = 0.5
    n_top.par.speed       = 0.3
    n_top.nodeX, n_top.nodeY = -300, 0
    created.append('led_source (Noise TOP  88×10)')

    # ── 3. Execute DAT (フレーム毎送信) ───────────────────────
    script_path = app.samplesFolder + '/scripts/dats/serial_send_led.py'
    # スクリプト本文をファイルから読む
    import os
    script_file = os.path.join(
        os.path.dirname(__file__), 'dats', 'serial_send_led.py'
    )
    if not os.path.exists(script_file):
        # 相対パスが通らない場合はワークスペース直下を試す
        script_file = 'scripts/dats/serial_send_led.py'

    try:
        with open(script_file, 'r', encoding='utf-8') as f:
            code = f.read()
    except FileNotFoundError:
        code = _fallback_script()

    e_dat = root.findChildren(type=executeDAT, name='led_serial_exec')
    if not e_dat:
        e_dat = root.create(executeDAT, 'led_serial_exec')
    else:
        e_dat = e_dat[0]
    e_dat.par.framestart = True   # Frame Start を ON
    e_dat.par.active     = True
    e_dat.clear()
    e_dat.write(code)
    e_dat.nodeX, e_dat.nodeY = 0, 200
    created.append('led_serial_exec (Execute DAT)')

    # ── 4. 確認メッセージ ──────────────────────────────────────
    print("=" * 50)
    print("TD Serial LED セットアップ完了")
    print("=" * 50)
    for c in created:
        print(f"  ✓ {c}")
    print()
    print("【次のステップ】")
    print("  1. serial_out DAT が COM6 / 921600 で接続できているか確認")
    print("  2. led_source TOP を好みのソース（Noise, Constant等）に変更")
    print("  3. BRIGHTNESS を下げたい場合は led_serial_exec DAT 内で調整")
    print()
    print("【単色テスト (Textport から)】")
    print("  op('led_serial_exec').run('test_solid', 80, 0, 80)")
    print("  op('led_serial_exec').run('test_off')")


def _fallback_script():
    """ファイルが見つからない場合の最小スクリプト"""
    return '''\
SERIAL_OP  = 'serial_out'
SOURCE_TOP = 'led_source'
LED_COLS   = 88
LED_ROWS   = 10
BRIGHTNESS = 1.0

def onFrameStart(frame):
    serial = op(SERIAL_OP)
    src    = op(SOURCE_TOP)
    if serial is None or src is None or not serial.par.active:
        return
    pix = src.numpyArray(delayed=False)
    if pix is None:
        return
    num_leds = LED_COLS * LED_ROWS
    buf = bytearray(4 + num_leds * 3)
    buf[0], buf[1] = 0x55, 0xAA
    buf[2], buf[3] = num_leds & 0xFF, (num_leds >> 8) & 0xFF
    h, w = pix.shape[:2]
    pos = 4
    for row in range(min(h, LED_ROWS)):
        for col in range(min(w, LED_COLS)):
            buf[pos]   = int(min(255, pix[row,col,0]*255*BRIGHTNESS))
            buf[pos+1] = int(min(255, pix[row,col,1]*255*BRIGHTNESS))
            buf[pos+2] = int(min(255, pix[row,col,2]*255*BRIGHTNESS))
            pos += 3
    serial.sendBytes(bytes(buf))

def test_solid(r=80, g=0, b=80):
    serial = op(SERIAL_OP)
    if serial is None or not serial.par.active: return
    n = LED_COLS * LED_ROWS
    buf = bytearray(4 + n*3)
    buf[0],buf[1],buf[2],buf[3] = 0x55,0xAA,n&0xFF,(n>>8)&0xFF
    for i in range(n): buf[4+i*3]=r; buf[5+i*3]=g; buf[6+i*3]=b
    serial.sendBytes(bytes(buf))

def test_off():
    test_solid(0,0,0)
'''


# 実行
setup()
