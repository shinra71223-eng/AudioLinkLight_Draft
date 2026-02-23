import traceback

try:
    glsl = op('/AudioLinkLight_V01/TEST_SCREEN2/cyber_clock_v2')
    if glsl:
        print(f"\n--- Checking Parameters for {glsl.path} ---")
        
        # Check standard Vectors (uniname0, value0x, etc.)
        for i in range(10):
            par_name = f'uniname{i}'
            if hasattr(glsl.par, par_name):
                name_val = getattr(glsl.par, par_name).eval()
                if name_val:
                    # check what value is driving this
                    v0 = getattr(glsl.par, f'value{i}x').eval()
                    expr = getattr(glsl.par, f'value{i}x').expr
                    print(f"[Vector] {name_val}: val={v0:.3f}, expr='{expr}'")
        
        # Check Arrays (chop0, unichop0, etc.)
        for i in range(10):
            chop_par = f'chop{i}'
            if hasattr(glsl.par, chop_par):
                chop_val = getattr(glsl.par, chop_par).eval()
                if chop_val:
                    chop_name = getattr(glsl.par, f'unichop{i}').eval()
                    print(f"[CHOP Array] {chop_name}: linked to CHOP='{chop_val}'")
                    
        print("--- Parameter Check Complete ---\n")
    else:
        print("Error: cyber_clock_v2 not found!")
except Exception as e:
    traceback.print_exc()
