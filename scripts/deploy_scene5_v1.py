# deploy_scene5_v1.py
# ================================================================
# SCENE_5: "Sonic Nebula" (Fixed Aspect & Audio Reactivity)
# ================================================================
# ・Internal Square Canvas (256x256) to prevent skewing/parallelogram
# ・Output Cropped to 88x50
# ・Bass & Hihat reactive
# ================================================================

import os

ROOT_PATH = '/AudioLinkLight_V01'
SCENE_PATH = f'{ROOT_PATH}/SCENE_5'
AUDIO_PATH = f'{ROOT_PATH}/AudioLinkCore/out1'
RES_W = 88
RES_H = 50
INT_RES = 256 # Higher square res for stable feedback rotation

def _create_or_get(parent, op_type, name):
    existing = parent.op(name)
    if existing: return existing
    return parent.create(op_type, name)

def deploy():
    scene = op(SCENE_PATH)
    if not scene:
        print(f'[ERROR] {SCENE_PATH} not found')
        return

    print('='*60)
    print(f'[deploy_scene5] {SCENE_PATH} を再構築 (アスペクト比修正版)')
    print('='*60)

    # 1. Base Noise (Source) - Use Square Res
    noise = _create_or_get(scene, noiseTOP, 'noise_base')
    noise.par.outputresolution = 1 # Custom
    noise.par.resolutionw = INT_RES
    noise.par.resolutionh = INT_RES
    noise.par.type = 'simplex3d'
    noise.par.mono = False
    noise.par.period = 4.0
    noise.par.offset = 0.3
    noise.par.tz.expr = 'absTime.seconds * 0.2'
    
    # Audio Reactivity for Noise
    bass_expr = f"op('{AUDIO_PATH}')['uBassEnergy'] if op('{AUDIO_PATH}') else 0"
    noise.par.amp.expr = f"0.1 + ({bass_expr}) * 0.4"
    
    # 2. Additive Feedback Loop - Use Square Res
    comp = _create_or_get(scene, compositeTOP, 'comp_feedback')
    fb = _create_or_get(scene, feedbackTOP, 'feedback1')
    xf = _create_or_get(scene, transformTOP, 'transform1')
    lvl = _create_or_get(scene, levelTOP, 'level1')
    
    for n in [comp, fb, xf, lvl]:
        n.par.outputresolution = 1 # Custom
        n.par.resolutionw = INT_RES
        n.par.resolutionh = INT_RES

    # Operation: Add (index 8)
    try:
        comp.par.operand = 'add'
    except:
        comp.par.operand = 8

    # Clear existing connections
    for n in [comp, fb, xf, lvl]:
        for c in n.inputConnectors:
            c.disconnect()
    
    # --- Feedback Setup ---
    # Concept: comp = noise + lvl
    fb.par.top = comp.name
    fb.inputConnectors[0].connect(noise) # Reset source
    
    xf.par.extend = 'zero' 
    xf.par.sx = 1.002 # Subtle zoom
    xf.par.sy = 1.002
    xf.par.rz.expr = 'absTime.seconds * 2.0' # Slightly faster rotation
    
    lvl.par.opacity = 0.8
    hihat_expr = f"op('{AUDIO_PATH}')['Hihat'] if op('{AUDIO_PATH}') else 0"
    lvl.par.brightness1.expr = f"0.9 + ({hihat_expr}) * 0.8" # Flash on Hihat
    
    # Internal Loop Path: fb -> xf -> lvl
    xf.inputConnectors[0].connect(fb)
    lvl.inputConnectors[0].connect(xf)

    # Composite Wiring
    # Input 0: Feedback Path (BACK)
    comp.inputConnectors[0].connect(lvl)
    # Input 1: Noise Source (FRONT)
    comp.inputConnectors[1].connect(noise)
    
    # 3. Final Look & Crop to 88x50
    blur = _create_or_get(scene, blurTOP, 'blur_glow')
    for c in blur.inputConnectors: c.disconnect()
    blur.par.outputresolution = 0 # Use Input (256x256)
    blur.par.size = 3
    blur.inputConnectors[0].connect(comp)
    
    final_adjust = _create_or_get(scene, levelTOP, 'final_adjust')
    for c in final_adjust.inputConnectors: c.disconnect()
    final_adjust.par.outputresolution = 0 # Use Input
    final_adjust.par.gamma1 = 1.3
    final_adjust.inputConnectors[0].connect(blur)

    # FINAL CROP / RESIZE to 88x50
    out = _create_or_get(scene, nullTOP, 'scene_out')
    for c in out.inputConnectors: c.disconnect()
    out.par.outputresolution = 1 # Custom
    out.par.resolutionw = RES_W
    out.par.resolutionh = RES_H
    # Use "Fit Outside" or "Fit Best" logic? 
    # NULL doesn't have FIT, so let's use a FIT TOP if needed, 
    # but Null will just crop from top-left by default.
    # Better: Use a Reorder or Scale TOP to center it.
    
    fit = _create_or_get(scene, fitTOP, 'fit_to_led')
    for c in fit.inputConnectors: c.disconnect()
    fit.par.outputresolution = 1
    fit.par.resolutionw = RES_W
    fit.par.resolutionh = RES_H
    fit.par.fit = 'fitbest' # Keep aspect, fill the rest
    fit.inputConnectors[0].connect(final_adjust)
    
    out.inputConnectors[0].connect(fit)
    
    # Layout adjustment
    noise.nodeX,     noise.nodeY     = -800, 200
    comp.nodeX,      comp.nodeY      = -400, 200
    fb.nodeX,        fb.nodeY        = -600, -100
    xf.nodeX,        xf.nodeY        = -400, -100
    lvl.nodeX,       lvl.nodeY        = -200, -100
    blur.nodeX,      blur.nodeY      = -200, 200
    final_adjust.nodeX, final_adjust.nodeY = 0, 200
    fit.nodeX,       fit.nodeY       = 200, 200
    out.nodeX,       out.nodeY       = 400, 200

    print('[SUCCESS] SCENE_5 アスペクト比修正完了！')
    print(f'  - Feedback Loop: {INT_RES}x{INT_RES} (Square)')
    print(f'  - LED Output: {RES_W}x{RES_H}')
    print(f'  - Fix: Parallel skewing resolved by square internal buffer.')
    print('='*60)

if __name__ == '__main__':
    deploy()
