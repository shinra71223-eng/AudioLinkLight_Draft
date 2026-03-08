# deploy_led_output.py
# ================================================================
# LED_OUTPUT Base COMP を作成する（LED送信モジュール分離）
# ================================================================
# 【実行方法 (TD Textport)】
#   exec(open(project.folder + '/scripts/deploy_led_output.py', encoding='utf-8').read())
#
# 【前提条件】
#   SCENE_1 ~ SCENE_4 が既に作成されていること
#   (deploy_scenes.py を先に実行してください)
#
# 【作成されるノード構成】
#   /AudioLinkLight_V01/LED_OUTPUT/
#     ├── scene_in_1  (Select TOP → SCENE_1/scene_out)
#     ├── scene_in_2  (Select TOP → SCENE_2/scene_out)
#     ├── scene_in_3  (Select TOP → SCENE_3/scene_out)
#     ├── scene_in_4  (Select TOP → SCENE_4/scene_out)
#     ├── scene_select (Switch TOP — index 0~3 でシーン切替)
#     ├── brightness   (Level TOP — 輝度調整)
#     ├── led_source   (Null TOP, 88x10 — LED送信元)
#     ├── led_preview  (Resolution TOP, 880x100 — モニタープレビュー)
#     └── led_exec     (Execute DAT — pyserial LED送信ループ)
# ================================================================

import os

ROOT_PATH  = '/AudioLinkLight_V01'
LED_COLS   = 88
LED_ROWS   = 10
NUM_SCENES = 6

# ─────────────────────────────────────────────────────────────────
def deploy():
    root_op = op(ROOT_PATH)
    if root_op is None:
        print(f'[ERROR] {ROOT_PATH} が見つかりません')
        return

    print('=' * 60)
    print('[deploy_led_output] LED_OUTPUT を作成します')
    print('=' * 60)

    # ---- LED_OUTPUT Base COMP ----
    base = root_op.op('LED_OUTPUT')
    if base is None:
        base = root_op.create(baseCOMP, 'LED_OUTPUT')
        base.nodeX = 400
        base.nodeY = -800
        print(f'  [NEW] {base.path}')
    else:
        print(f'  [EXISTS] {base.path}')

    # ---- 既存ノードのクリーンアップ ----
    cleanup_names = [
        'scene_in_1', 'scene_in_2', 'scene_in_3', 'scene_in_4',
        'scene_in_5', 'scene_in_6',
        'scene_select', 'brightness', 'led_source',
        'led_preview', 'led_exec'
    ]
    for name in cleanup_names:
        old = base.op(name)
        if old is not None:
            try:
                old.par.active = False
            except:
                pass
            old.destroy()

    # ---- Select TOPs (各シーンの scene_out を参照) ----
    scene_ins = []
    for i in range(1, NUM_SCENES + 1):
        sel_name = f'scene_in_{i}'
        scene_path = f'{ROOT_PATH}/SCENE_{i}/scene_out'

        sel = base.create(selectTOP, sel_name)
        sel.par.top = scene_path
        sel.nodeX = (i - 1) * 200
        sel.nodeY = 0
        scene_ins.append(sel)
        print(f'  + {sel_name} (Select TOP → {scene_path})')

    # ---- Switch TOP (シーン切替) ----
    sw = base.create(switchTOP, 'scene_select')
    for i, sel in enumerate(scene_ins):
        sw.inputConnectors[i].connect(sel)
    sw.par.index = 0  # デフォルト: SCENE_1
    sw.nodeX = 200
    sw.nodeY = -200
    print(f'  + scene_select (Switch TOP, index=0)')

    # ---- Level TOP (輝度調整) ----
    lv = base.create(levelTOP, 'brightness')
    lv.par.opacity = 1.0
    lv.inputConnectors[0].connect(sw)
    lv.nodeX = 200
    lv.nodeY = -400
    print(f'  + brightness (Level TOP)')

    # ---- Null TOP: led_source (送信元) ----
    nl = base.create(nullTOP, 'led_source')
    nl.par.resolutionw = LED_COLS
    nl.par.resolutionh = LED_ROWS
    nl.inputConnectors[0].connect(lv)
    nl.nodeX = 200
    nl.nodeY = -600
    print(f'  + led_source (Null TOP, {LED_COLS}x{LED_ROWS})')

    # ---- Resolution TOP: led_preview (モニタープレビュー) ----
    preview = base.create(resolutionTOP, 'led_preview')
    preview.par.outputresolution = 'custom'
    preview.par.resolutionw = 880
    preview.par.resolutionh = 100
    preview.par.filtertype = 'nearest'  # ドットのまま拡大
    preview.inputConnectors[0].connect(nl)
    preview.nodeX = 500
    preview.nodeY = -600
    print(f'  + led_preview (Resolution TOP, 880x100)')

    # ---- Execute DAT: led_exec (pyserial LED送信) ----
    script_path = project.folder + '/scripts/dats/led_sender_pyserial.py'
    if not os.path.exists(script_path):
        print(f'  [WARN] {script_path} が見つかりません。led_exec は空で作成します。')
        script_content = '# led_sender_pyserial.py not found\n'
    else:
        with open(script_path, encoding='utf-8') as f:
            script_content = f.read()

    ex = base.create(executeDAT, 'led_exec')
    ex.par.framestart = True
    ex.par.active = False  # 安全のため OFF で作成
    ex.text = script_content
    ex.nodeX = 200
    ex.nodeY = -800
    print(f'  + led_exec (Execute DAT, active=False)')

    # ---- 完了メッセージ ----
    print()
    print('=' * 60)
    print('[deploy_led_output] LED_OUTPUT 構築完了！')
    print()
    print('【ノード構成】')
    print(f'  {base.path}/')
    print(f'    scene_in_1~4 → scene_select → brightness → led_source → led_preview')
    print(f'                                                    └── led_exec')
    print()
    print('【操作方法】')
    print('  # シーン切替 (0=SCENE_1, 1=SCENE_2, 2=SCENE_3, 3=SCENE_4)')
    print(f"  op('{base.path}/scene_select').par.index = 0")
    print()
    print('  # 輝度調整 (0.0 ~ 1.0)')
    print(f"  op('{base.path}/brightness').par.opacity = 0.8")
    print()
    print('  # LED送信 ON')
    print(f"  op('{base.path}/led_exec').par.active = True")
    print()
    print('  # LED送信 OFF')
    print(f"  op('{base.path}/led_exec').par.active = False")
    print('=' * 60)

deploy()
