# build_visual_scaffold.py
# Builds the GlobalEngine_Canvas and 5 Screen Set components with crop/mix logic.
# Max resolution for non-commercial TD is 1280x1280.
#
# Verified API: par.chops, par.expr, COMP.create, ParMode.EXPRESSION, ParMode.CONSTANT,
#               conn.connect, OP.destroy()

def build():
    try:
        core = None
        for comp in root.findChildren(type=COMP):
            if 'AudioLinkLight_V' in comp.name:
                core = comp
                break
        if not core:
            print('ERROR: AudioLinkLight not found')
            return

        # ----------------------------------------------------
        # 1. GlobalEngine_Canvas (1280x1280)
        # ----------------------------------------------------
        canvas_name = 'GlobalEngine_Canvas'
        canvas = core.op(canvas_name)
        if canvas:
            canvas.destroy()
        
        canvas = core.create(baseCOMP, canvas_name)
        canvas.nodeX = 1000
        canvas.nodeY = -200
        print(f'Created: {canvas_name}')

        # Input Audio Signal
        c_sel_audio = canvas.create(selectCHOP, 'sel_audio')
        c_sel_audio.par.chops = '../AudioLinkCore/out1'
        c_sel_audio.nodeX = 0
        c_sel_audio.nodeY = 200

        # Global Visual: Background Noise (reacts to uVocalIntensity)
        c_bg = canvas.create(noiseTOP, 'bg_canvas')
        c_bg.par.resolutionw = 1280
        c_bg.par.resolutionh = 720
        c_bg.par.format = 3 # 8-bit fixed (RGBA)
        # Animate Z translation using time.seconds * 0.1
        c_bg.par.tz.mode = ParMode.EXPRESSION
        c_bg.par.tz.expr = "absTime.seconds * 0.1"
        # React to VocalIntensity (Hue)
        c_bg.par.type = 1 # Simplex 3D
        c_bg.par.period = 2
        # Colorize
        c_bg.par.mono = False
        c_bg.nodeX = 200
        c_bg.nodeY = 0

        # Add a Level TOP to boost brightness via uBassEnergy
        c_level = canvas.create(levelTOP, 'level_bass')
        c_level.inputConnectors[0].connect(c_bg)
        c_level.par.brightness1.mode = ParMode.EXPRESSION
        # Bass energy usually 0-1, map to 0.5-1.5
        c_level.par.brightness1.expr = "0.5 + op('sel_audio')['uBassEnergy']*1.0"
        c_level.nodeX = 400
        c_level.nodeY = 0

        # Out TOP
        c_out = canvas.create(outTOP, 'out1')
        c_out.inputConnectors[0].connect(c_level)
        c_out.nodeX = 600
        c_out.nodeY = 0

        # ----------------------------------------------------
        # 2. Local Screen Sets (x5)
        # ----------------------------------------------------
        # Configuration for 5 screens
        screen_configs = [
            {'id': 1, 'x': 0, 'y': 0, 'w': 256, 'h': 256},
            {'id': 2, 'x': 256, 'y': 0, 'w': 256, 'h': 256},
            {'id': 3, 'x': 512, 'y': 0, 'w': 256, 'h': 256},
            {'id': 4, 'x': 768, 'y': 0, 'w': 256, 'h': 256},
            {'id': 5, 'x': 1024, 'y': 0, 'w': 256, 'h': 256},
        ]

        for sc in screen_configs:
            sid = sc['id']
            s_name = f'Screen_{sid:02d}'
            s_comp = core.op(s_name)
            if s_comp:
                s_comp.destroy()

            s_comp = core.create(baseCOMP, s_name)
            s_comp.nodeX = 1000
            s_comp.nodeY = -400 - (sid * 200)
            print(f'Created: {s_name} (Pos: {sc["x"]},{sc["y"]} Size: {sc["w"]}x{sc["h"]})')

            # --- Create Custom Parameters ---
            # Page: ScreenConfig
            page = s_comp.appendCustomPage('ScreenConfig')
            # Parameters
            p_name = page.appendStr('Screenname')[0]
            p_name.val = f'LED_{sid}'
            
            p_w = page.appendInt('Resw')[0]
            p_w.val = sc['w']
            
            p_h = page.appendInt('Resh')[0]
            p_h.val = sc['h']
            
            p_x = page.appendInt('Posx')[0]
            p_x.val = sc['x']
            
            p_y = page.appendInt('Posy')[0]
            p_y.val = sc['y']
            
            p_mix = page.appendFloat('Globalmix')[0]
            p_mix.val = 0.5  # 50% Mix by default

            # --- Internal Nodes ---
            # 1. Audio In
            l_audio = s_comp.create(selectCHOP, 'sel_audio')
            l_audio.par.chops = '../../AudioLinkCore/out1'
            l_audio.nodeX = 0
            l_audio.nodeY = 400

            # 2. Global Canvas In & Crop
            l_global = s_comp.create(selectTOP, 'sel_global')
            l_global.par.top = f'../../{canvas_name}/out1'
            l_global.nodeX = 0
            l_global.nodeY = 200

            l_crop = s_comp.create(cropTOP, 'crop_global')
            l_crop.inputConnectors[0].connect(l_global)
            # Crop uses pixels: Left, Right, Bottom, Top
            # Right = Left + W, Top = Bottom + H
            # Unit 1 = Pixels
            l_crop.par.cropleftunit = 1
            l_crop.par.croprightunit = 1
            l_crop.par.cropbottomunit = 1
            l_crop.par.croptopunit = 1
            
            l_crop.par.cropleft.mode = ParMode.EXPRESSION
            l_crop.par.cropleft.expr = "parent().par.Posx"
            l_crop.par.cropright.mode = ParMode.EXPRESSION
            l_crop.par.cropright.expr = "parent().par.Posx + parent().par.Resw"
            l_crop.par.cropbottom.mode = ParMode.EXPRESSION
            l_crop.par.cropbottom.expr = "parent().par.Posy"
            l_crop.par.croptop.mode = ParMode.EXPRESSION
            l_crop.par.croptop.expr = "parent().par.Posy + parent().par.Resh"
            l_crop.nodeX = 200
            l_crop.nodeY = 200

            # 3. Local Render (Simple circle flashing to Kick)
            l_base = s_comp.create(constantTOP, 'local_bg')
            l_base.par.colorr = 0
            l_base.par.colorg = 0
            l_base.par.colorb = 0
            l_base.par.resolutionw.mode = ParMode.EXPRESSION
            l_base.par.resolutionw.expr = "parent().par.Resw"
            l_base.par.resolutionh.mode = ParMode.EXPRESSION
            l_base.par.resolutionh.expr = "parent().par.Resh"
            l_base.nodeX = 0
            l_base.nodeY = -200

            l_circle = s_comp.create(circleTOP, 'circle_kick')
            l_circle.par.resolutionw.mode = ParMode.EXPRESSION
            l_circle.par.resolutionw.expr = "parent().par.Resw"
            l_circle.par.resolutionh.mode = ParMode.EXPRESSION
            l_circle.par.resolutionh.expr = "parent().par.Resh"
            l_circle.par.radiusx = 0.3
            l_circle.par.radiusy = 0.3
            l_circle.par.fillcolorr = 1
            l_circle.par.fillcolorg = 0.2
            l_circle.par.fillcolorb = 0.2
            # Opacity reacts to Kick
            l_circle.par.fillalpha.mode = ParMode.EXPRESSION
            l_circle.par.fillalpha.expr = "op('sel_audio')['Kick']"
            l_circle.nodeX = 0
            l_circle.nodeY = -400

            l_comp = s_comp.create(compositeTOP, 'comp_local')
            l_comp.inputConnectors[0].connect(l_base)
            l_comp.inputConnectors[1].connect(l_circle)
            l_comp.par.operand = 0 # Over
            l_comp.nodeX = 200
            l_comp.nodeY = -300

            # 4. Cross Mix (Global vs Local)
            l_mix = s_comp.create(crossTOP, 'cross_mix')
            l_mix.inputConnectors[0].connect(l_comp)   # Input 0: Local
            l_mix.inputConnectors[1].connect(l_crop)   # Input 1: Global Crop
            l_mix.par.cross.mode = ParMode.EXPRESSION
            l_mix.par.cross.expr = "parent().par.Globalmix"
            l_mix.nodeX = 400
            l_mix.nodeY = 0

            # 5. Out
            l_out = s_comp.create(outTOP, 'out1')
            l_out.inputConnectors[0].connect(l_mix)
            l_out.nodeX = 600
            l_out.nodeY = 0

        print('\n=== Visual Scaffold Build Complete! ===')
        print('Created GlobalEngine_Canvas (1280x1280)')
        print('Created Screen_01 to Screen_05 with custom properties and crop/mix logic.')

    except Exception as e:
        import traceback
        print(f"Error during execution: {e}")
        traceback.print_exc()

build()
