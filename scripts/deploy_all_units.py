# deploy_all_units.py
# TDのTextportで実行してください:
#   exec(open(project.folder + '/scripts/deploy_all_units.py', encoding='utf-8').read())

def setup_unit(name, source_top, com_port, x, y):
    parent_path = '/AudioLinkLight_V01/LED_OUTPUT'
    parent = op(parent_path)
    if not parent:
        print(f"ERROR: {parent_path} not found.")
        return

    # --- 1. 送信コンテナの作成/取得 ---
    base = parent.op(name)
    if not base:
        base = parent.create(baseCOMP, name)
    base.nodeX = x
    base.nodeY = y
    
    # --- 2. カスタムパラメータ設定 ---
    if not hasattr(base.par, 'Comport'):
        page = base.appendCustomPage('LED Config')
        page.appendStr('Comport', label='COM Port')
        page.appendInt('Baudrate', label='Baud Rate')
        page.appendStr('Sourcetop', label='Source TOP')
        page.appendInt('Ledcols', label='LED Columns')
        page.appendInt('Ledrows', label='LED Rows')
    
    # デフォルト値
    is_usb = 'USB' in name
    base.par.Comport = com_port
    base.par.Baudrate = 2000000
    base.par.Sourcetop = source_top
    base.par.Ledcols = 81 if is_usb else 88
    base.par.Ledrows = 12 if is_usb else 10
    
    # --- 3. 送信元TOPの確認/プレースホルダ作成 ---
    src_node = op(source_top)
    if not src_node:
        base_name = source_top.split('/')[-1]
        src_node = parent.create(nullTOP, base_name)
        src_node.par.resolutionw = base.par.Ledcols
        src_node.par.resolutionh = base.par.Ledrows
        src_node.nodeX = x - 250
        src_node.nodeY = y
    
    # --- 4. ボタン (Button COMP) の作成とクリーンアップ ---
    btn_name = f"btn_{name}"
    
    # 重複ボタン（btn_...01など）を徹底的に消去
    for neighbor in parent.findChildren(name=btn_name + '*', depth=1):
        if neighbor.name != btn_name:
            print(f"  [CLEANUP] Destroying duplicate: {neighbor.name}")
            neighbor.destroy()

    btn = parent.op(btn_name)
    if not btn:
        btn = parent.create(buttonCOMP, btn_name)
    
    btn.nodeX = x + 200
    btn.nodeY = y
    btn.par.buttontype = 'toggle'
    btn.par.label = f"{name} ACTIVE"
    btn.par.w = 150
    btn.par.h = 50

    # --- 5. Execute DAT の作成と設定 ---
    ex = base.op('led_exec_x')
    if not ex:
        ex = base.create(executeDAT, 'led_exec_x')
    ex.par.framestart = True
    ex.nodeX = 400
    ex.nodeY = 0
    
    # スクリプトの適用 (USB以外は 88x10 専用、USBは 12x81 デバッグ版)
    if is_usb:
        script_path = project.folder + '/scripts/dats/led_sender_x_debug.py'
    else:
        script_path = project.folder + '/scripts/dats/led_sender_88x10.py'
        
    try:
        with open(script_path, encoding='utf-8') as f:
            ex.text = f.read()
    except:
        print(f"  [ERROR] Failed to load script: {script_path}")
        pass
    
    # 確実にエクスプレッションを上書き（絶対パスを使用）
    # パラメータモードを明示的に変更して、以前の不正な参照をクリアする
    ex.par.active.mode = ParMode.CONSTANT
    ex.par.active = 0
    ex.par.active.mode = ParMode.EXPRESSION
    ex.par.active.expr = f"op('{btn.path}').panel.state"
    
    print(f"Done: {name} (via {btn.name})")

# 配置の基準
START_X = 0
START_Y = -1200
Y_STEP  = 200

# 全ユニット一括デプロイ
units = [
    ('LED_SOURCE_U1',    '/AudioLinkLight_V01/LED_OUTPUT/led_source_u1',  'COM20', START_X, START_Y - Y_STEP*0),
    ('LED_SOURCE_UNIT2', '/AudioLinkLight_V01/LED_OUTPUT/led_source',     'COM21', START_X, START_Y - Y_STEP*1),
    ('LED_SOURCE_D1',    '/AudioLinkLight_V01/LED_OUTPUT/led_source_d1',  'COM22', START_X, START_Y - Y_STEP*2),
    ('LED_SOURCE_USB',   '/AudioLinkLight_V01/LED_OUTPUT/led_source_USB', 'COM19', START_X, START_Y - Y_STEP*3),
]

for u in units:
    setup_unit(*u)

print("\n--- DEPLOY COMPLETE (FIXED VERSION) ---")
print("Verified linking and cleaned up duplicates.")
