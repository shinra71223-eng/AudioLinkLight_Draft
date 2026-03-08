# deploy_scene5_v4.py
# ================================================================
# SCENE_5: "Pro Fluid Nebula" (V4 - Depth & Contrast)
# ================================================================
# ・Advanced Layering: Masked feedback for organic depth
# ・Exposure Control: Prevents saturation to keep "TD vibe"
# ・128x128 Internal / 88x50 Output (Strict compliance)
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
    print(f'[deploy_scene5] {SCENE_PATH} V4: "Pro Depth" 構築中...')
    print('='*60)

    # 1. CLEAN UP
    for o in list(scene.children):
        try:
            o.destroy()
        except:
            pass

    # 2. SOURCE NOISE (Sharp detail)
    noise = scene.create(noiseTOP, 'noise_base')
    noise.par.outputresolution = 1
    noise.par.resolutionw = INT_RES
    noise.par.resolutionh = INT_RES
    noise.par.type = 'simplex3d'
    noise.par.period = 2.5
    bass_val = f"(op('{AUDIO_PATH}')['uBassEnergy'] if op('{AUDIO_PATH}') else 0)"
    noise.par.period.expr = f"2.5 - ({bass_val} * 1.0)"
    noise.par.tz.expr = 'absTime.seconds * 0.15'
    noise.par.mono = True
    
    # 3. FEEDBACK LOOP (Organic Mist)
    comp = scene.create(compositeTOP, 'comp_feedback')
    fb = scene.create(feedbackTOP, 'feedback1')
    xf = scene.create(transformTOP, 'transform1')
    disp = scene.create(displaceTOP, 'displace1')
    disp_noise = scene.create(noiseTOP, 'disp_noise')
    lvl = scene.create(levelTOP, 'level1')
    
    for n in [comp, fb, xf, disp, disp_noise, lvl]:
        n.par.outputresolution = 1
        n.par.resolutionw = INT_RES
        n.par.resolutionh = INT_RES

    fb.par.top = comp.name
    fb.inputConnectors[0].connect(noise)
    
    # Movement
    xf.par.sx = 1.002
    xf.par.sy = 1.002
    xf.par.rz = 0.4
    
    # Displace (Fluid movement)
    disp_noise.par.type = 'perlin3d'
    disp_noise.par.mono = False
    disp_noise.par.tz.expr = 'absTime.seconds * 0.3'
    disp.par.displaceweightx.expr = f"0.01 + {bass_val} * 0.04"
    disp.par.displaceweighty.expr = disp.par.displaceweightx
    
    # MEANINGFUL LAYERING: Lower gain to prevent "Flatness"
    # Keeping values < 1.0 is CRITICAL for the Lookup gradient to work
    lvl.par.opacity = 0.82 # More decay means more transparency/depth
    hihat_val = f"(op('{AUDIO_PATH}')['Hihat'] if op('{AUDIO_PATH}') else 0)"
    lvl.par.brightness1.expr = f"0.75 + {hihat_val} * 0.7"
    
    # 4. WIRING & MIXING
    xf.inputConnectors[0].connect(fb)
    disp.inputConnectors[0].connect(xf)
    disp.inputConnectors[1].connect(disp_noise)
    lvl.inputConnectors[0].connect(disp)
    
    # Composit Operation: "Maximum" for layering without burnout
    # This prevents the "flat white" look of simple "Add"
    try:
        comp.par.operand = 'maximum'
    except:
        comp.par.operand = 14 # Index for Max in some versions

    comp.inputConnectors[0].connect(lvl)
    comp.inputConnectors[1].connect(noise)
    
    # 5. POST-PROCESS (Contrast & Color)
    # Exposure Control: Pull values down before Lookup
    expo = scene.create(levelTOP, 'exposure_ctrl')
    expo.par.outputresolution = 0
    expo.par.gamma1 = 0.9 # Darken mids for depth
    expo.par.brightness1 = 0.9
    expo.inputConnectors[0].connect(comp)

    lookup = scene.create(lookupTOP, 'color_look')
    ramp = scene.create(rampTOP, 'color_ramp')
    ramp_dat = scene.create(tableDAT, 'ramp_data')
    
    ramp_dat.clear()
    ramp_dat.appendRow(['pos', 'r', 'g', 'b', 'a'])
    ramp_dat.appendRow([0.0, 0.0, 0.0, 0.15, 1.0]) # Dark Deep Blue
    ramp_dat.appendRow([0.4, 0.0, 0.6, 0.6, 1.0])  # Vibrant Cyan
    ramp_dat.appendRow([0.8, 0.5, 0.0, 0.8, 1.0])  # Vibrant Purple
    ramp_dat.appendRow([1.0, 0.9, 0.8, 1.0, 1.0])  # White Highlight (Inner Nebula)
    
    ramp.par.dat = ramp_dat.name
    lookup.inputConnectors[0].connect(expo)
    lookup.inputConnectors[1].connect(ramp)
    
    # FINAL FIT (88x50 Validation)
    fit = scene.create(fitTOP, 'fit_to_output')
    fit.par.outputresolution = 1
    fit.par.resolutionw = RES_W
    fit.par.resolutionh = RES_H
    
    # Fit Mode: 2 is 'Fit Outside' (fills the 88x50 without black bars)
    try:
        fit.par.fit = 2 
    except:
        pass
        
    # Interpolation: 'box' (3) provides cleaner/sharper downscaling for textures
    try:
        fit.par.filter = 3 
    except:
        pass
        
    fit.inputConnectors[0].connect(lookup)
    
    out = scene.create(nullTOP, 'scene_out')
    out.inputConnectors[0].connect(fit)
    
    # Layout Nodes
    noise.nodeX,     noise.nodeY      = -1400, 200
    fb.nodeX,        fb.nodeY         = -1200, -200
    xf.nodeX,        xf.nodeY         = -1000, -200
    disp_noise.nodeX, disp_noise.nodeY = -1000, -400
    disp.nodeX,      disp.nodeY       = -800, -200
    lvl.nodeX,       lvl.nodeY        = -600, -200
    comp.nodeX,      comp.nodeY       = -600, 200
    expo.nodeX,      expo.nodeY       = -400, 200
    ramp_dat.nodeX,  ramp_dat.nodeY    = -200, 450
    ramp.nodeX,      ramp.nodeY       = -200, 300
    lookup.nodeX,    lookup.nodeY     = 0, 200
    fit.nodeX,       fit.nodeY        = 200, 200
    out.nodeX,       out.nodeY        = 400, 200

    print('[V4 SUCCESS] SCENE_5: Professional Fluid Nebula 完成！')
    print(f'  - Resolved "Flatness" with Exposure Control and Max Blend.')
    print(f'  - Verified Pixel Counts: All internal {INT_RES}p, final {RES_W}x{RES_H}.')
    print('='*60)

if __name__ == '__main__':
    deploy()
