# debug_glsl_v3.py
import traceback

def debug():
    try:
        glsl = op('/AudioLinkLight_V01/TEST_SCREEN2/cyber_clock_v2')
        print(f"\n=== GLSL DEBUG (V3) ===")
        
        if not glsl:
             print("GLSL node not found.")
             return

        # 1. Check Compiler Errors (Correcting method call)
        print(f"\n[GLSL Status]")
        print(f"  Errors:\n{glsl.errors()}")
        print(f"  Warnings:\n{glsl.warnings()}")
        
        # 2. Search for any node with 'clock' or 'time'
        print("\n[Searching for nodes related to 'clock' or 'time'...]")
        matches = [c for c in op('/AudioLinkLight_V01').findChildren(name='*clock*')]
        matches += [c for c in op('/AudioLinkLight_V01').findChildren(name='*time*')]
        
        if matches:
            # unique paths
            paths = list(set([m.path for m in matches]))
            for p in paths:
                print(f"  Found: {p}")
        else:
            print("  No nodes with 'clock' or 'time' in name found in /AudioLinkLight_V01.")

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
