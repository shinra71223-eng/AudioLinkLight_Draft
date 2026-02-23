# baseline_scan.py
import traceback

def scan():
    try:
        print("\n=== Baseline Scan (AudioLinkLight_V03_b01) ===")
        
        # 1. Identify active GLSL
        # We look for TEST_SCREEN2 specifically as before
        glsl = None
        for c in op('/').findChildren(type=glslTOP):
            if 'TEST_SCREEN2' in c.path:
                glsl = c
                break
        
        if not glsl:
            print("GLSL TOP in TEST_SCREEN2 not found. Checking root children...")
            for c in op('/').findChildren(type=glslTOP):
                 print(f"  Available GLSL: {c.path}")
            return

        print(f"Found Active GLSL: {glsl.path}")
        
        # 2. Identify the Pixel DAT
        pixel_dat = op(glsl.par.pixeldat.eval())
        if pixel_dat:
             print(f"Linked Pixel DAT: {pixel_dat.path}")
             # Let's see the first few lines to know what's there
             lines = pixel_dat.text.splitlines()
             print("\n--- Current GLSL Code (Top 20 lines) ---")
             for l in lines[:20]:
                 print(l)
        else:
             print("No Pixel DAT linked!")

        # 3. Check existing Uniforms
        print("\n[Current Uniform Vectors]")
        for i in range(10):
            u_name = getattr(glsl.par, f'uniname{i}').eval()
            if u_name:
                expr = getattr(glsl.par, f'value{i}x').expr
                print(f"  {u_name} in slot {i}: {expr}")

        # 4. Check for Audio CHOP
        core_out = op('/AudioLinkLight_V01/AudioLinkCore/out1')
        if core_out:
            print(f"\nAudio CHOP found: {core_out.path}")
            print(f"Channels: {[c.name for c in core_out.chans()]}")
        else:
            print("\nAudioLinkCore/out1 NOT FOUND at expected path.")

    except Exception as e:
        traceback.print_exc()

scan()
