# debug_rect_params.py
# ================================================================
# Rectangle TOP のパラメータ名を書き出す
# ================================================================

def dump_rect_params():
    # 一時的に Rectangle TOP を作成
    scene = op('/AudioLinkLight_V01/SCENE_4')
    if scene is None:
        print("SCENE_4 NOT FOUND!")
        return
        
    r = scene.create(rectangleTOP, 'tmp_rect_dump')
    print(f"\n--- Rectangle TOP パラメータ一覧 ---")
    
    # 全パラメータ名を出力 (特にサイズと位置に関連するもの)
    for p in r.pars():
        if any(keyword in p.name.lower() for keyword in ['size', 'width', 'height', 'center', 'pos']):
            print(f"Name: {p.name:20s} Label: {p.label:20s} Value: {p.val}")
    
    r.destroy()

if __name__ == '__main__':
    dump_rect_params()
