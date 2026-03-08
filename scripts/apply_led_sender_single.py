# apply_led_sender_single.py
# TDのTextportで実行してください:
#   exec(open(project.folder + '/scripts/apply_led_sender_single.py', encoding='utf-8').read())

TARGET_COMP = '/AudioLinkLight_V01/LED_OUTPUT'

def run():
    base = op(TARGET_COMP)
    if not base:
        print(f"ERROR: {TARGET_COMP} が見つかりません。")
        return

    print(f"Updating {base.path}/led_exec with SINGLE source sender...")
    
    # ノードの確認・作成
    ex = base.op('led_exec')
    if not ex:
        ex = base.create(executeDAT, 'led_exec')
        ex.par.framestart = True
        ex.nodeX = 400
        ex.nodeY = -800
    
    # 更新中は停止
    ex.par.active = False
    
    # スクリプトの読み込みと適用
    script_path = project.folder + '/scripts/dats/led_sender_single.py'
    try:
        with open(script_path, encoding='utf-8') as f:
            ex.text = f.read()
    except Exception as e:
        print(f"ERROR reading script file: {e}")
        return
    
    # led_source TOPの確認（存在しない場合は作成）
    if not base.op('led_source'):
        n = base.create(nullTOP, 'led_source')
        n.nodeX = 200
        n.nodeY = -600
        print(f"Created missing node: led_source")

    print(f"Successfully applied SINGLE source sender to {ex.path}")
    print("READY TO ACTIVATE: op('"+ex.path+"').par.active = True")

if __name__ == '__main__':
    run()
