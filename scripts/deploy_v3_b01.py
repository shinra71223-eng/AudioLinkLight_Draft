# scripts/deploy_v3_b01.py
import traceback

try:
    # 1. Target nodes (Confirmed by baseline_scan.py)
    glsl = op('/AudioLinkLight_V01/TEST_SCREEN2/cyber_clock_v2')
    pixel_dat = op('/AudioLinkLight_V01/TEST_SCREEN2/cyber_clock_v2_pixel22')
    audio_chop = op('/AudioLinkLight_V01/AudioLinkCore/out1')
    clock_chop = op('/AudioLinkLight_V01/TEST_SCREEN2/clock_updater_v2')
    
    glsl_file = project.folder + '/scripts/cyber_clock_v2.glsl'
    
    if glsl and pixel_dat and audio_chop and clock_chop:
        print("\n--- Starting Verified Deployment (V03_b01) ---")
        
        # A. Update GLSL Code
        with open(glsl_file, 'r', encoding='utf-8') as f:
            pixel_dat.text = f.read()
        print(f"1. Updated code in: {pixel_dat.path}")
        
        # B. Reset Vector Parameters (Slots 0-9)
        # We only need 4 slots for Time/Clock now
        for i in range(10):
            getattr(glsl.par, f'uniname{i}').val = ''
            getattr(glsl.par, f'value{i}x').expr = ''
            getattr(glsl.par, f'value{i}x').val = 0.0
            
        glsl.par.uniname0, glsl.par.value0x.expr = 'uTime', 'absTime.seconds'
        glsl.par.uniname1, glsl.par.value1x.expr = 'uHour', f"op('{clock_chop.path}')['hour']"
        glsl.par.uniname2, glsl.par.value2x.expr = 'uMinute', f"op('{clock_chop.path}')['minute']"
        glsl.par.uniname3, glsl.par.value3x.expr = 'uSecond', f"op('{clock_chop.path}')['second']"
        print(f"2. Mapped Clock to: {clock_chop.path}")

        # C. Configure CHOP Array (The "uAudio" mapping)
        # Using verified parameter names: array0name, array0chop
        glsl.par.array = 1 # Enable arrays
        glsl.par.array0name = 'uAudio'
        glsl.par.array0chop = audio_chop.path
        print(f"3. Mapped Audio Array: {audio_chop.path} -> uAudio")
        
        # D. Final sync
        glsl.cook(force=True)
        print("\n--- DEPLOYMENT COMPLETE: Visuals should be active! ---")
    else:
        print("Error: Missing required nodes. Please check the paths in the script.")
except Exception as e:
    traceback.print_exc()
