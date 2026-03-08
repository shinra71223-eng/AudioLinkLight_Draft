# debug_btn_exec.py
# Check if scene_btn_exec exists, is active, and what it prints
import td

led_out = op('/AudioLinkLight_V01/LED_OUTPUT')
if not led_out: led_out = op('LED_OUTPUT')

if not led_out:
    print("Error: LED_OUTPUT not found.")
else:
    pe = led_out.op('scene_btn_exec')
    if pe:
        print(f"--- Foud Panel Execute DAT: {pe.path} ---")
        print(f"Panels string: {pe.par.panels.eval()}")
        print(f"Panel par: {pe.par.panel.eval()}")
        print(f"offToOn par: {pe.par.offtoon.eval()}")
        
        # Check text
        print("\nScript content:")
        print(pe.text)
        
        scene_sel = led_out.op('scene_select')
        if not scene_sel: scene_sel = op('/AudioLinkLight_V01/scene_select')
        if scene_sel:
            print(f"\nscene_select index current value: {scene_sel.par.index.eval()}")
            if hasattr(scene_sel.par.index, 'expr') and scene_sel.par.index.expr:
                print(f"scene_select index EXPR: {scene_sel.par.index.expr}")
    else:
        print("ERROR: scene_btn_exec DAT not found!")
