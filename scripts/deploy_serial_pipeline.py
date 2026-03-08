"""
deploy_serial_pipeline.py
=========================
AudioLinkLight V03_b02 — Serial パイプライン構築スクリプト (Phase 1)

【実行方法 (TD Textport)】
exec(open(project.folder + '/scripts/deploy_serial_pipeline.py', encoding='utf-8').read())

【構築するノード】
  cross_mix → level_serial → crop_top (上5行)
                           └─ crop_bot (下5行)
                                └─ layout_10x88
                                     └─ top_to_chop
                                          └─ serial_out

【前提条件】
  - TEST_SCREEN baseCOMP が /AudioLinkLight_VXX/TEST_SCREEN に存在すること
  - cross_mix ノードが TEST_SCREEN 内に存在すること
"""

import td

# ─────────────────────────────────────────────
# 0. ターゲット baseCOMP を探す
# ─────────────────────────────────────────────
def find_test_screen():
    """TEST_SCREEN baseCOMPを探す"""
    candidates = root.findChildren(type=baseCOMP, name='TEST_SCREEN')
    if not candidates:
        raise RuntimeError("TEST_SCREEN が見つかりません。build_test_screen.py を先に実行してください。")
    return candidates[0]

parent = find_test_screen()
print(f"[deploy_serial_pipeline] 対象コンポーネント: {parent.path}")

# ─────────────────────────────────────────────
# 1. 接続元 cross_mix を確認
# ─────────────────────────────────────────────
cross_mix = parent.op('cross_mix')
if cross_mix is None:
    raise RuntimeError("cross_mix ノードが見つかりません。TEST_SCREENの構造を確認してください。")

print(f"[deploy_serial_pipeline] cross_mix 確認: {cross_mix.path}")

# ─────────────────────────────────────────────
# 2. level_serial — 輝度リミッター TOP
# ─────────────────────────────────────────────
if parent.op('level_serial'):
    parent.op('level_serial').destroy()

level_serial = parent.create(levelTOP, 'level_serial')
level_serial.inputConnectors[0].connect(cross_mix)

# 輝度を安全値に抑える（全白時の電流保護）
level_serial.par.brightness2 = 0.8
level_serial.par.clamp = True
level_serial.par.clamphigh2 = 1.0

# 配置
level_serial.nodeX = cross_mix.nodeX + 200
level_serial.nodeY = cross_mix.nodeY - 100

print("[deploy_serial_pipeline] level_serial 作成完了")

# ─────────────────────────────────────────────
# 3. crop_top — 上段 5行 (Row 0〜4)
# ─────────────────────────────────────────────
if parent.op('crop_top'):
    parent.op('crop_top').destroy()

crop_top = parent.create(cropTOP, 'crop_top')
crop_top.inputConnectors[0].connect(level_serial)

# 解像度: 88×10 → 上5行 = 88×5
# cropTOP の値は 0〜1 の相対値（0.5 = 5/10行）
crop_top.par.cropleft = 0
crop_top.par.cropright = 0
crop_top.par.croptop = 0       # 上端から切らない
crop_top.par.cropbottom = 0.5  # 下半分を切る → 上5行が残る

crop_top.nodeX = level_serial.nodeX
crop_top.nodeY = level_serial.nodeY - 150

print("[deploy_serial_pipeline] crop_top 作成完了 (上段 5×88)")

# ─────────────────────────────────────────────
# 4. crop_bot — 下段 5行 (Row 5〜9)
# ─────────────────────────────────────────────
if parent.op('crop_bot'):
    parent.op('crop_bot').destroy()

crop_bot = parent.create(cropTOP, 'crop_bot')
crop_bot.inputConnectors[0].connect(level_serial)

# 下5行 = 88×5
# 上半分を切る → 下5行が残る
crop_bot.par.cropleft = 0
crop_bot.par.cropright = 0
crop_bot.par.croptop = 0.5     # 上半分を切る → 下5行が残る
crop_bot.par.cropbottom = 0

crop_bot.nodeX = level_serial.nodeX + 200
crop_bot.nodeY = level_serial.nodeY - 150

print("[deploy_serial_pipeline] crop_bot 作成完了 (下段 5×88)")

# ─────────────────────────────────────────────
# 5. layout_10x88 — 上下を縦連結で 10×88 に再構成
# ─────────────────────────────────────────────
if parent.op('layout_10x88'):
    parent.op('layout_10x88').destroy()

layout = parent.create(layoutTOP, 'layout_10x88')

# tops パラメータで入力TOPをパスで指定（layoutTOPはinputConnectorsではなくtopsパラで入力）
layout.par.tops = f"{crop_top.path} {crop_bot.path}"
# 縦方向に並べる（1列 × 2行）
layout.par.align   = 'verttb'   # vertical top-to-bottom
layout.par.maxcols = 1
layout.par.fit     = 'fill'     # セルいっぱいに引き伸ばす（比率無視）
# 出力解像度: 88×10
layout.par.outputresolution = 'custom'
layout.par.resolutionw = 88
layout.par.resolutionh = 10

layout.nodeX = crop_top.nodeX + 100
layout.nodeY = crop_top.nodeY - 180

print("[deploy_serial_pipeline] layout_10x88 作成完了 (10×88)")

# ─────────────────────────────────────────────
# 6. top_to_chop — TOP → CHOP 変換
# ─────────────────────────────────────────────
if parent.op('top_to_chop'):
    parent.op('top_to_chop').destroy()

# TD バージョンによりクラス名が異なるため総当たりで探す
_top_to_chop_cls = None
for _name in ['toptoCHOP', 'topToCHOP', 'TOPToCHOP', 'topToChopCHOP', 'TOPToChopCHOP']:
    try:
        _top_to_chop_cls = eval(_name)
        print(f"[deploy_serial_pipeline] TOP to CHOP クラス名: {_name}")
        break
    except NameError:
        pass
if _top_to_chop_cls is None:
    raise RuntimeError("TOP to CHOP クラスが見つかりません。dump_op_params.py で確認してください。")

top_to_chop = parent.create(_top_to_chop_cls, 'top_to_chop')
# toptoCHOP は inputConnectors ではなく par.top でTOPを参照する
top_to_chop.par.top = layout.path
top_to_chop.par.downloadtype = 'nextframe'

top_to_chop.nodeX = layout.nodeX
top_to_chop.nodeY = layout.nodeY - 180

print("[deploy_serial_pipeline] top_to_chop 作成完了")

# ─────────────────────────────────────────────
# 7. serial_out — Serial CHOP
# ─────────────────────────────────────────────
if parent.op('serial_out'):
    parent.op('serial_out').destroy()

serial_out = parent.create(serialCHOP, 'serial_out')
serial_out.inputConnectors[0].connect(top_to_chop)

# シリアルパラメータ（dump_op_params.py で確認済みの正しいパラメータ名）
serial_out.par.baudrate  = 2000000
serial_out.par.port      = 'COM3'   # CH340 ポート
serial_out.par.databits  = 8
serial_out.par.parity    = 'none'
serial_out.par.stopbits  = 2
# active は手動で On にする（誤送信防止）
serial_out.par.active    = False

serial_out.nodeX = top_to_chop.nodeX
serial_out.nodeY = top_to_chop.nodeY - 180

print("[deploy_serial_pipeline] serial_out 作成完了")
print()
print("=" * 60)
print("Serial パイプライン構築完了！")
print()
print("【次のステップ】")
print("1. serial_out ノードを選択")
print("2. Parameters → Port に COMポート番号を設定 (例: COM3)")
print("3. ESP32 に phase1_minimal.ino を書き込む")
print("4. Active パラメータを True にして送信開始")
print("=" * 60)
