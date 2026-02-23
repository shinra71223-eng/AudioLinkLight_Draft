# diagnose_sustain_logic.py
def diagnose():
    parent_comp = op('/AudioLinkLight_V01/TEST_SCREEN2')
    sus_sel = parent_comp.op('vocal_sustain_select')
    peak_hold = parent_comp.op('sustain_peak_hold')
    rel_trig = parent_comp.op('sustain_rel_trigger')
    
    print("\n--- Sustain Logic Diagnosis ---")
    if not all([sus_sel, peak_hold, rel_trig]):
        print("Error: Some nodes are missing!")
        return

    print(f"Sustain Input: {sus_sel[0] if len(sus_sel.chans()) > 0 else 'N/A'}")
    print(f"Peak Hold Output: {peak_hold[0] if len(peak_hold.chans()) > 0 else 'N/A'} (Sample Mode: {peak_hold.par.sample.val})")
    print(f"Release Trigger Output: {rel_trig[0] if len(rel_trig.chans()) > 0 else 'N/A'} (Trigger On Mode: {rel_trig.par.triggeron.val})")
    
    # Check GLSL expressions
    glsl = op('/AudioLinkLight_V01/TEST_SCREEN2/cyber_clock_v2')
    if glsl:
        print(f"GLSL SustainVec Exprs: X={glsl.par.value8x.expr}, Y={glsl.par.value8y.expr}, Z={glsl.par.value8z.expr}, W={glsl.par.value8w.expr}")

diagnose()
