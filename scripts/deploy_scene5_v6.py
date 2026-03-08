# deploy_scene5_v6.py
# ================================================================
# SCENE_5: "Edge Spark Nebula" (V6 - Contrast & Sharpness)
# ================================================================
# ・Native 88x50 Resolution
# ・Edge-Only Feedback: Preserves contrast by only trailing peaks
# ・High-Contrast Post-Processing
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
    print(f'[deploy_scene5] {SCENE_PATH} V6: "Edge Spark" 構築中...')
    print('='*60)

    # 1. CLEAN UP
    for o in list(scene.children):
        try:
            o.destroy()
        except:
            pass

    # 2. SOURCE NOISE (Crisp & Dark)
    noise = scene.create(noiseTOP, 'noise_base')
    noise.par.outputresolution = 1
    noise.par.resolutionw = RES_W
    noise.par.resolutionh = RES_H
    noise.par.type = 'simplex3d'
    noise.par.period = 1.8
    bass_val = f"(op('{AUDIO_PATH}')['uBassEnergy'] if op('{AUDIO_PATH}') else 0)"
    noise.par.period.expr = f"2.2 - ({bass_val} * 1.2)"
    noise.par.tz.expr = 'absTime.seconds * 0.25'
    noise.par.offset = 0.2 # Lower offset for more black space
    noise.par.mono = True
    
    # 3. EDGE FEEDBACK LOOP (Trails only the bright bits)
    comp = scene.create(compositeTOP, 'comp_feedback')
    fb = scene.create(feedbackTOP, 'feedback1')
    
    # NEW: Slope + Threshold to keep it sharp
    slope = scene.create(slopeTOP, 'edge_finder')
    thresh = scene.create(thresholdTOP, 'peak_filter')
    
    xf = scene.create(transformTOP, 'transform1')
    disp = scene.create(displaceTOP, 'displace1')
    disp_noise = scene.create(noiseTOP, 'disp_noise')
    lvl = scene.create(levelTOP, 'level1')
    
    for n in [comp, fb, slope, thresh, xf, disp, disp_noise, lvl]:
        n.par.outputresolution = 1
        n.par.resolutionw = RES_W
        n.par.resolutionh = RES_H

    fb.par.top = comp.name
    fb.inputConnectors[0].connect(noise)
    
    # Slope makes it react to motion/boundaries
    slope.inputConnectors[0].connect(fb)
    
    # Threshold chops off the grays, keeping only the "Sparks"
    thresh.inputConnectors[0].connect(slope)
    thresh.par.threshold = 0.5
    thresh.par.softness = 0.2
    
    # Movement
    xf.par.sx = 1.01
    xf.par.sy = 1.01
    xf.inputConnectors[0].connect(thresh)
    
    # Subtle Displacement
    disp_noise.par.type = 'perlin3d'
    disp_noise.par.tz.expr = 'absTime.seconds * 0.5'
    disp.par.displaceweightx.expr = f"0.01 + {bass_val} * 0.05"
    disp.par.displaceweighty.expr = disp.par.displaceweightx
    disp.inputConnectors[0].connect(xf)
    disp.inputConnectors[1].connect(disp_noise)
    
    # Fast Decay to keep it from flattening
    lvl.par.opacity = 0.75 # Faster decay
    hihat_val = f"(op('{AUDIO_PATH}')['Hihat'] if op('{AUDIO_PATH}') else 0)"
    lvl.par.brightness1.expr = f"0.8 + {hihat_val} * 1.2" # Sharp spikes
    lvl.inputConnectors[0].connect(disp)
    
    # Composite: noise FRONT, lvl BACK
    # Using 'Add' is fine here because 'lvl' is mostly black gaps now
    comp.par.operand = 'add'
    comp.inputConnectors[0].connect(lvl)
    comp.inputConnectors[1].connect(noise)
    
    # 4. COLOR & CONTRAST
    lookup = scene.create(lookupTOP, 'color_look')
    ramp = scene.create(rampTOP, 'color_ramp')
    ramp_dat = scene.create(tableDAT, 'ramp_data')
    
    ramp_dat.clear()
    ramp_dat.appendRow(['pos', 'r', 'g', 'b', 'a'])
    ramp_dat.appendRow([0.0, 0.0, 0.0, 0.0, 1.0])  # Real Black
    ramp_dat.appendRow([0.2, 0.0, 0.1, 0.4, 1.0])  # Deep Blue
    ramp_dat.appendRow([0.6, 0.0, 0.8, 0.9, 1.0])  # Electric Cyan
    ramp_dat.appendRow([0.9, 0.8, 0.2, 1.0, 1.0])  # White/Hot
    
    ramp.par.dat = ramp_dat.name
    lookup.inputConnectors[0].connect(comp)
    lookup.inputConnectors[1].connect(ramp)
    
    # Final Contrast Boost
    final_lvl = scene.create(levelTOP, 'final_punch')
    final_lvl.par.outputresolution = 0
    final_lvl.par.contrast = 1.3
    final_lvl.par.gamma1 = 0.9
    final_lvl.inputConnectors[0].connect(lookup)

    out = scene.create(nullTOP, 'scene_out')
    out.inputConnectors[0].connect(final_lvl)
    
    # Layout Nodes
    noise.nodeX, noise.nodeY = -1600, 200
    fb.nodeX, fb.nodeY = -1400, -200
    slope.nodeX, slope.nodeY = -1200, -200
    thresh.nodeX, thresh.nodeY = -1000, -200
    xf.nodeX, xf.nodeY = -800, -200
    disp.nodeX, disp.nodeY = -600, -200
    lvl.nodeX, lvl.nodeY = -400, -200
    comp.nodeX, comp.nodeY = -400, 200
    lookup.nodeX, lookup.nodeY = -200, 200
    final_lvl.nodeX, final_lvl.nodeY = 0, 200
    out.nodeX, out.nodeY = 200, 200

    print('[V6 SUCCESS] SCENE_5: Edge Spark Nebula 完成！')
    print('  - Feedback filters peaks only (Preserves Contrast)')
    print('  - Native 88x50 throughout (Sharp Detail)')
    print('='*60)

if __name__ == '__main__':
    deploy()
