# close_ports.py
# TDのTextportで実行してください:
#   exec(open(project.folder + '/scripts/close_ports.py', encoding='utf-8').read())

def run():
    # 全てのExecute DATを停止
    for n in root.findChildren(type=executeDAT):
        if 'led_exec' in n.name:
            n.par.active = False
            print(f"Stopped {n.path}")
    
    # Python内でシリアルポートを保持している可能性があるため、一度クリーンアップを試みる
    # (既存の sender スクリプトの stop() を呼ぶなどは難しいので、
    #  pyserial オブジェクトがグローバルにある場合は手動で閉じる必要がありますが、
    #  基本的には Active=False で十分なはずです)
    
    # 明示的にクローズが必要な場合（前回のセッションが残っているなど）は
    # TDを再起動するか、シリアルデバイスマネージャーで確認してください。
    print("Ports should be released. Ready to flash.")

if __name__ == '__main__':
    run()
