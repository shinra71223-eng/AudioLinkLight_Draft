import traceback

try:
    glsl = op('/AudioLinkLight_V01/TEST_SCREEN2/cyber_clock_v2')
    pixel_dat = op('/AudioLinkLight_V01/TEST_SCREEN2/cyber_clock_v2_pixel22')
    out1_chop = op('/AudioLinkLight_V01/AudioLinkCore/out1')
    # Corrected clock path found by scan
    clock_chop = op('/AudioLinkLight_V01/TEST_SCREEN2/clock_updater_v2')
    
    glsl_file_path = project.folder + '/scripts/cyber_clock_v2.glsl'
    
    if glsl and pixel_dat and out1_chop and clock_chop:
        print(f"--- Deploying and Configuring {glsl.path} ---")
        
        # 1. Load GLSL code from file and apply to DAT
        with open(glsl_file_path, 'r', encoding='utf-8') as f:
            code = f.read()
            pixel_dat.text = code
        print(f"Updated GLSL code in {pixel_dat.path}")
        
        # 2. Clear old vector uniforms (prevent name conflicts)
        for i in range(10):
            getattr(glsl.par, f'uniname{i}').val = ''
            getattr(glsl.par, f'value{i}x').expr = ''
            getattr(glsl.par, f'value{i}x').val = 0.0
        print("Cleared old vector uniforms.")
        
        # 3. Re-assign core Vector uniforms (Time and Clock)
        glsl.par.uniname0 = 'uTime'
        glsl.par.value0x.expr = 'absTime.seconds'
        
        # Use the found clock_updater_v2 CHOP
        glsl.par.uniname1 = 'uHour'
        glsl.par.value1x.expr = f"op('{clock_chop.path}')['hour']"
        glsl.par.uniname2 = 'uMinute'
        glsl.par.value2x.expr = f"op('{clock_chop.path}')['minute']"
        glsl.par.uniname3 = 'uSecond'
        glsl.par.value3x.expr = f"op('{clock_chop.path}')['second']"
        print("Re-assigned time vectors using clock_updater_v2.")

        # 4. Configure CHOP Array (uAudio)
        if hasattr(glsl.par, 'array'):
            glsl.par.array = 1 
        glsl.par.array0name = 'uAudio'
        glsl.par.array0chop = out1_chop.path
        
        # 5. Clear problematic legacy pars if they exist
        for p_name in ['chop0', 'unichop0']:
            if hasattr(glsl.par, p_name):
                getattr(glsl.par, p_name).val = ''

        print(f"Linked {out1_chop.path} to 'uAudio' array.")
        
        # Force cook
        glsl.cook(force=True)
        print("Done! Deployed successfully!")
            
    else:
        print("Error: Required nodes not found.")
        print(f"GLSL: {'OK' if glsl else 'MISS'} | DAT: {'OK' if pixel_dat else 'MISS'}")
        print(f"CHOP: {'OK' if out1_chop else 'MISS'} | Clock: {'OK' if clock_chop else 'MISS'}")
except Exception as e:
    traceback.print_exc()
