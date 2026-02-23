# build_test_screen.py
# Builds a single TEST_SCREEN with resolution W: 88, H: 10
# Uses Script TOP + numpy for pixel-perfect LED grid mask

import traceback

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

        canvas_name = 'GlobalEngine_Canvas'
        s_name = 'TEST_SCREEN'
        sc_w = 88
        sc_h = 10
        sc_x = 0
        sc_y = 0
        SCALE = 10  # 1 LED pixel = 10x10 screen pixels

        # Create or recreate TEST_SCREEN
        s_comp = core.op(s_name)
        if s_comp:
            s_comp.destroy()

        s_comp = core.create(baseCOMP, s_name)
        s_comp.nodeX = 1000
        s_comp.nodeY = -200
        print(f'Created: {s_name} (Size: {sc_w}x{sc_h})')

        # --- Custom Parameters ---
        page = s_comp.appendCustomPage('ScreenConfig')
        page.appendStr('Screenname')[0].val = 'TEST_LED'
        page.appendInt('Resw')[0].val = sc_w
        page.appendInt('Resh')[0].val = sc_h
        page.appendInt('Posx')[0].val = sc_x
        page.appendInt('Posy')[0].val = sc_y
        page.appendFloat('Globalmix')[0].val = 0.5

        # 1. Audio In
        l_audio = s_comp.create(selectCHOP, 'sel_audio')
        l_audio.par.chops = '../AudioLinkCore/out1'
        l_audio.nodeX = 0
        l_audio.nodeY = 400

        # 2. Global Canvas In & Crop
        l_global = s_comp.create(selectTOP, 'sel_global')
        l_global.par.top = f'../{canvas_name}/out1'
        l_global.nodeX = 0
        l_global.nodeY = 200

        l_crop = s_comp.create(cropTOP, 'crop_global')
        l_crop.inputConnectors[0].connect(l_global)
        l_crop.par.cropleftunit = 1; l_crop.par.croprightunit = 1
        l_crop.par.cropbottomunit = 1; l_crop.par.croptopunit = 1
        l_crop.par.cropleft.mode = ParMode.EXPRESSION; l_crop.par.cropleft.expr = "parent().par.Posx"
        l_crop.par.cropright.mode = ParMode.EXPRESSION; l_crop.par.cropright.expr = "parent().par.Posx + parent().par.Resw"
        l_crop.par.cropbottom.mode = ParMode.EXPRESSION; l_crop.par.cropbottom.expr = "parent().par.Posy"
        l_crop.par.croptop.mode = ParMode.EXPRESSION; l_crop.par.croptop.expr = "parent().par.Posy + parent().par.Resh"
        l_crop.nodeX = 200
        l_crop.nodeY = 200

        # 3. Local Render (Kick flash)
        l_base = s_comp.create(constantTOP, 'local_bg')
        l_base.par.colorr = 0; l_base.par.colorg = 0; l_base.par.colorb = 0
        l_base.par.resolutionw.mode = ParMode.EXPRESSION; l_base.par.resolutionw.expr = "parent().par.Resw"
        l_base.par.resolutionh.mode = ParMode.EXPRESSION; l_base.par.resolutionh.expr = "parent().par.Resh"
        l_base.nodeX = 0
        l_base.nodeY = -200

        l_circle = s_comp.create(circleTOP, 'circle_kick')
        l_circle.par.resolutionw.mode = ParMode.EXPRESSION; l_circle.par.resolutionw.expr = "parent().par.Resw"
        l_circle.par.resolutionh.mode = ParMode.EXPRESSION; l_circle.par.resolutionh.expr = "parent().par.Resh"
        l_circle.par.radiusx = 0.45; l_circle.par.radiusy = 0.45
        l_circle.par.fillcolorr = 1; l_circle.par.fillcolorg = 0.2; l_circle.par.fillcolorb = 0.2
        l_circle.par.fillalpha.mode = ParMode.EXPRESSION; l_circle.par.fillalpha.expr = "op('sel_audio')['Kick']"
        l_circle.nodeX = 0
        l_circle.nodeY = -400

        l_comp = s_comp.create(compositeTOP, 'comp_local')
        l_comp.inputConnectors[0].connect(l_base)
        l_comp.inputConnectors[1].connect(l_circle)
        l_comp.par.operand = 'over'
        l_comp.nodeX = 200
        l_comp.nodeY = -300

        # 4. Cross Mix (88x10 Data for actual LED)
        l_mix = s_comp.create(crossTOP, 'cross_mix')
        l_mix.inputConnectors[0].connect(l_comp)
        l_mix.inputConnectors[1].connect(l_crop)
        l_mix.par.cross.mode = ParMode.EXPRESSION
        l_mix.par.cross.expr = "parent().par.Globalmix"
        l_mix.nodeX = 400
        l_mix.nodeY = 0

        # 5. Out (Actual 88x10 for LED device)
        l_out = s_comp.create(outTOP, 'out_led')
        l_out.inputConnectors[0].connect(l_mix)
        l_out.nodeX = 600
        l_out.nodeY = 100

        # ========== LED PREVIEW (GLSL GPU Shader) ==========

        # 6. We DON'T scale the input first! We pipe the raw 88x10 data directly into GLSL.
        # The GLSL shader itself will generate the 264x30 output, reading from the 88x10 input exactly.
        
        # 7. GLSL Shader DAT
        l_glsl_dat = s_comp.create(textDAT, 'glsl_pixel')
        l_glsl_dat.text = '''// 3x3 True Hardware LED Simulation Shader + Full Audio-Reactive Demo
uniform float uTime;
uniform float uClap;
uniform float uVocal;
uniform float uBass;
uniform float uHihat;
out vec4 fragColor;

void main()
{
    // Output resolution (264x30)
    vec2 outRes = uTDOutputInfo.res.zw;
    
    // Input resolution (88x10)
    vec2 inRes = uTDOutputInfo.res.zw / 3.0;
    
    // Exact output pixel coordinate as integers
    vec2 pixelCoord = floor(vUV.st * outRes);
    
    // Which 3x3 cell? (x: 0...87, y: 0...9)
    vec2 cellIndex = floor(pixelCoord / 3.0);
    
    // Where inside the 3x3 cell?
    vec2 posInCell = mod(pixelCoord, 3.0);
    
    if (posInCell.x == 1.0 && posInCell.y == 1.0) {
        // --- 1. Base Image Data ---
        vec2 sampleUV = (cellIndex + vec2(0.5)) / inRes;
        vec4 baseColor = texture(sTD2DInputs[0], sampleUV);
        
        // --- 2. Generative Background Wave (Modulated by Bass) ---
        vec2 uv = cellIndex / inRes;
        
        // Wave pattern that pulses with Bass energy
        float wave1 = sin(uv.x * 10.0 + uTime * 2.0);
        float wave2 = cos(uv.y * 5.0 - uTime * 1.5 + wave1);
        float brightness = (wave1 + wave2) * 0.5 + 0.5;
        
        // Bass controls overall wave intensity (dim when quiet, vivid when loud)
        brightness *= (0.1 + uBass * 0.9);
        
        // Flowing cyberpunk colors (Cyan to Magenta)
        vec3 genColor = vec3(0.1, 0.8, 1.0) * brightness;
        genColor += vec3(1.0, 0.2, 0.8) * (1.0 - brightness) * (0.1 + uBass * 0.9);
        
        // Combine generative art with the underlying video canvas (Screen blend)
        vec3 finalColor = baseColor.rgb + genColor - (baseColor.rgb * genColor);
        
        // --- 3. Vocal-Reactive Generative Orb ---
        vec2 orbUV = uv - vec2(0.5);
        orbUV.x *= (inRes.x / inRes.y); // Aspect ratio correction (88:10)
        
        float orbDist = length(orbUV);
        
        // Base radius of 1.0 (always visible) + expands with VocalIntensity
        float orbRadius = 1.0 + uVocal * 3.0;
        
        // Soft glowing sphere using inverse-square falloff
        float glow = 1.0 / (1.0 + orbDist * orbDist * 4.0 / max(orbRadius * orbRadius, 0.01));
        
        // Golden color, intensity scales with vocal
        vec3 orbColor = vec3(1.0, 0.6, 0.1) * glow * (0.3 + uVocal * 1.5);
        
        // White-hot core when singing loudly
        float coreGlow = 1.0 / (1.0 + orbDist * orbDist * 40.0);
        orbColor += vec3(1.0, 0.95, 0.8) * coreGlow * uVocal * 3.0;
        
        finalColor += orbColor;

        // --- 4. Outer Ring reacts to HiHat (10x brightness boost) ---
        if (cellIndex.x == 0.0 || cellIndex.x == inRes.x - 1.0 || 
            cellIndex.y == 0.0 || cellIndex.y == inRes.y - 1.0) {
            finalColor *= (1.0 + uHihat * 9.0); // 1x normal, up to 10x on HiHat
        }
        
        // --- 5. Clap: Full canvas white flash ---
        finalColor += vec3(1.0, 1.0, 1.0) * uClap * 2.0;
        
        fragColor = vec4(finalColor, 1.0);
    } else {
        // Hardware LED gaps
        fragColor = vec4(0.0, 0.0, 0.0, 1.0);
    }
}'''
        l_glsl_dat.nodeX = 600
        l_glsl_dat.nodeY = -250

        # 8. GLSL TOP (Outputs the final 264x30 preview)
        l_glsl = s_comp.create(glslTOP, 'led_glsl')
        l_glsl.inputConnectors[0].connect(l_mix) # Connect RAW 88x10 data directly!
        l_glsl.par.pixeldat = 'glsl_pixel'
        l_glsl.par.outputresolution = 'custom'
        l_glsl.par.resolutionw.mode = ParMode.EXPRESSION
        l_glsl.par.resolutionw.expr = "parent().par.Resw * 3"
        l_glsl.par.resolutionh.mode = ParMode.EXPRESSION
        l_glsl.par.resolutionh.expr = "parent().par.Resh * 3"
        
        # Uniform 0: Time
        l_glsl.par.uniname0 = "uTime"
        l_glsl.par.value0x.mode = ParMode.EXPRESSION
        l_glsl.par.value0x.expr = "absTime.seconds"
        
        # Uniform 1: Clap (exact channel name from AudioLinkCore)
        l_glsl.par.uniname1 = "uClap"
        l_glsl.par.value1x.mode = ParMode.EXPRESSION
        l_glsl.par.value1x.expr = "float(op('sel_audio')['Clap'] or 0)"
        
        # Uniform 2: VocalIntensity (exact channel name: 'uVocalIntensity')
        l_glsl.par.uniname2 = "uVocal"
        l_glsl.par.value2x.mode = ParMode.EXPRESSION
        l_glsl.par.value2x.expr = "float(op('sel_audio')['uVocalIntensity'] or 0)"
        
        # Uniform 3: BassEnergy (exact channel name: 'uBassEnergy')
        l_glsl.par.uniname3 = "uBass"
        l_glsl.par.value3x.mode = ParMode.EXPRESSION
        l_glsl.par.value3x.expr = "float(op('sel_audio')['uBassEnergy'] or 0)"
        
        # Uniform 4: Hihat (exact channel name: 'Hihat', lowercase h!)
        l_glsl.par.uniname4 = "uHihat"
        l_glsl.par.value4x.mode = ParMode.EXPRESSION
        l_glsl.par.value4x.expr = "float(op('sel_audio')['Hihat'] or 0)"
        
        l_glsl.nodeX = 800
        l_glsl.nodeY = -150

        # 9. Out Preview
        l_out_prev = s_comp.create(outTOP, 'out_preview')
        l_out_prev.inputConnectors[0].connect(l_glsl)
        l_out_prev.nodeX = 1000
        l_out_prev.nodeY = -150

        print('\n=== TEST_SCREEN Created with GLSL LED GPU Simulation! ===')
        print('The Script TOP will generate 880 LED spheres on first cook.')

    except Exception as e:
        import traceback
        print(f"Error during execution: {e}")
        traceback.print_exc()

build()
