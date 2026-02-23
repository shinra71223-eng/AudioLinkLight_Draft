# deploy_wave_fix.py - Final 'Threshold Release' Master Version
import traceback

try:
    glsl = op('/AudioLinkLight_V01/TEST_SCREEN2/cyber_clock_v2')
    pixel_dat = op('/AudioLinkLight_V01/TEST_SCREEN2/cyber_clock_v2_pixel22')
    core = op('/AudioLinkLight_V01/AudioLinkCore/out1')
    
    parent_comp = op('/AudioLinkLight_V01/TEST_SCREEN2')
    
    # --- 1. Vocal Onset Wave Trigger ---
    sel_onset = parent_comp.op('vocal_select') or parent_comp.create(selectCHOP, 'vocal_select')
    sel_onset.par.chops = core.path
    sel_onset.par.channames = 'uVocalOnset'
    
    trigger = parent_comp.op('vocal_trigger') or parent_comp.create(triggerCHOP, 'vocal_trigger')
    trigger.inputConnectors[0].disconnect()
    trigger.inputConnectors[0].connect(sel_onset)
    trigger.par.attack = 0.5; trigger.par.sustain = 0; trigger.par.release = 0
    
    # --- 2. Smooth Background Scroll ---
    sel_int = parent_comp.op('vocal_intensity_select') or parent_comp.create(selectCHOP, 'vocal_intensity_select')
    sel_int.par.chops = core.path
    sel_int.par.channames = 'uVocalIntensity'
    
    speed_integrator = parent_comp.op('vocal_speed_integrator') or parent_comp.create(speedCHOP, 'vocal_speed_integrator')
    speed_integrator.inputConnectors[0].disconnect()
    speed_integrator.inputConnectors[0].connect(sel_int)
    speed_integrator.par.limittype = 1; speed_integrator.par.min = 0; speed_integrator.par.max = 100
    
    # --- 3. Sustain 'Threshold Flow' Logic ---
    sel_sus = parent_comp.op('vocal_sustain_select') or parent_comp.create(selectCHOP, 'vocal_sustain_select')
    sel_sus.par.chops = core.path
    sel_sus.par.channames = 'uVocalSustain'

    # Peak Hold CHOP (Sustain中の最大値を保持)
    peak_hold = parent_comp.op('sustain_peak_hold') or parent_comp.create(holdCHOP, 'sustain_peak_hold')
    peak_hold.inputConnectors[0].disconnect()
    peak_hold.inputConnectors[0].connect(sel_sus) # Input 0: Data
    peak_hold.inputConnectors[1].disconnect()
    peak_hold.inputConnectors[1].connect(sel_sus) # Input 1: Trigger (Reset on change)
    peak_hold.par.sample = 1 # While On (音が出ている間は値を追いかけ、止まったらその値をHold)

    # Trigger for Release Animation (1.2s Duration)
    rel_trig = parent_comp.op('sustain_rel_trigger') or parent_comp.create(triggerCHOP, 'sustain_rel_trigger')
    rel_trig.inputConnectors[0].disconnect()
    rel_trig.inputConnectors[0].connect(sel_sus)
    rel_trig.par.threshold = 0.1
    rel_trig.par.triggeron = 1 # Decreasing (音が止まった瞬間に発動)
    rel_trig.par.retrigger = 1
    rel_trig.par.attack = 0
    rel_trig.par.peak = 1
    rel_trig.par.decay = 1.2 # 余韻の時間 1.2s
    rel_trig.par.sustain = 0
    
    # --- 4. GLSL Deployment ---
    glsl_path = project.folder + '/scripts/cyber_clock_wave_fix.glsl'

    if glsl and pixel_dat:
        wave_expr = f"op('{trigger.path}')[0] if op('{trigger.path}') and len(op('{trigger.path}').chans()) > 0 else 0.0"
        scroll_expr = f"op('{speed_integrator.path}')[0]"
        # uSustainVec: X=Len, Y=Phase(0->1), Z=Alpha, W=Mode(0:Fade, 1:Flow)
        sus_len_expr = f"op('{peak_hold.path}')[0]"
        # 余韻トリガーが動いている間(>0)だけPhaseを進める。それ以外は0
        sus_phase_expr = f"(1.0 - op('{rel_trig.path}')[0]) if op('{rel_trig.path}')[0] > 0 else 0.0"
        # 音がある時は音量を、止まったらトリガーの減衰値を使う
        sus_alpha_expr = f"op('{sel_sus.path}')[0] if op('{sel_sus.path}')[0] > 0.1 else op('{rel_trig.path}')[0]"
        sus_mode_expr = f"1.0 if op('{peak_hold.path}')[0] > 0.5 else 0.0"
        
        mapping = [
            (0, 'uTime',        "absTime.seconds"),
            (1, 'uVocal',       f"op('{core.path}')['uVocalIntensity']"),
            (2, 'uOnset',       f"op('{core.path}')['uVocalOnset']"),
            (3, 'uBass',        f"op('{core.path}')['uBassEnergy']"),
            (4, 'uWavePhase',   wave_expr), 
            (5, 'uHour',        None), (6, 'uMinute', None), (7, 'uSecond', None),
            (8, 'uSustainVec',  None), # Handled below
            (9, 'uVocalScroll', scroll_expr) 
        ]

        for slot, name, expr in mapping:
            if name: getattr(glsl.par, f'uniname{slot}').val = name
            if expr: getattr(glsl.par, f'value{slot}x').expr = expr

        # Sustain Packed Uniform (X=Len, Y=Phase, Z=Alpha, W=Mode)
        glsl.par.uniname8.val = 'uSustainVec'
        glsl.par.value8x.expr = sus_len_expr
        glsl.par.value8y.expr = sus_phase_expr
        glsl.par.value8z.expr = sus_alpha_expr
        glsl.par.value8w.expr = sus_mode_expr

        with open(glsl_path, 'r', encoding='utf-8') as f:
            pixel_dat.text = f.read()
            
        print("\n--- DEPLOYED: FINAL MASTER with Threshold Release Logic ---")
    else:
        print("Error: Required nodes not found!")

except Exception as e:
    traceback.print_exc()
