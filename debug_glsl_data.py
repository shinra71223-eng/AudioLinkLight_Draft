# debug_glsl_data.py
import traceback

def debug():
    try:
        glsl = op('/AudioLinkLight_V01/TEST_SCREEN2/cyber_clock_v2')
        out1 = op('/AudioLinkLight_V01/AudioLinkCore/out1')
        
        if not glsl:
            print("Error: GLSL TOP not found.")
            return

        print(f"\n=== Debugging GLSL: {glsl.path} ===")
        
        # 1. 基礎Vector変数のチェック
        print("\n[Vector Uniforms]")
        for i in range(10):
            name = getattr(glsl.par, f'uniname{i}').eval()
            if name:
                val = getattr(glsl.par, f'value{i}x').eval()
                expr = getattr(glsl.par, f'value{i}x').expr
                print(f"  {name}: value={val:.4f}, expression='{expr}'")

        # 2. Array変数のチェック
        print("\n[Array (CHOP) Uniforms]")
        if hasattr(glsl.par, 'array0name'):
            array_name = glsl.par.array0name.eval()
            array_chop = glsl.par.array0chop.eval()
            print(f"  array0name: '{array_name}'")
            print(f"  array0chop: '{array_chop}'")
            
            if array_chop:
                chop_node = op(array_chop)
                if chop_node:
                    print(f"  CHOP Status: {chop_node.name} has {len(chop_node.chans())} channels.")
                    # 最初の数チャンネルの現在値を表示
                    for i, c in enumerate(chop_node.chans()):
                        if i < 5 or c.name in ['uVocalOnset', 'Kick', 'uBassEnergy']:
                            print(f"    CHOP[{i}] ({c.name}): {c.eval():.4f}")
                else:
                    print(f"  ERROR: CHOP node at '{array_chop}' not found!")
        else:
            print("  ERROR: This GLSL TOP does not have 'array0name' parameter.")

        # 3. エラー・コンパイル状態のチェック
        print("\n[Shader Status]")
        print(f"  Warnings/Errors: {glsl.warnings}")
        
    except Exception as e:
        traceback.print_exc()

debug()
