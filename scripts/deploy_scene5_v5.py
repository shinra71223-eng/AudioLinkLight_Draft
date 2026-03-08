# deploy_scene5_v5.py
# ================================================================
# SCENE_5: "Native Fluid Nebula" (V5 - Native 88x50 Resolution)
# ================================================================
# ・All nodes set to 88x50 strictly (No resizing)
# ・Deep Fluid Feedback: No rotation to prevent skewing
# ・Vibrant Color Mapping (DAT-Driven Ramp)
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
    print(f'[deploy_scene5] {SCENE_PATH} V5: Native {RES_W}x{RES_H} 構築中...')
    print('='*60)

    # 1. CLEAN UP
    for o in list(scene.children):
        try:
            o.destroy()
        except:
            pass

    # 2. SOURCE NOISE (Sharp, Native detail)
    noise = scene.create(noiseTOP, 'noise_base')
    noise.par.outputresolution = 1 # Custom
    noise.par.resolutionw = RES_W
    noise.par.resolutionh = RES_H
    noise.par.type = 'simplex3d'
    noise.par.period = 2.0
    bass_val = f"(op('{AUDIO_PATH}')['uBassEnergy'] if op('{AUDIO_PATH}') else 0)"
    noise.par.period.expr = f"2.0 - ({bass_val} * 0.8)"
    noise.par.tz.expr = 'absTime.seconds * 0.2' # Z-axis morphing
    noise.par.mono = True
    
    # 3. FEEDBACK LOOP (Native 88x50)
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
    fb.inputConnectors[0].connect(noise)
    
    # Movement: Zoom + Subtle Drift (NO ROTATION to avoid skewing)
    xf.par.sx = 1.005 # Subtle scale out
    xf.par.sy = 1.005
    xf.par.tx = 0.001 # Drift right
    
    # Displace (Fluid movement)
    disp_noise.par.type = 'perlin3d'
    disp_noise.par.mono = False
    disp_noise.par.period = 1.0
    disp_noise.par.tz.expr = 'absTime.seconds * 0.4'
    disp.par.displaceweightx.expr = f"0.02 + {bass_val} * 0.08" # Stronger force
    disp.par.displaceweighty.expr = disp.par.displaceweightx
    
    # Feedback Level (Contrast & Decay)
    lvl.par.opacity = 0.85
    hihat_val = f"(op('{AUDIO_PATH}')['Hihat'] if op('{AUDIO_PATH}') else 0)"
    lvl.par.brightness1.expr = f"0.8 + {hihat_val} * 0.8" # Reactive flash
    # Gamma up to push mid-tones into blacks, preventing "flat" look
    lvl.par.gamma1 = 1.1
    
    # WIRING
    xf.inputConnectors[0].connect(fb)
    disp.inputConnectors[0].connect(xf)
    disp.inputConnectors[1].connect(disp_noise)
    lvl.inputConnectors[0].connect(disp)
    
    # Composite: Maximum mode for sharp layering
    try:
        comp.par.operand = 'maximum'
    except:
        comp.par.operand = 14

    comp.inputConnectors[0].connect(lvl)
    comp.inputConnectors[1].connect(noise)
    
    # 4. COLOR LOOKUP (Native mapping)
    lookup = scene.create(lookupTOP, 'color_look')
    ramp = scene.create(rampTOP, 'color_ramp')
    ramp_dat = scene.create(tableDAT, 'ramp_data')
    
    ramp_dat.clear()
    ramp_dat.appendRow(['pos', 'r', 'g', 'b', 'a'])
    ramp_dat.appendRow([0.0, 0.0, 0.0, 0.1, 1.0])  # Void
    ramp_dat.appendRow([0.4, 0.0, 0.5, 0.8, 1.0])  # Electric Blue
    ramp_dat.appendRow([0.7, 0.6, 0.0, 1.0, 1.0])  # Vibrant Purple
    ramp_dat.appendRow([0.95, 1.0, 0.9, 1.0, 1.0]) # Core Bright
    
    ramp.par.dat = ramp_dat.name
    ramp.par.outputresolution = 1
    ramp.par.resolutionw = 256
    ramp.par.resolutionh = 1
    
    lookup.inputConnectors[0].connect(comp)
    lookup.inputConnectors[1].connect(ramp)
    
    # 5. FINAL ADJUST & OUTPUT
    # Add a final Level for ultimate contrast punch
    final_punch = scene.create(levelTOP, 'final_punch')
    final_punch.par.outputresolution = 0
    final_punch.par.contrast = 1.1
    final_punch.par.gamma1 = 1.0
    final_punch.inputConnectors[0].connect(lookup)

    out = scene.create(nullTOP, 'scene_out')
    out.inputConnectors[0].connect(final_punch)
    
    # Layout Nodes
    noise.nodeX,     noise.nodeY      = -1400, 200
    fb.nodeX,        fb.nodeY         = -1200, -200
    xf.nodeX,        xf.nodeY         = -1000, -200
    disp_noise.nodeX, disp_noise.nodeY = -1000, -400
    disp.nodeX,      disp.nodeY       = -800, -200
    lvl.nodeX,       lvl.nodeY        = -600, -200
    comp.nodeX,      comp.nodeY       = -600, 200
    ramp_dat.nodeX,  ramp_dat.nodeY    = -400, 450
    ramp.nodeX,      ramp.nodeY       = -400, 300
    lookup.nodeX,    lookup.nodeY     = -200, 200
    final_punch.nodeX, final_punch.nodeY = 0, 200
    out.nodeX,       out.nodeY        = 200, 200

    print('[V5 SUCCESS] SCENE_5: Native 88x50 Fluid Nebula 完成！')
    print('  - All nodes running at native resolution (No Blur)')
    print('  - Rotational distortion eliminated by morphing approach.')
    print('='*60)

if __name__ == '__main__':
    deploy()
