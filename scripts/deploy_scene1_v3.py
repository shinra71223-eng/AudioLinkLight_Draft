# deploy_scene1_v3.py
# ================================================================
# SCENE_1 を独立した Cyber Clock v3 (88x50) に再構築する
# ================================================================
# 【実行方法 (TD Textport)】
#   exec(open(project.folder + '/scripts/deploy_scene1_v3.py', encoding='utf-8').read())
#
# 【作成されるノード構成】
#   /AudioLinkLight_V01/SCENE_1/
#     ├── shader_code          (Text DAT — cyber_clock_v3.glsl)
#     ├── font_atlas           (Script TOP — 8x8 font atlas 2048x8)
#     ├── font_atlas_callbacks (Text DAT — font onCook script)
#     ├── sel_audio            (Select CHOP → AudioLinkCore/out1)
#     ├── glsl_clock           (GLSL TOP — 88x50, font_atlas as Input 0)
#     ├── clock_updater        (Execute DAT — 毎フレーム時刻更新)
#     └── scene_out            (Null TOP — output)
# ================================================================

import os

ROOT_PATH = '/AudioLinkLight_V01'
PROJECT_FOLDER = project.folder
LED_COLS = 88
LED_ROWS = 50  # 新しいキャンバスサイズ

def _create_or_get(parent, op_type, name):
    """既存ノードがあればそれを返し、なければ作成する"""
    existing = parent.op(name)
    if existing:
        return existing
    return parent.create(op_type, name)

def deploy():
    root = op(ROOT_PATH)
    if not root:
        print(f'[ERROR] {ROOT_PATH} が見つかりません')
        return

    scene = _create_or_get(root, baseCOMP, 'SCENE_1')
    print('='*60)
    print('[deploy_scene1_v3] SCENE_1 を Cyber Clock v3 (88x50) に再構築')
    print('='*60)

    # ---- 0. 古い不要ノードのクリーンアップ ----
    old_nodes = ['scene_source']  # 旧構成の残骸
    for name in old_nodes:
        old = scene.op(name)
        if old:
            old.destroy()
            print(f'  [CLEANUP] {name} を削除しました')

    # ---- 1. Shader Code (Text DAT) ----
    shader_dat = _create_or_get(scene, textDAT, 'shader_code')
    shader_path = PROJECT_FOLDER + '/scripts/cyber_clock_v3.glsl'
    try:
        with open(shader_path, 'r', encoding='utf-8') as f:
            shader_dat.text = f.read()
        print(f'  + shader_code (Text DAT) loaded from {shader_path}')
    except Exception as e:
        print(f'  [ERROR] Shader load failed: {e}')
        shader_dat.text = '// Shader Load Error'

    # ---- 2. Font Atlas (Script TOP — 2048x8, r8) ----
    font_top = _create_or_get(scene, scriptTOP, 'font_atlas')
    font_top.par.outputresolution = 'custom'
    font_top.par.resolutionw = 2048
    font_top.par.resolutionh = 8
    if hasattr(font_top.par, 'format'):
        font_top.par.format = 'r8'
    if hasattr(font_top.par, 'filtertype'):
        font_top.par.filtertype = 0  # Nearest
    if hasattr(font_top.par, 'inputfiltertype'):
        font_top.par.inputfiltertype = 0  # Nearest

    font_bin_path = (PROJECT_FOLDER + '/scripts/font_8x8.bin').replace('\\', '/')
    font_script = f"""import numpy as np
_f_cache = None
def onCook(scriptOp):
    global _f_cache
    if _f_cache is None:
        try:
            with open('{font_bin_path}', 'rb') as f:
                _f_cache = f.read()
        except Exception as e:
            print("Font Load Error: " + str(e))
            return

    if _f_cache:
        try:
            arr = np.frombuffer(_f_cache, dtype=np.uint8).reshape(8, 2048, 1)
            scriptOp.copyNumpyArray(np.ascontiguousarray(np.flipud(arr)))
        except Exception as e:
            print("Font cook Error: " + str(e))
"""
    # Set script code via callbacks DAT
    cb_dat = scene.op('font_atlas_callbacks')
    if not cb_dat:
        cb_dat = scene.create(textDAT, 'font_atlas_callbacks')
    cb_dat.text = font_script
    if hasattr(font_top.par, 'callbacks'):
        font_top.par.callbacks = cb_dat
    font_top.cook(force=True)
    print('  + font_atlas (Script TOP, 2048x8, Nearest)')

    # ---- 3. Select CHOP (AudioLinkCore audio) ----
    sel_audio = _create_or_get(scene, selectCHOP, 'sel_audio')
    sel_audio.par.chop = f'{ROOT_PATH}/AudioLinkCore/out1'
    print('  + sel_audio (Select CHOP → AudioLinkCore)')

    # ---- 4. GLSL TOP (88x50, cyber_clock_v3) ----
    glsl = _create_or_get(scene, glslTOP, 'glsl_clock')
    glsl.par.pixeldat = shader_dat
    glsl.par.outputresolution = 'custom'
    glsl.par.resolutionw = LED_COLS
    glsl.par.resolutionh = LED_ROWS
    if hasattr(glsl.par, 'filtertype'):
        glsl.par.filtertype = 0  # Nearest
    if hasattr(glsl.par, 'inputfiltertype'):
        glsl.par.inputfiltertype = 0  # Nearest

    # Connect font atlas as Input 0
    glsl.inputConnectors[0].connect(font_top)

    # ---- 5. Uniforms ----
    # Channel names from existing AudioLinkCore/out1 (confirmed in deploy_cyber_clock_v2.py)
    audio_path = f'{ROOT_PATH}/AudioLinkCore/out1'
    
    # Uniform 0: uTime
    glsl.par.uniname0 = 'uTime'
    glsl.par.value0x.expr = 'absTime.seconds'
    
    # Uniform 1: uHour   (set by Execute DAT, not expression)
    glsl.par.uniname1 = 'uHour'
    glsl.par.value1x = 0
    
    # Uniform 2: uMinute (set by Execute DAT)
    glsl.par.uniname2 = 'uMinute'
    glsl.par.value2x = 0
    
    # Uniform 3: uSecond (set by Execute DAT)
    glsl.par.uniname3 = 'uSecond'
    glsl.par.value3x = 0
    
    # Uniform 4: uVocal
    glsl.par.uniname4 = 'uVocal'
    glsl.par.value4x.expr = f"op('{audio_path}')['uVocalIntensity'] if op('{audio_path}') else 0"
    
    # Uniform 5: uOnset
    glsl.par.uniname5 = 'uOnset'
    glsl.par.value5x.expr = f"op('{audio_path}')['uVocalOnset'] if op('{audio_path}') else 0"
    
    # Uniform 6: uBass
    glsl.par.uniname6 = 'uBass'
    glsl.par.value6x.expr = f"op('{audio_path}')['uBassEnergy'] if op('{audio_path}') else 0"
    
    # Uniform 7: uHihat
    glsl.par.uniname7 = 'uHihat'
    glsl.par.value7x.expr = f"op('{audio_path}')['Hihat'] if op('{audio_path}') else 0"
    
    # Uniform 8: uClap
    glsl.par.uniname8 = 'uClap'
    glsl.par.value8x.expr = f"op('{audio_path}')['Clap'] if op('{audio_path}') else 0"
    
    # Uniform 9: uMelody
    glsl.par.uniname9 = 'uMelody'
    glsl.par.value9x.expr = f"op('{audio_path}')['uMelodyIntensity'] if op('{audio_path}') else 0"

    # Uniform 10: uMonth (set by Execute DAT)
    glsl.par.uniname10 = 'uMonth'
    glsl.par.value10x = 1

    # Uniform 11: uDay (set by Execute DAT)
    glsl.par.uniname11 = 'uDay'
    glsl.par.value11x = 1

    print('  + glsl_clock (GLSL TOP, 88x50, 12 uniforms)')
    glsl.cook(force=True)  # Force recompile with updated shader

    # ---- 5b. Execute DAT (毎フレーム時刻更新) ----
    exec_dat = _create_or_get(scene, executeDAT, 'clock_updater')
    exec_dat.par.framestart = True
    exec_dat.text = """import datetime
def onFrameStart(frame):
    now = datetime.datetime.now()
    glsl = op('glsl_clock')
    if glsl:
        glsl.par.value1x = now.hour
        glsl.par.value2x = now.minute
        glsl.par.value3x = now.second
        glsl.par.value10x = now.month
        glsl.par.value11x = now.day
"""
    print('  + clock_updater (Execute DAT, frameStart=True)')

    # ---- 6. Pat Rain v2 (Data Stream, separate GLSL TOP) ----
    rain_shader_dat = _create_or_get(scene, textDAT, 'rain_shader_code')
    rain_shader_path = PROJECT_FOLDER + '/scripts/rain_shader_v2.glsl'
    try:
        with open(rain_shader_path, 'r', encoding='utf-8') as f:
            rain_shader_dat.text = f.read()
        print(f'  + rain_shader_code (Text DAT) loaded')
    except Exception as e:
        print(f'  [ERROR] Rain shader load failed: {e}')
        rain_shader_dat.text = '// Rain Shader Load Error'

    pat_rain = _create_or_get(scene, glslTOP, 'pat_rain_v2')
    pat_rain.par.pixeldat = rain_shader_dat
    pat_rain.par.outputresolution = 'custom'
    pat_rain.par.resolutionw = LED_COLS
    pat_rain.par.resolutionh = LED_ROWS
    if hasattr(pat_rain.par, 'filtertype'):
        pat_rain.par.filtertype = 0  # Nearest

    # uTime uniform for rain
    pat_rain.par.uniname0 = 'uTime'
    pat_rain.par.value0x.expr = 'absTime.seconds'

    pat_rain.cook(force=True)
    print(f'  + pat_rain_v2 (GLSL TOP, {LED_COLS}x{LED_ROWS})')

    # ---- 7. Composite (Rain背景 + Clock前景) ----
    comp = _create_or_get(scene, compositeTOP, 'comp_final')
    if hasattr(comp.par, 'operand'):
        comp.par.operand = 'add'  # Additive blending
    comp.inputConnectors[0].connect(pat_rain)   # Input 0: Rain (背景)
    comp.inputConnectors[1].connect(glsl)       # Input 1: Clock (前景)
    print('  + comp_final (Composite TOP: rain + clock)')

    # ---- 8. scene_out (Null TOP) ----
    out = _create_or_get(scene, nullTOP, 'scene_out')
    out.inputConnectors[0].connect(comp)  # Connect to composite, not glsl directly
    print('  + scene_out (Null TOP)')

    # ---- 完了 ----
    print()
    print('='*60)
    print('[deploy_scene1_v3] SCENE_1 構築完了！')
    print(f'  Canvas: {LED_COLS}x{LED_ROWS}')
    print(f'  Font: 8x8 Pro Font (font_8x8.bin)')
    print(f'  Layout: 2 Rows (X=0)')
    print(f'    Row 21: HH:MM (Clock)')
    print(f'    Row 31: MM/DD (Date)')
    print(f'    Rain: pat_rain_v2 (Additive)')
    print('='*60)

deploy()
