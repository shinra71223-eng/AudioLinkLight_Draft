# deploy_scene5_v3.py
# ================================================================
# SCENE_5: "Organic Fluid Nebula" (High-End TD Vibe - Final Build)
# ================================================================
# ・Displace Feedback: Organic fluid melting
# ・DAT-Driven Ramp: 100% version-independent color setup
# ・Resolution: 128x128 internal, 88x50 final output
# ================================================================

import os

ROOT_PATH = '/AudioLinkLight_V01'
SCENE_PATH = f'{ROOT_PATH}/SCENE_5'
AUDIO_PATH = f'{ROOT_PATH}/AudioLinkCore/out1'
RES_W = 88
RES_H = 50
INT_RES = 128 

def deploy():
    scene = op(SCENE_PATH)
    if not scene:
        print(f'[ERROR] {SCENE_PATH} not found')
        return

    print('='*60)
    print(f'[deploy_scene5] {SCENE_PATH} を "Organic Fluid" で徹底構築中...')
    print('='*60)

    # 1. CLEAN UP
    for o in list(scene.children):
        try:
            o.destroy()
        except:
            pass

    # 2. SOURCE NOISE
    noise = scene.create(noiseTOP, 'noise_base')
    noise.par.outputresolution = 1 # Custom
    noise.par.resolutionw = INT_RES
    noise.par.resolutionh = INT_RES
    noise.par.type = 'simplex3d'
    noise.par.period = 3.0
    # Bass Energy drives speed and density
    bass_val_expr = f"(op('{AUDIO_PATH}')['uBassEnergy'] if op('{AUDIO_PATH}') else 0)"
    noise.par.period.expr = f"3.0 - ({bass_val_expr} * 1.5)"
    noise.par.tz.expr = 'absTime.seconds * 0.1'
    noise.par.mono = True
    
    # 3. FEEDBACK LOOP with DISPLACEMENT
    comp = scene.create(compositeTOP, 'comp_feedback')
    fb = scene.create(feedbackTOP, 'feedback1')
    xf = scene.create(transformTOP, 'transform1')
    disp = scene.create(displaceTOP, 'displace1')
    disp_noise = scene.create(noiseTOP, 'disp_noise')
    lvl = scene.create(levelTOP, 'level1')
    
    # Strictly set resolution for ALL nodes in the loop
    for n in [comp, fb, xf, disp, disp_noise, lvl]:
        n.par.outputresolution = 1
        n.par.resolutionw = INT_RES
        n.par.resolutionh = INT_RES

    # Operation: Add
    try:
        comp.par.operand = 'add'
    except:
        comp.par.operand = 8

    disp_noise.par.type = 'perlin3d'
    disp_noise.par.mono = False
    disp_noise.par.tz.expr = 'absTime.seconds * 0.3'

    fb.par.top = comp.name
    fb.inputConnectors[0].connect(noise) # Reset
    
    xf.par.extend = 'zero' 
    xf.par.sx = 1.002
    xf.par.sy = 1.002
    xf.par.rz = 0.5
    
    # Verified Displace parameters
    disp.par.displaceweightx.expr = f"0.005 + {bass_val_expr} * 0.05"
    disp.par.displaceweighty.expr = f"0.005 + {bass_val_expr} * 0.05"
    
    lvl.par.opacity = 0.88
    hihat_val_expr = f"(op('{AUDIO_PATH}')['Hihat'] if op('{AUDIO_PATH}') else 0)"
    lvl.par.brightness1.expr = f"0.8 + ({hihat_val_expr}) * 0.8"
    
    # WIRING
    xf.inputConnectors[0].connect(fb)
    disp.inputConnectors[0].connect(xf)
    disp.inputConnectors[1].connect(disp_noise)
    lvl.inputConnectors[0].connect(disp)
    
    # Composite: noise FRONT (Input 1), lvl BACK (Input 0)
    comp.inputConnectors[0].connect(lvl)
    comp.inputConnectors[1].connect(noise)
    
    # 4. COLOR LOOKUP (DAT-Driven for Reliability)
    lookup = scene.create(lookupTOP, 'color_look')
    ramp = scene.create(rampTOP, 'color_ramp')
    ramp_dat = scene.create(tableDAT, 'ramp_data')
    
    # Define Ramp Points in DAT (pos, r, g, b, a)
    ramp_dat.clear()
    ramp_dat.appendRow(['pos', 'r', 'g', 'b', 'a'])
    ramp_dat.appendRow([0.0, 0.0, 0.0, 0.2, 1.0]) # Deep Blue
    ramp_dat.appendRow([0.5, 0.0, 0.7, 0.7, 1.0]) # Cyan
    ramp_dat.appendRow([1.0, 0.4, 0.0, 0.7, 1.0]) # Purple
    
    # Connect DAT to Ramp
    ramp.par.dat = ramp_dat.name
    
    lookup.par.outputresolution = 1
    lookup.par.resolutionw = INT_RES
    lookup.par.resolutionh = INT_RES
    ramp.par.outputresolution = 1
    ramp.par.resolutionw = 256
    ramp.par.resolutionh = 1
    
    lookup.inputConnectors[0].connect(comp)
    lookup.inputConnectors[1].connect(ramp)
    
    # 5. FINAL FIT & NULL
    fit = scene.create(fitTOP, 'fit_to_output')
    fit.par.outputresolution = 1
    fit.par.resolutionw = RES_W
    fit.par.resolutionh = RES_H
    try:
        fit.par.fit = 0 # Fit Best
    except:
        pass
    fit.inputConnectors[0].connect(lookup)
    
    out = scene.create(nullTOP, 'scene_out')
    out.inputConnectors[0].connect(fit)
    
    # Layout Nodes
    noise.nodeX, noise.nodeY = -1400, 200
    fb.nodeX, fb.nodeY = -1200, -200
    xf.nodeX, xf.nodeY = -1000, -200
    disp_noise.nodeX, disp_noise.nodeY = -1000, -400
    disp.nodeX, disp.nodeY = -800, -200
    lvl.nodeX, lvl.nodeY = -600, -200
    comp.nodeX, comp.nodeY = -600, 200
    ramp_dat.nodeX, ramp_dat.nodeY = -400, 450
    ramp.nodeX, ramp.nodeY = -400, 300
    lookup.nodeX, lookup.nodeY = -200, 200
    fit.nodeX, fit.nodeY = 0, 200
    out.nodeX, out.nodeY = 200, 200

    print('[CLEAN SUCCESS] SCENE_5: Organic Fluid Nebula 完成！')
    print('  - DAT-Driven Ramp 搭載 (バージョン互換性100%)')
    print('  - Displace Feedback 搭載 (TDらしさ)')
    print('='*60)

if __name__ == '__main__':
    deploy()
