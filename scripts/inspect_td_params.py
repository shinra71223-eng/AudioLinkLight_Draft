# inspect_td_params.py
# ================================================================
# TouchDesigner の TOP パラメータを調査するためのスクリプト
# ================================================================

def inspect_nodes():
    root = op('/AudioLinkLight_V01')
    if root is None:
        print("[ERROR] /AudioLinkLight_V01 が見つかりません。")
        return

    # 調査対象のノードタイプ
    targets = [
        ('Noise TOP', noiseTOP),
        ('Rectangle TOP', rectangleTOP),
        ('Movie File Out TOP', moviefileoutTOP),
        ('Composite TOP', compositeTOP),
        ('Blur TOP', blurTOP)
    ]

    print("\n" + "="*60)
    print("【TD パラメータ調査レポート】")
    print("="*60)

    for label, op_type in targets:
        print(f"\n▼ {label} ({op_type.__name__})")
        # 一時的なノードを作成
        tmp = root.create(op_type, 'tmp_inspect_node')
        
        # 全パラメータを表示 (名前 : ラベル)
        pars = tmp.pars()
        # アルファベット順にソートして見やすくする
        pars.sort(key=lambda p: p.name)
        
        for p in pars:
            # page が None の場合があるため安全に処理
            page = "N/A"
            if hasattr(p, 'page') and p.page is not None:
                page = p.page.name
            print(f"  {p.name:20s} | {p.label:20s} (Page: {page})")
            
        # 削除
        tmp.destroy()

    print("\n" + "="*60)
    print("調査完了。この出力をコピーして教えてください。")
    print("="*60)

if __name__ == '__main__':
    inspect_nodes()
