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
    # 旧名称 (led_exec_x, multiなど) があれば停止してから削除
    for legacy in ['led_exec_x', 'led_multi', 'led_exec_multi', 'led_exec_multi_relay']:
        old = base.op(legacy)
        if old:
            print(f"  [CLEANUP] Stopping and destroying legacy node: {old.path}")
            old.par.active = False
            try: old.run('stop')
            except: pass
            old.destroy()

    ex = base.op('led_exec')
    if not ex:
        ex = base.create(executeDAT, 'led_exec')
    else:
        # 既存ノードがある場合も一度停止させる
        ex.par.active = False
        try: ex.run('stop')
        except: pass
    
    ex.par.framestart = True
    ex.nodeX = 400
    ex.nodeY = 0
    
    # スクリプトの適用
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
    
    # 確実にエクスプレッションを上書き
    ex.par.active.mode = ParMode.CONSTANT
    ex.par.active = 0
    ex.par.active.mode = ParMode.EXPRESSION
    ex.par.active.expr = f"op('{btn.path}').panel.state"
    
    print(f"Done: {name} (via {btn.name}, node: {ex.name})")

def setup_global_reset():
    parent_path = '/AudioLinkLight_V01/LED_OUTPUT'
    parent = op(parent_path)
    if not parent: return

    btn = parent.op('RESET_Button')
    if not btn: return

    # --- プロジェクト全体を対象とした徹底クリーンアップ ---
    print("\n[CLEANUP] Purging ALL competing reset logic nodes...")
    
    # 1. 'led_exec_multi' 文字列を含む全DATを排除
    for n in root.findChildren(type=DAT):
        if n.isDAT and n.text and 'led_exec_multi' in n.text:
            if 'deploy_all_units' in n.name: continue
            print(f"  [DESTROY] Found legacy script containing 'led_exec_multi': {n.path}")
            try: n.par.active = False
            except: pass
            n.destroy()

    # 2. RESET_Button を監視している全 Panel Execute を検索（新名称以外）
    rex_unique_name = 'RESET_ALL_UNITS_LOGIC'
    for n in root.findChildren(type=panelexecuteDAT):
        if n.name == rex_unique_name: continue
        
        panel_path = str(getattr(n.par, 'panel', ''))
        if btn.path in panel_path or btn.name in panel_path:
            print(f"  [DESTROY] Found competing Panel Execute linked to RESET_Button: {n.path}")
            n.destroy()

    # 3. 新しいリセットロジックの作成
    rex = parent.op(rex_unique_name)
    if rex: rex.destroy()
    rex = parent.create(panelexecuteDAT, rex_unique_name)
    
    rex.par.panel = btn.path
    rex.par.valuechange = True
    rex.nodeX = btn.nodeX
    rex.nodeY = btn.nodeY - 100
    
    script = """# Automatically generated Blackout-Reset logic (v12)
def onValueChange(panelValue):
    if panelValue.name == 'state' and panelValue.val == 1:
        print('\\n--- GLOBAL BLACKOUT & RESET TRIGGERED ---')
        
        containers = [
            'led_source_u1', 'led_source', 'led_source_d1', 'led_source_USB'
        ]
        
        # Step 1: 各ユニットにブラックアウト信号を送信
        for c_name in containers:
            c = parent().op(c_name)
            if not c: continue
            ex = c.op('led_exec')
            if ex and hasattr(ex.module, '_ser') and ex.module._ser:
                ser = ex.module._ser
                if ser.is_open:
                    try:
                        num_leds = c.par.Ledcols.eval() * c.par.Ledrows.eval()
                        header = bytes([0x55, 0xAA, num_leds & 0xFF, (num_leds >> 8) & 0xFF])
                        blackout = header + bytes(num_leds * 3)
                        ser.write(blackout)
                        ser.flush()
                        print(f'  [BLACKOUT] Sent to {c_name}')
                    except: pass

        # Step 2: 全ポートを強制クローズ (5フレーム後)
        def step_close():
            for c_name in containers:
                c = parent().op(c_name)
                if c and c.op('led_exec'):
                    node = c.op('led_exec')
                    node.par.active = False
                    try: node.run('stop')
                    except: pass
                    print(f'  [CLOSED] {c_name}')

        run("args[0]()", step_close, delayFrames=5)
        
        # Step 3: 全ポートを再開 (55フレーム後)
        def step_open():
            for c_name in containers:
                c = parent().op(c_name)
                if c and c.op('led_exec'):
                    c.op('led_exec').par.active = True
                    print(f'  [RESTARTED] {c_name}')
            print('--- RESET SEQUENCE COMPLETE ---')

        run("args[0]()", step_open, delayFrames=55)
"""
    rex.text = script
    print(f"  [LOGIC] RESET_Button link established ONLY via {rex.path}")

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

# メイン処理
print("\n--- DEPLOY START (v12: MEGA CLEAN) ---")

parent = op('/AudioLinkLight_V01/LED_OUTPUT')
if parent:
    # 既存の競合リセットノードを掃除してから構築
    setup_global_reset()

    for u in units:
        setup_unit(*u)

print("\n--- DEPLOY COMPLETE (v12) ---")
print("All legacy references scrubbed. RESET_Button logic updated with Blackout.")
