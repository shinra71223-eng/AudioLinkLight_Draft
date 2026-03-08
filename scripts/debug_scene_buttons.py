# debug_scene_buttons.py
# ================================================================
# Diagnostics to verify the exact names and parameters of
# button components and scene_select in LED_OUTPUT.
# ================================================================

led_out = op('/AudioLinkLight_V01/LED_OUTPUT')
if not led_out: led_out = op('LED_OUTPUT')

if not led_out:
    print("Error: LED_OUTPUT not found.")
else:
    print(f"--- Foud LED_OUTPUT: {led_out.path} ---")
    
    # Check buttons
    print("\n--- Checking Buttons ---")
    for i in range(1, 7):
        btn_name = f'button{i}'
        btn = led_out.op(btn_name)
        if btn:
            print(f"Found: {btn.name} (Type: {btn.OPType})")
            # Check what state parameter it has
            if hasattr(btn.par, 'state'):
                print(f"  Has 'state' par: {btn.par.state.eval()}")
            # Check other common output properties
            if hasattr(btn, 'panel'):
                try: print(f"  Panel value 'state': {btn.panel.state.val}")
                except: pass
        else:
            print(f"NOT FOUND: {btn_name}")
            
    # Check scene_select
    print("\n--- Checking scene_select ---")
    scene_sel = led_out.op('scene_select')
    if not scene_sel:
        # Search globally in the project
        root = op('/AudioLinkLight_V01') if op('/AudioLinkLight_V01') else op('/')
        scene_sel = root.op('scene_select')
        
    if scene_sel:
        print(f"Found: {scene_sel.name} at {scene_sel.path} (Type: {scene_sel.OPType})")
        # Check integer parameters like 'index'
        if hasattr(scene_sel.par, 'index'):
            print(f"  Has 'index' par: {scene_sel.par.index.eval()}")
        else:
            print("  WARNING: No 'index' parameter found on this node.")
            
        print("  Inputs:")
        for input_op in scene_sel.inputs:
            print(f"    - {input_op.name}")
    else:
        print("NOT FOUND: scene_select")
