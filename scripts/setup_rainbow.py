# setup_rainbow.py
# Run in TD Textport:
#   exec(open(project.folder + '/scripts/setup_rainbow.py', encoding='utf-8').read())

TARGET = '/AudioLinkLight_V01/TEST_SCREEN'
base = op(TARGET)

if base is None:
    print(f'[ERROR] {TARGET} not found')
else:
    # ---- 既存ノードを削除 ----
    for name in ('pat_rainbow', 'pat_rainbow_keys', 'pat_rainbow_scroll'):
        o = base.op(name)
        if o is not None:
            o.destroy()

    # ---- Ramp TOP（虹色グラデーション）----
    ramp = base.create(rampTOP, 'pat_rainbow')
    ramp.par.outputresolution = 'custom'
    ramp.par.resolutionw = 88
    ramp.par.resolutionh = 10
    ramp.nodeX = 0
    ramp.nodeY = -200

    # ---- キーカラーテーブル ----
    keys = base.create(tableDAT, 'pat_rainbow_keys')
    keys.clear()
    keys.appendRow(['r', 'g', 'b', 'a', 'pos'])
    keys.appendRow([1,   0,   0,   1,   0.000])
    keys.appendRow([1,   1,   0,   1,   0.167])
    keys.appendRow([0,   1,   0,   1,   0.333])
    keys.appendRow([0,   1,   1,   1,   0.500])
    keys.appendRow([0,   0,   1,   1,   0.667])
    keys.appendRow([1,   0,   1,   1,   0.833])
    keys.appendRow([1,   0,   0,   1,   1.000])
    keys.nodeX = 0
    keys.nodeY = -320
    ramp.par.dat = keys

    # ---- Ramp TOP の phase で横スクロール ----
    ramp.par.phase.expr = 'absTime.seconds * 0.1'

    # ---- led_source に直接接続 ----
    led_src = base.op('led_source')
    led_src.inputConnectors[0].connect(ramp)

    print('=' * 40)
    print('[setup_rainbow] Done!')
    print(f'  pat_rainbow : {ramp.width} x {ramp.height}')
    print(f'  phase expr  : {ramp.par.phase.expr}')
    print(f'  phase mode  : {ramp.par.phase.mode}')
    print()
    print('速度変更例:')
    print("  op('/AudioLinkLight_V01/TEST_SCREEN/pat_rainbow').par.phase.expr = 'absTime.seconds * 0.3'")
    print('=' * 40)
