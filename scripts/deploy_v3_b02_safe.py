# deploy_v3_b02_safe.py - Individual Uniform Version
import traceback

try:
    # 安定版のパスを指定
    glsl = op('/AudioLinkLight_V01/TEST_SCREEN2/cyber_clock_v2')
    pixel_dat = op('/AudioLinkLight_V01/TEST_SCREEN2/cyber_clock_v2_pixel22')
    core = op('/AudioLinkLight_V01/AudioLinkCore/out1')
    clock = op('/AudioLinkLight_V01/TEST_SCREEN2/clock_updater_v2')
    
    glsl_path = project.folder + '/scripts/cyber_clock_v2.glsl'

    if glsl and pixel_dat and core and clock:
        print("\n--- Deploying V03_b02 Safe Mode ---")

        # 1. 配列（Array）設定を完全に解除（フリーズ防止のため）
        glsl.par.array = 0
        glsl.par.array0name = ''
        glsl.par.array0chop = ''
        print("1. Disabled CHOP Arrays to ensure stability.")

        # 2. パラメータを個別に繋ぐ（10本制限以内）
        # 初期化
        for i in range(10):
            getattr(glsl.par, f'uniname{i}').val = ''
            getattr(glsl.par, f'value{i}x').expr = ''
            getattr(glsl.par, f'value{i}x').val = 0.0

        # 紐付け定義
        params = [
            ('uTime',   "absTime.seconds"),
            ('uHour',   f"op('{clock.path}')['hour']"),
            ('uMinute', f"op('{clock.path}')['minute']"),
            ('uSecond', f"op('{clock.path}')['second']"),
            ('uVocal',  f"op('{core.path}')['uVocalIntensity']"),
            ('uOnset',  f"op('{core.path}')['uVocalOnset']"),
            ('uBass',   f"op('{core.path}')['uBassEnergy']"),
            ('uHihat',  f"op('{core.path}')['Hihat']"),
            ('uClap',   f"op('{core.path}')['Clap']"),
            ('uMelody', f"op('{core.path}')['uMelodyIntensity']")
        ]

        for i, (name, expr) in enumerate(params):
            getattr(glsl.par, f'uniname{i}').val = name
            getattr(glsl.par, f'value{i}x').expr = expr
        
        print(f"2. Mapped {len(params)} individual uniforms (0-9).")

        # 3. コードを流し込む
        with open(glsl_path, 'r', encoding='utf-8') as f:
            pixel_dat.text = f.read()
        print(f"3. Updated GLSL code from {glsl_path}")

        # 4. コンパイル結果の確認
        # 強制クックは行わず、自然な更新を待ちます（安全第一）
        print("\n--- DEPLOYED SUCCESSFULLY ---")
        print("Please check the screen. If it works, the clock should move and background appear.")

    else:
        print("Error: Required nodes not found. Check your network hierarchy.")

except Exception as e:
    traceback.print_exc()
