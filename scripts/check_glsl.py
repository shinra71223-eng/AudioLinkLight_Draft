# scripts/check_glsl.py
import traceback

try:
    print("--- Checking GLSL TOP Parameters ---")
    polish = op('/AudioLinkLight_V01/TEST_SCREEN')
    if polish:
        glsl = polish.create(glslTOP, 'temp_glsl_check')
        # pixel, dat, shaderなどに関連するパラメーター名を抽出
        matching_pars = [p.name for p in glsl.pars() if 'pixel' in p.name.lower() or 'dat' in p.name.lower()]
        print(f"Matching parameters: {matching_pars}")
        glsl.destroy()
    else:
        print("TEST_SCREEN not found.")
except Exception as e:
    print(f"Error: {e}")
    traceback.print_exc()
