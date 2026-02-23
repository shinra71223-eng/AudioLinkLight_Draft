# diagnose_vocal_signal_and_error.py
import traceback

def diagnose():
    try:
        glsl = op('/AudioLinkLight_V01/TEST_SCREEN2/cyber_clock_v2')
        core = op('/AudioLinkLight_V01/AudioLinkCore/out1')
        sel = op('/AudioLinkLight_V01/TEST_SCREEN2/vocal_select')
        trigger = op('/AudioLinkLight_V01/TEST_SCREEN2/vocal_trigger')
        
        print("\n=== AudioLink Connectivity Check ===")
        if core:
            print(f"Core CHOP: {core.path}")
            print(f"  Available Channels: {[c.name for c in core.chans()]}")
        else:
            print("ERROR: AudioLinkCore/out1 not found!")

        print("\n=== Vocal Select Check ===")
        if sel:
            print(f"Select Node: {sel.path}")
            print(f"  Selected Channels (par.channames): '{sel.par.channames.eval()}'")
            print(f"  Resulting Channels: {[c.name for c in sel.chans()]}")
            if len(sel.chans()) == 0:
                 print("  WARNING: vocal_select has NO CHANNELS.")
        else:
            print("ERROR: vocal_select not found!")

        print("\n=== GLSL Parameter Type Check ===")
        if glsl:
            print(f"GLSL Node: {glsl.path}")
            for i in range(10):
                name = getattr(glsl.par, f'uniname{i}').eval()
                val_par = getattr(glsl.par, f'value{i}x')
                if name:
                    try:
                        v = val_par.eval()
                        print(f"  Slot {i} ({name}): value={v}, type={type(v)}")
                    except Exception as e:
                        print(f"  Slot {i} ({name}): FAILED to eval. Expr='{val_par.expr}', Error={e}")
        
    except Exception as e:
        traceback.print_exc()

diagnose()
