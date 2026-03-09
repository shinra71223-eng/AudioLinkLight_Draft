# deploy_u1_d1.py
# TDのTextportで実行してください:
#   exec(open(project.folder + '/scripts/deploy_u1_d1.py', encoding='utf-8').read())

def setup_unit(name, source_top, com_port):
    parent_path = '/AudioLinkLight_V01/LED_OUTPUT'
    parent = op(parent_path)
    if not parent:
        print(f"ERROR: {parent_path} not found.")
        return

    # コンテナの作成または取得
    base = parent.op(name)
    if not base:
        base = parent.create(baseCOMP, name)
        print(f"Created {base.path}")
    
    # カスタムパラメータ設定
    if not hasattr(base.par, 'Comport'):
        page = base.appendCustomPage('LED Config')
        page.appendStr('Comport', label='COM Port')
        page.appendInt('Baudrate', label='Baud Rate')
        page.appendStr('Sourcetop', label='Source TOP')
        page.appendInt('Ledcols', label='LED Columns')
        page.appendInt('Ledrows', label='LED Rows')
    
    # 値のセット (88x10, PIN固定などはUNIT2と同じ前提)
    base.par.Comport = com_port
    base.par.Baudrate = 2000000
    base.par.Sourcetop = source_top
    base.par.Ledcols = 88
    base.par.Ledrows = 10
    
    # 送信先TOPの確認・作成 (無い場合はNull TOPを作成)
    src_node = op(source_top)
    if not src_node:
        print(f"  [INFO] {source_top} not found. Creating placeholder Null TOP...")
        base_name = source_top.split('/')[-1]
        src_node = parent.create(nullTOP, base_name)
        src_node.par.resolutionw = 88
        src_node.par.resolutionh = 10;
        src_node.nodeX = -200
        src_node.nodeY = -600
    
    # Execute DAT の作成
    ex = base.op('led_exec_x')
    if not ex:
        ex = base.create(executeDAT, 'led_exec_x')
        ex.par.framestart = True
        ex.nodeX = 400
        ex.nodeY = 0
    
    # スクリプトの適用 (汎用デバッグ版を使用)
    script_path = project.folder + '/scripts/dats/led_sender_x_debug.py'
    try:
        with open(script_path, encoding='utf-8') as f:
            ex.text = f.read()
    except Exception as e:
        print(f"  [ERROR] Failed to read script: {e}")
        return
    
    ex.par.active = False # 最初は安全のためOFF
    print(f"Setup complete for {name} -> {source_top}")

# UNIT 1 Setup
setup_unit('LED_SOURCE_U1', '/AudioLinkLight_V01/LED_OUTPUT/led_source_u1', 'COM1')

# UNIT 2 Setup (Original)
setup_unit('LED_SOURCE_UNIT2', '/AudioLinkLight_V01/LED_OUTPUT/led_source', 'COM21')

# UNIT 3 Setup
setup_unit('LED_SOURCE_D1', '/AudioLinkLight_V01/LED_OUTPUT/led_source_d1', 'COM3')

print("\n--- ALL DONE ---")
print("Please check LED Config parameters in LED_OUTPUT/LED_SOURCE_U1 and D1")
