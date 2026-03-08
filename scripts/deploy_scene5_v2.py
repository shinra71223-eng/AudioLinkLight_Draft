# deploy_scene5_v2.py
# ================================================================
# SCENE_5: "Sonic Nebula" (Clean Build V2)
# ================================================================
# ・Internal Square Canvas (256x256) for stable feedback
# ・Forced 88x50 Fit Output
# ・Audio Reactive: Bass (Movement) + Hihat (Brightness)
# ================================================================

import os

ROOT_PATH = '/AudioLinkLight_V01'
SCENE_PATH = f'{ROOT_PATH}/SCENE_5'
AUDIO_PATH = f'{ROOT_PATH}/AudioLinkCore/out1'
RES_W = 88
RES_H = 50
INT_RES = 256 

def deploy():
    scene = op(SCENE_PATH)
    if not scene:
        print(f'[ERROR] {SCENE_PATH} not found')
        return

    print('='*60)
    print(f'[deploy_scene5] {SCENE_PATH} をクリーン・ビルド中...')
    print('='*60)

    # DELETE EXISTING NODES to ensure a fresh state
    nodes_to_clear = [
        'noise_base', 'comp_feedback', 'feedback1', 'transform1', 
        'level1', 'blur_glow', 'final_adjust', 'fit_to_led', 'scene_out'
    ]
    for name in nodes_to_clear:
        o = scene.op(name)
        if o: o.destroy()

    # 1. Base Noise (Source)
    noise = scene.create(noiseTOP, 'noise_base')
    noise.par.outputresolution = 1 # Custom
    noise.par.resolutionw = INT_RES
    noise.par.resolutionh = INT_RES
    noise.par.type = 'simplex3d'
    noise.par.mono = False
    noise.par.period = 4.0
    noise.par.offset = 0.2
    noise.par.tz.expr = 'absTime.seconds * 0.2'
    
    # Audio Reactivity for Noise (Movement/Density)
    bass_expr = f"op('{AUDIO_PATH}')['uBassEnergy'] if op('{AUDIO_PATH}') else 0"
    noise.par.amp.expr = f"0.1 + ({bass_expr}) * 0.3"
    
    # 2. Additive Feedback Loop
    comp = scene.create(compositeTOP, 'comp_feedback')
    fb = scene.create(feedbackTOP, 'feedback1')
    xf = scene.create(transformTOP, 'transform1')
    lvl = scene.create(levelTOP, 'level1')
    
    for n in [comp, fb, xf, lvl]:
        n.par.outputresolution = 1
        n.par.resolutionw = INT_RES
        n.par.resolutionh = INT_RES

    comp.par.operand = 'add'
    
    # --- Feedback Wiring ---
    fb.par.top = comp.name
    fb.inputConnectors[0].connect(noise) # Reset source
    
    xf.par.extend = 'zero' 
    xf.par.sx = 1.002
    xf.par.sy = 1.002
    xf.par.rz.expr = 'absTime.seconds * 1.5' 
    
    lvl.par.opacity = 0.82
    # Hihat Reactivity for Flash
    hihat_expr = f"op('{AUDIO_PATH}')['Hihat'] if op('{AUDIO_PATH}') else 0"
    lvl.par.brightness1.expr = f"0.8 + ({hihat_expr}) * 0.8" 
    
    # Loop Chain: fb -> xf -> lvl -> comp
    xf.inputConnectors[0].connect(fb)
    lvl.inputConnectors[0].connect(xf)

    # Composite: noise FRONT, lvl BACK
    comp.inputConnectors[0].connect(lvl)   # Input 0 (Back)
    comp.inputConnectors[1].connect(noise) # Input 1 (Front)
    
    # 3. Post-Process & Fit to 88x50
    blur = scene.create(blurTOP, 'blur_glow')
    blur.par.outputresolution = 0 # Use Input
    blur.par.size = 2
    blur.inputConnectors[0].connect(comp)
    
    final_lvl = scene.create(levelTOP, 'final_adjust')
    final_lvl.par.outputresolution = 0 # Use Input
    final_lvl.par.gamma1 = 1.2
    final_lvl.inputConnectors[0].connect(blur)
    
    fit = scene.create(fitTOP, 'fit_to_led')
    fit.par.outputresolution = 1 # Custom
    fit.par.resolutionw = RES_W
    fit.par.resolutionh = RES_H
    fit.par.fit = 'fitbest' # Keep ratio
    fit.inputConnectors[0].connect(final_lvl)
    
    out = scene.create(nullTOP, 'scene_out')
    out.inputConnectors[0].connect(fit)
    
    # Layout Nodes
    noise.nodeX,     noise.nodeY     = -800, 200
    comp.nodeX,      comp.nodeY      = -400, 200
    fb.nodeX,        fb.nodeY        = -600, -100
    xf.nodeX,        xf.nodeY        = -400, -100
    lvl.nodeX,       lvl.nodeY        = -200, -100
    blur.nodeX,      blur.nodeY      = 0, 200
    final_lvl.nodeX, final_lvl.nodeY = 200, 200
    fit.nodeX,       fit.nodeY       = 400, 200
    out.nodeX,       out.nodeY       = 600, 200

    print('[CLEAN SUCCESS] SCENE_5 を完全に再構築しました。')
    print(f'  - Loop Res: {INT_RES}x{INT_RES}')
    print(f'  - Out Res: {RES_W}x{RES_H}')
    print(f'  - Audio: Bass (Noise Amp), Hihat (Feedback Glow)')
    print('='*60)

if __name__ == '__main__':
    deploy()
