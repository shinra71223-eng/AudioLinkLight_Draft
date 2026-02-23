# diagnose_error_v4.py
import traceback

def diagnose():
    try:
        glsl = op('/AudioLinkLight_V01/TEST_SCREEN2/cyber_clock_v2')
        print(f"\n=== Diagnosing GLSL: {glsl.path} ===")
        
        # 1. Check all vector slots
        for i in range(10):
            name_par = getattr(glsl.par, f'uniname{i}')
            val_par = getattr(glsl.par, f'value{i}x')
            print(f"Slot {i}:")
            print(f"  Name: '{name_par.eval()}' (Expr: '{name_par.expr}')")
            try:
                print(f"  Value: {val_par.eval()} (Type: {type(val_par.eval())})")
            except Exception as e:
                print(f"  Value Error: {e}")
            print(f"  Expression: '{val_par.expr}'")

        # 2. Check Trigger CHOP
        trigger = op('/AudioLinkLight_V01/TEST_SCREEN2/vocal_trigger')
        if trigger:
            print(f"\nTrigger CHOP: {trigger.path}")
            print(f"  Num Chan: {len(trigger.chans())}")
            if len(trigger.chans()) > 0:
                print(f"  Active Value: {trigger[0].eval()}")
        else:
            print("\nTrigger CHOP NOT FOUND!")

    except Exception as e:
        traceback.print_exc()

diagnose()
