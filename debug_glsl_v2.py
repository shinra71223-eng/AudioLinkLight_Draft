# debug_glsl_v2.py
import traceback

def debug():
    try:
        glsl = op('/AudioLinkLight_V01/TEST_SCREEN2/cyber_clock_v2')
        print(f"\n=== GLSL DEBUG (Detailed) ===")
        
        if not glsl:
             print("GLSL node not found.")
             return

        # 1. Check Compiler Errors
        print(f"\n[GLSL Status]")
        print(f"  Errors: {glsl.errors}")
        print(f"  Warnings: {glsl.warnings}")
        
        # 2. Find clock_dat
        print("\n[Searching for 'clock_dat'...]")
        matches = [c for c in op('/AudioLinkLight_V01').findChildren(name='clock_dat')]
        if matches:
            for m in matches:
                print(f"  Found at: {m.path}")
        else:
            print("  'clock_dat' NOT FOUND anywhere in /AudioLinkLight_V01.")

        # 3. Check values reaching the Vector uniforms
        print("\n[Vector Uniforms Check]")
        for i in range(10):
            uniname = getattr(glsl.par, f'uniname{i}').eval()
            if uniname:
                val = getattr(glsl.par, f'value{i}x').eval()
                expr = getattr(glsl.par, f'value{i}x').expr
                print(f"  {uniname}: {val:.4f} (Expr: {expr})")

    except Exception as e:
        traceback.print_exc()

debug()
