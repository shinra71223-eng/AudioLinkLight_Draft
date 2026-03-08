# deploy_scene5_v7.py
# ================================================================
# SCENE_5: "Native Flow Nebula" (V7 - Ultimate Stability & Contrast)
# ================================================================
# ・Native 88x50
# ・Source Leveling: Extracts "sparks" safely without Threshold TOP
# ・Maximum Composite: Prevents flattening and white-outs
# ================================================================

import os

ROOT_PATH = '/AudioLinkLight_V01'
SCENE_PATH = f'{ROOT_PATH}/SCENE_5'
AUDIO_PATH = f'{ROOT_PATH}/AudioLinkCore/out1'
RES_W = 88
RES_H = 50

def deploy():
    scene = op(SCENE_PATH)
    if not scene:
        print(f'[ERROR] {SCENE_PATH} not found')
        return

    print('='*60)
    print(f'[deploy_scene5] {SCENE_PATH} V7: "Native Flow" 構築中...')
    print('='*60)

    # 1. CLEAN UP
    for o in list(scene.children):
        try:
            o.destroy()
        except:
            pass

    # 2. SOURCE NOISE & LEVEL (Safe Spark Extraction)
    noise = scene.create(noiseTOP, 'noise_base')
    noise.par.outputresolution = 1
    noise.par.resolutionw = RES_W
    noise.par.resolutionh = RES_H
    noise.par.type = 'simplex3d'
    noise.par.period = 1.8
    bass_val = f"(op('{AUDIO_PATH}')['uBassEnergy'] if op('{AUDIO_PATH}') else 0)"
    noise.par.period.expr = f"2.2 - ({bass_val} * 1.2)"
    noise.par.tz.expr = 'absTime.seconds * 0.25'
    noise.par.mono = True
    
    # LEVEL: Acts like a safe Threshold to prevent "flatness"
    src_lvl = scene.create(levelTOP, 'src_level')
    src_lvl.par.outputresolution = 1
    src_lvl.par.resolutionw = RES_W
    src_lvl.par.resolutionh = RES_H
    src_lvl.par.blacklevel = 0.5   # Crushes gray into black
    src_lvl.par.brightness1 = 1.5  # Boosts remaining whites
    src_lvl.inputConnectors[0].connect(noise)
    
    # 3. FEEDBACK LOOP
    comp = scene.create(compositeTOP, 'comp_feedback')
    fb = scene.create(feedbackTOP, 'feedback1')
    xf = scene.create(transformTOP, 'transform1')
    disp = scene.create(displaceTOP, 'displace1')
    disp_noise = scene.create(noiseTOP, 'disp_noise')
    lvl = scene.create(levelTOP, 'level1')
    
    for n in [comp, fb, xf, disp, disp_noise, lvl]:
        n.par.outputresolution = 1
        n.par.resolutionw = RES_W
        n.par.resolutionh = RES_H

    fb.par.top = comp.name
    fb.inputConnectors[0].connect(src_lvl)

    # Movement
    xf.par.sx = 1.01
    xf.par.sy = 1.01

    # Displace Fluid
    disp_noise.par.type = 'perlin3d'
    disp_noise.par.mono = False
    disp_noise.par.tz.expr = 'absTime.seconds * 0.5'
    disp.par.displaceweightx.expr = f"0.01 + {bass_val} * 0.05"
    disp.par.displaceweighty.expr = disp.par.displaceweightx
    
    # Decay
    lvl.par.opacity = 0.82
    hihat_val = f"(op('{AUDIO_PATH}')['Hihat'] if op('{AUDIO_PATH}') else 0)"
    lvl.par.brightness1.expr = f"0.8 + {hihat_val} * 1.2"
    
    # WIRING
    xf.inputConnectors[0].connect(fb)
    disp.inputConnectors[0].connect(xf)
    disp.inputConnectors[1].connect(disp_noise)
    lvl.inputConnectors[0].connect(disp)
    
    # Composit: Maximum mode prevents additive white-outs (Flatness killer)
    try:
        comp.par.operand = 'maximum'
    except:
        comp.par.operand = 14

    comp.inputConnectors[0].connect(lvl)
    comp.inputConnectors[1].connect(src_lvl)
    
    # 4. COLOR & POST PUNCH
    lookup = scene.create(lookupTOP, 'color_look')
    ramp = scene.create(rampTOP, 'color_ramp')
    ramp_dat = scene.create(tableDAT, 'ramp_data')
    
    ramp_dat.clear()
    ramp_dat.appendRow(['pos', 'r', 'g', 'b', 'a'])
    ramp_dat.appendRow([0.0, 0.0, 0.0, 0.0, 1.0])   # Black Void
    ramp_dat.appendRow([0.2, 0.0, 0.1, 0.4, 1.0])   # Deep Blue
    ramp_dat.appendRow([0.6, 0.0, 0.7, 0.9, 1.0])   # Electric Cyan
    ramp_dat.appendRow([0.9, 0.8, 0.2, 1.0, 1.0])   # Hot Purple/White
    
    ramp.par.dat = ramp_dat.name
    ramp.par.outputresolution = 1
    ramp.par.resolutionw = 256
    ramp.par.resolutionh = 1
    lookup.par.outputresolution = 1
    lookup.par.resolutionw = RES_W
    lookup.par.resolutionh = RES_H
    
    lookup.inputConnectors[0].connect(comp)
    lookup.inputConnectors[1].connect(ramp)
    
    final_punch = scene.create(levelTOP, 'final_punch')
    final_punch.par.outputresolution = 0
    final_punch.par.contrast = 1.2
    final_punch.par.gamma1 = 0.9
    final_punch.inputConnectors[0].connect(lookup)

    out = scene.create(nullTOP, 'scene_out')
    out.inputConnectors[0].connect(final_punch)
    
    # Easy Layout
    try:
        noise.nodeX, noise.nodeY = -1400, 200
        src_lvl.nodeX, src_lvl.nodeY = -1200, 200
        fb.nodeX, fb.nodeY = -1200, -200
        xf.nodeX, xf.nodeY = -1000, -200
        disp_noise.nodeX, disp_noise.nodeY = -1000, -400
        disp.nodeX, disp.nodeY = -800, -200
        lvl.nodeX, lvl.nodeY = -600, -200
        comp.nodeX, comp.nodeY = -600, 200
        ramp_dat.nodeX, ramp_dat.nodeY = -400, 450
        ramp.nodeX, ramp.nodeY = -400, 300
        lookup.nodeX, lookup.nodeY = -400, 200
        final_punch.nodeX, final_punch.nodeY = -200, 200
        out.nodeX, out.nodeY = 0, 200
    except:
        pass

    print('[V7 SUCCESS] SCENE_5: Native Flow Nebula 完成！')
    print('  - Error-Proof: Removed unstable Threshold TOP.')
    print('  - Contrast: Used "Maximum" blend and Source Leveling.')
    print('  - Result: Sharp, dynamic sparks that never flatten out.')
    print('='*60)

if __name__ == '__main__':
    deploy()
