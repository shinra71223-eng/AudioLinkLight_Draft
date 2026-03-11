def run():
    print("--- FORCING SERIAL PORT CLEANUP ---")
    # 全てのExecute DATを検索し、それらしいものを全て停止
    for n in root.findChildren(type=executeDAT):
        low_name = n.name.lower()
        if 'led' in low_name or 'exec' in low_name:
            n.par.active = False
            # スクリプト内の stop 関数を直接呼ぶ試み
            try:
                n.run('stop')
            except:
                pass
            print(f"  [STOPPED] {n.path}")
    
    # ユーザーに物理的な抜き差しも案内する
    print("\nPorts should be released in TD.")
    print("If still failing, please UNPLUG and RE-PLUG ESP32 USB cables.")

if __name__ == '__main__':
    run()
