# apply_led_sender_x.py
# TDのTextportで実行してください:
#   exec(open(project.folder + '/scripts/apply_led_sender_x.py', encoding='utf-8').read())

TARGET_COMP = '/AudioLinkLight_V01/LED_OUTPUT/LED_SOURCE_USB'

def run():
    base = op(TARGET_COMP)
    if not base:
        # 見つからない場合は作成を試みる（任意）
        print(f"WARNING: {TARGET_COMP} が見つかりません。新規作成します。")
        parent_path = '/AudioLinkLight_V01'
        p = op(parent_path)
        if p:
            base = p.create(baseCOMP, 'LED_SOURCE_USB')
            base.nodeX = 0
            base.nodeY = -1200
        else:
            print(f"ERROR: {parent_path} が見つかりません。")
            return

    # カスタムパラメータの追加または取得
    if not hasattr(base.par, 'Comport'):
        page = base.appendCustomPage('LED Config')
        page.appendStr('Comport', label='COM Port')
        page.appendInt('Baudrate', label='Baud Rate')
        page.appendStr('Sourcetop', label='Source TOP')
        page.appendInt('Ledcols', label='LED Columns')
        page.appendInt('Ledrows', label='LED Rows')
        print("Created new LED Config page")
    
    # 値を強制的に UNIT4 用に更新
    base.par.Comport = 'COM19'
    base.par.Baudrate = 2000000
    base.par.Sourcetop = '/AudioLinkLight_V01/LED_OUTPUT/led_source_USB'
    base.par.Ledcols = 81
    base.par.Ledrows = 12
    print(f"Forced update parameters for UNIT4 ({base.par.Comport}, 81x12)")

    # ノードの確認・作成
    ex = base.op('led_exec_x')
    if not ex:
        ex = base.create(executeDAT, 'led_exec_x')
        ex.par.framestart = True
        ex.nodeX = 400
        ex.nodeY = 0
    
    # 更新中は停止
    ex.par.active = False
    
    # スクリプトの読み込みと適用 (デバッグ版)
    script_path = project.folder + '/scripts/dats/led_sender_x_debug.py'
    try:
        with open(script_path, encoding='utf-8') as f:
            ex.text = f.read()
    except Exception as e:
        print(f"ERROR reading script file: {e}")
        return
    
    # 依存するTOPの確認
    if not base.op('led_source'):
        print(f"Hint: {base.path}/led_source TOP is missing. Please ensure data is flowing to this unit.")

    print(f"Successfully applied Generic sender to {ex.path}")
    print(f"Configured for {base.par.Comport.eval()}")
    print("READY TO ACTIVATE: op('"+ex.path+"').par.active = True")

if __name__ == '__main__':
    run()
