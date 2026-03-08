# deploy_scene5_new.py
# ================================================================
# SCENE_5: "Audio Bloom" (Zero-Base Redesign)
# ================================================================
# CONCEPT: 
# 音のエネルギー（Bass）で物理的に膨張する「光の輪」を作り、
# それを高音（Hihat）でうねらせながらフィードバックで空間に広げていく、
# TDのCHOP×TOP連携の王道とも言えるジェネラティブ・アートです。
# 88x50のネイティブ解像度でも、エッジがパキッと美しく光ります。
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
    print(f'[deploy_scene5] {SCENE_PATH} 新コンセプト "Audio Bloom" を構築中...')
    print('='*60)

    # 1. CLEAN UP (完全リセット)
    for o in list(scene.children):
        try: o.destroy()
        except: pass

    # 2. CORE GEOMETRY (光の輪)
    # 完全に鮮明な円形をベースにする
    circle = scene.create(circleTOP, 'base_shape')
    circle.par.outputresolution = 1
    circle.par.resolutionw = RES_W
    circle.par.resolutionh = RES_H
    circle.par.radiusx = 0.15 # 小さめのコア
    circle.par.radiusy = 0.15
    circle.par.softness = 0.0 # エッジをくっきり
    circle.par.fillcolorr, circle.par.fillcolorg, circle.par.fillcolorb = 1, 1, 1
    circle.par.bordercolorr, circle.par.bordercolorg, circle.par.bordercolorb = 0, 0, 0

    # 音（Bass）に合わせて輪が「ドクン」と脈打つ（スケールアップ）
    shape_xf = scene.create(transformTOP, 'shape_pulse')
    shape_xf.par.outputresolution = 1
    shape_xf.par.resolutionw = RES_W
    shape_xf.par.resolutionh = RES_H
    bass_val = f"(op('{AUDIO_PATH}')['uBassEnergy'] if op('{AUDIO_PATH}') else 0)"
    # Base scale + Audio Kick
    shape_xf.par.sx.expr = f"0.5 + ({bass_val} * 1.5)"
    shape_xf.par.sy.expr = shape_xf.par.sx
    shape_xf.inputConnectors[0].connect(circle)

    # 輪郭だけを抽出 (Edge) することでクールなネオン管のようなルックに
    edge = scene.create(edgeTOP, 'neon_edge')
    edge.par.outputresolution = 1
    edge.par.resolutionw = RES_W
    edge.par.resolutionh = RES_H
    try:
        edge.par.blackbg = 1
    except:
        pass
    try:
        edge.par.strength = 10.0
    except:
        pass
    edge.inputConnectors[0].connect(shape_xf)

    # 3. ORGANIC DISTORTION (有機的なうねり)
    disp = scene.create(displaceTOP, 'organic_warp')
    disp_noise = scene.create(noiseTOP, 'warp_noise')
    for n in [disp, disp_noise]:
        n.par.outputresolution = 1
        n.par.resolutionw = RES_W
        n.par.resolutionh = RES_H

    disp_noise.par.type = 'simplex3d'
    disp_noise.par.period = 1.0
    disp_noise.par.tz.expr = 'absTime.seconds * 0.5'
    
    # 高音（Hihat）や中音域が鳴ると、輪郭が激しく歪む（ビリビリする）
    hihat_val = f"(op('{AUDIO_PATH}')['Hihat'] if op('{AUDIO_PATH}') else 0)"
    disp.par.displaceweightx.expr = f"0.01 + ({hihat_val} * 0.15)"
    disp.par.displaceweighty.expr = disp.par.displaceweightx
    
    disp.inputConnectors[0].connect(edge)
    disp.inputConnectors[1].connect(disp_noise)

    # 4. KALEIDOSCOPIC FEEDBACK (華やかな軌跡)
    # ベースの形が崩れないよう、Feedbackは後ろに引きながら残す
    comp = scene.create(compositeTOP, 'comp_feedback')
    fb = scene.create(feedbackTOP, 'feedback1')
    fb_xf = scene.create(transformTOP, 'fb_transform')
    lvl = scene.create(levelTOP, 'fb_level')
    
    for n in [comp, fb, fb_xf, lvl]:
        n.par.outputresolution = 1
        n.par.resolutionw = RES_W
        n.par.resolutionh = RES_H

    try: comp.par.operand = 'maximum' # 白飛び防止
    except: comp.par.operand = 14

    fb.par.top = comp.name
    fb.inputConnectors[0].connect(disp) # Reset to the current warped frame

    # 軌跡を少しずつ外側に広げながら回転させる
    fb_xf.par.extend = 'zero'
    fb_xf.par.sx = 1.06 # 外側に広がる
    fb_xf.par.sy = 1.06
    fb_xf.par.rz.expr = 'absTime.seconds * 5.0' # ゆるやかに回転

    # 残像の減衰と色味の変化（外側にいくほど暗くなる）
    lvl.par.opacity = 0.90
    lvl.par.gamma1 = 0.9 # 残像のディティールを保つ
    
    # 結線: fb -> fb_xf -> lvl -> comp
    fb_xf.inputConnectors[0].connect(fb)
    lvl.inputConnectors[0].connect(fb_xf)
    
    # 合成: 現在の光(disp)と過去の残像(lvl)
    comp.inputConnectors[0].connect(lvl)
    comp.inputConnectors[1].connect(disp)

    # 5. PREMIUM COLOR MAPPING (確実なTable DAT管理)
    lookup = scene.create(lookupTOP, 'color_look')
    ramp = scene.create(rampTOP, 'color_ramp')
    ramp_dat = scene.create(tableDAT, 'ramp_data')
    
    ramp_dat.clear()
    ramp_dat.appendRow(['pos', 'r', 'g', 'b', 'a'])
    # 暗い部分: 無（黒）
    ramp_dat.appendRow([0.0, 0.0, 0.0, 0.0, 1.0])
    # 中間（残像）: ディープパープル -> マゼンタ
    ramp_dat.appendRow([0.2, 0.1, 0.0, 0.3, 1.0])
    ramp_dat.appendRow([0.6, 0.8, 0.0, 0.4, 1.0])
    # コア（発光部）: ゴールド/オレンジ
    ramp_dat.appendRow([0.9, 1.0, 0.6, 0.1, 1.0])
    ramp_dat.appendRow([1.0, 1.0, 1.0, 0.8, 1.0])
    
    ramp.par.dat = ramp_dat.name
    ramp.par.outputresolution = 1
    ramp.par.resolutionw = 256
    ramp.par.resolutionh = 1
    
    lookup.par.outputresolution = 1
    lookup.par.resolutionw = RES_W
    lookup.par.resolutionh = RES_H
    
    lookup.inputConnectors[0].connect(comp)
    lookup.inputConnectors[1].connect(ramp)

    # 6. FINAL OUTPUT
    out = scene.create(nullTOP, 'scene_out')
    out.inputConnectors[0].connect(lookup)

    # Layout Nodes cleanly
    try:
        circle.nodeX, circle.nodeY         = -1400, 200
        shape_xf.nodeX, shape_xf.nodeY     = -1200, 200
        edge.nodeX, edge.nodeY             = -1000, 200
        disp_noise.nodeX, disp_noise.nodeY = -1000, 50
        disp.nodeX, disp.nodeY             = -800,  200
        
        fb.nodeX, fb.nodeY                 = -800, -100
        fb_xf.nodeX, fb_xf.nodeY           = -600, -100
        lvl.nodeX, lvl.nodeY               = -400, -100
        comp.nodeX, comp.nodeY             = -600,  200
        
        ramp_dat.nodeX, ramp_dat.nodeY     = -400,  450
        ramp.nodeX, ramp.nodeY             = -400,  300
        lookup.nodeX, lookup.nodeY         = -400,  200
        out.nodeX, out.nodeY               = -200,  200
    except:
        pass

    print('[NEW SUCCESS] SCENE_5: "Audio Bloom" 完成！')
    print('  - ゼロベースの完全新規アニメーション (Native 88x50)')
    print('  - Bass: コアのサイズが心臓のように脈打つ')
    print('  - Hihat: 光の輪郭がビリビリと有機的に歪む')
    print('  - Feedback: 最大値合成による立体的な残像展開')
    print('='*60)

if __name__ == '__main__':
    deploy()
