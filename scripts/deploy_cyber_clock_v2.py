# deploy_cyber_clock_v2.py
# TEST_SCREEN2 を新規作成し、88x10ネイティブ解像度のサイバーパンク時計を配置
import datetime

def deploy_v2():
    try:
        root = op('/AudioLinkLight_V01')
        if not root:
            print("Error: /AudioLinkLight_V01 not found.")
            return

        # ---- TEST_SCREEN2 コンテナの作成 ----
        screen2 = root.op('TEST_SCREEN2')
        if not screen2:
            screen2 = root.create(baseCOMP, 'TEST_SCREEN2')
            screen2.nodeX = 800
            screen2.nodeY = -600
            print(f"Created container: {screen2.path}")
        else:
            print(f"Using existing container: {screen2.path}")

        # ---- 既存ノードのクリーンアップ ----
        for name in ['cyber_clock_v2', 'cyber_clock_v2_pixel', 'clock_updater_v2',
                      'led_preview', 'led_preview_bg']:
            old = screen2.op(name)
            if old:
                old.destroy()

        # ---- GLSL TOP (88x10 ネイティブ) ----
        glsl = screen2.create(glslTOP, 'cyber_clock_v2')
        glsl.nodeX = 0
        glsl.nodeY = 0

        # Pixel Shader DAT
        shader_dat = screen2.create(textDAT, 'cyber_clock_v2_pixel')
        shader_dat.nodeX = 0
        shader_dat.nodeY = -200
        with open(project.folder + '/scripts/cyber_clock_v2.glsl', 'r', encoding='utf-8') as f:
            shader_dat.text = f.read()
        glsl.par.pixeldat = shader_dat

        # 解像度: 88x10 ネイティブ
        glsl.par.outputresolution = 'custom'
        glsl.par.resolutionw = 88
        glsl.par.resolutionh = 10
        glsl.par.filtertype = 'nearest'

        # ---- Uniform 設定 ----
        glsl.par.uniname0 = 'uTime'
        glsl.par.value0x.expr = "absTime.seconds"

        glsl.par.uniname1 = 'uClap'
        glsl.par.value1x.expr = "op('/AudioLinkLight_V01/AudioLinkCore/out1')['Clap'] if op('/AudioLinkLight_V01/AudioLinkCore/out1') else 0.0"

        glsl.par.uniname2 = 'uVocal'
        glsl.par.value2x.expr = "op('/AudioLinkLight_V01/AudioLinkCore/out1')['uVocalIntensity'] if op('/AudioLinkLight_V01/AudioLinkCore/out1') else 0.0"

        glsl.par.uniname3 = 'uBass'
        glsl.par.value3x.expr = "op('/AudioLinkLight_V01/AudioLinkCore/out1')['uBassEnergy'] if op('/AudioLinkLight_V01/AudioLinkCore/out1') else 0.0"

        glsl.par.uniname4 = 'uHihat'
        glsl.par.value4x.expr = "op('/AudioLinkLight_V01/AudioLinkCore/out1')['Hihat'] if op('/AudioLinkLight_V01/AudioLinkCore/out1') else 0.0"

        # 時計 Uniform
        glsl.par.uniname5 = 'uHour'
        glsl.par.uniname6 = 'uMinute'
        glsl.par.uniname7 = 'uSecond'

        # Sustain (uVocalSustain)
        glsl.par.uniname8 = 'uSustain'
        glsl.par.value8x.expr = "op('/AudioLinkLight_V01/AudioLinkCore/out1')['uVocalSustain'] if op('/AudioLinkLight_V01/AudioLinkCore/out1') else 0.0"

        # Melody (uMelodyIntensity)
        glsl.par.uniname9 = 'uMelody'
        glsl.par.value9x.expr = "op('/AudioLinkLight_V01/AudioLinkCore/out1')['uMelodyIntensity'] if op('/AudioLinkLight_V01/AudioLinkCore/out1') else 0.0"

        # Vibrato (uVocalVibrato)
        glsl.par.uniname10 = 'uVibrato'
        glsl.par.value10x.expr = "op('/AudioLinkLight_V01/AudioLinkCore/out1')['uVocalVibrato'] if op('/AudioLinkLight_V01/AudioLinkCore/out1') else 0.0"

        # Kick
        glsl.par.uniname11 = 'uKick'
        glsl.par.value11x.expr = "op('/AudioLinkLight_V01/AudioLinkCore/out1')['Kick'] if op('/AudioLinkLight_V01/AudioLinkCore/out1') else 0.0"

        # Snare
        glsl.par.uniname12 = 'uSnare'
        glsl.par.value12x.expr = "op('/AudioLinkLight_V01/AudioLinkCore/out1')['Snare'] if op('/AudioLinkLight_V01/AudioLinkCore/out1') else 0.0"

        # VocalOnset
        glsl.par.uniname13 = 'uOnset'
        glsl.par.value13x.expr = "op('/AudioLinkLight_V01/AudioLinkCore/out1')['uVocalOnset'] if op('/AudioLinkLight_V01/AudioLinkCore/out1') else 0.0"

        # ---- Execute DAT (毎フレーム時刻セット) ----
        exec_dat = screen2.create(executeDAT, 'clock_updater_v2')
        exec_dat.nodeX = 200
        exec_dat.nodeY = -200
        exec_dat.par.framestart = True
        exec_dat.text = """import datetime
def onFrameStart(frame):
    now = datetime.datetime.now()
    glsl = op('cyber_clock_v2')
    if glsl:
        glsl.par.value5x = now.hour
        glsl.par.value6x = now.minute
        glsl.par.value7x = now.second
"""

        # ---- プレビュー用 LED シミュレーション (モニター確認用) ----
        # 88x10 を 880x100 に拡大 (Nearest) → Bloom を重ねて光の拡散を再現
        preview = screen2.create(resolutionTOP, 'led_preview')
        preview.nodeX = 400
        preview.nodeY = 0
        preview.par.outputresolution = 'custom'
        preview.par.resolutionw = 880
        preview.par.resolutionh = 100
        preview.par.filtertype = 'nearest'   # ドットのまま拡大
        preview.inputConnectors[0].connect(glsl)

        print("=" * 50)
        print(f"Cyberpunk LED Clock v2 deployed to: {screen2.path}")
        print(f"  GLSL TOP (88x10): {glsl.path}")
        print(f"  Preview (880x100): {preview.path}")
        print(f"  Resolution: {glsl.par.resolutionw.val} x {glsl.par.resolutionh.val}")
        print("=" * 50)

    except Exception as e:
        import traceback
        print(f"Deploy error: {e}")
        traceback.print_exc()

deploy_v2()
