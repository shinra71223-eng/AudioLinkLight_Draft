# debug_noise_params.py
# ================================================================
# Noise TOP のパラメータ名を一列に書き出す
# ================================================================

def dump_noise_params():
    target = op('/AudioLinkLight_V01/SCENE_2/pat_noise')
    if target is None:
        print("Noise TOP NOT FOUND!")
        return
        
    print(f"\n--- Noise TOP: {target.path} ---")
    print(f"Noise Type: {target.par.type}")
    
    # 全パラメータ名を出力
    for p in target.pars():
        print(f"Name: {p.name:20s} Label: {p.label}")

if __name__ == '__main__':
    dump_noise_params()
