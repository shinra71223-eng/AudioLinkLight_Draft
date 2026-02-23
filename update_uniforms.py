import traceback

try:
    glsl = op('/AudioLinkLight_V01/TEST_SCREEN2/cyber_clock_v2')
    if glsl:
        print(f"--- Updating Parameters for {glsl.path} ---")
        
        # We need to add uVibrato, uKick, uSnare, and uOnset.
        # Let's find the first available uniname slots.
        
        new_uniforms = [
            ('uVibrato', "op('/AudioLinkLight_V01/AudioLinkCore/out1')['uVocalVibrato'] if op('/AudioLinkLight_V01/AudioLinkCore/out1') else 0.0"),
            ('uKick', "op('/AudioLinkLight_V01/AudioLinkCore/out1')['Kick'] if op('/AudioLinkLight_V01/AudioLinkCore/out1') else 0.0"),
            ('uSnare', "op('/AudioLinkLight_V01/AudioLinkCore/out1')['Snare'] if op('/AudioLinkLight_V01/AudioLinkCore/out1') else 0.0"),
            ('uOnset', "op('/AudioLinkLight_V01/AudioLinkCore/out1')['uVocalOnset'] if op('/AudioLinkLight_V01/AudioLinkCore/out1') else 0.0")
        ]
        
        idx = 0
        added_count = 0
        
        # 10スロット(uniname0 ~ uniname9)しかないため、足りなければ警告を出す
        # まず空いているスロットを探して埋める
        while added_count < len(new_uniforms) and idx < 10:
            name_par = getattr(glsl.par, f'uniname{idx}')
            val_par = getattr(glsl.par, f'value{idx}x')
            
            # 既存の名前かをチェック。既にあれば上書き（念のため）
            if name_par.eval() == new_uniforms[added_count][0]:
                val_par.expr = new_uniforms[added_count][1]
                print(f"Updated {name_par.eval()} in slot {idx}")
                added_count += 1
            # 空きスロットなら新規追加
            elif name_par.eval() == '':
                name_par.val = new_uniforms[added_count][0]
                val_par.expr = new_uniforms[added_count][1]
                print(f"Added {new_uniforms[added_count][0]} to slot {idx}")
                added_count += 1
                
            idx += 1
            
        if added_count < len(new_uniforms):
            print("Warning: Not enough uniform slots available (max 10).")
            print("To fix this, we need to pass data as a CHOP array instead of individual vectors.")
        else:
            print("Successfully updated all required parameters!")
            
    else:
        print("Error: cyber_clock_v2 not found!")
except Exception as e:
    traceback.print_exc()
