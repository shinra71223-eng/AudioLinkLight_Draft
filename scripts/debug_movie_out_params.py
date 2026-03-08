# debug_movie_out_params.py
# ================================================================
# Movie File Out TOP のパラメータ名を書き出す
# ================================================================

def dump_movie_params():
    # 一時的に Movie File Out TOP を作成
    scene = op('/AudioLinkLight_V01/SCENE_2')
    if scene is None:
        print("SCENE_2 NOT FOUND!")
        return
        
    m = scene.create(moviefileoutTOP, 'tmp_movie_dump')
    print(f"\n--- Movie File Out TOP パラメータ一覧 ---")
    
    # 全パラメータ名を出力
    for p in m.pars():
        print(f"Name: {p.name:20s} Label: {p.label} Value: {p.val}")
    
    m.destroy()

if __name__ == '__main__':
    dump_movie_params()
