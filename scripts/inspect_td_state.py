# inspect_td_state.py
# Run this in TD Textport to dump detailed state of relevant nodes.

def inspect():
    targets = [
        '/AudioLinkLight_V01/SCENE_4/scene_out',
        '/AudioLinkLight_V01/LED_OUTPUT/scene_select',
        '/AudioLinkLight_V01/LED_OUTPUT/brightness',
        '/AudioLinkLight_V01/LED_OUTPUT/crop_center',
        '/AudioLinkLight_V01/LED_OUTPUT/led_source'
    ]
    
    print("="*80)
    print(f"{'Node Path':<50} | {'Res WxH':<12} | {'OutRes Mode'}")
    print("-"*80)
    
    for path in targets:
        o = op(path)
        if not o:
            print(f"{path:<50} | {'NOT FOUND':<12} | -")
            continue
            
        res = f"{o.width}x{o.height}"
        out_res = "N/A"
        if hasattr(o.par, 'outputresolution'):
            # Show the label or index of the menu
            out_res = f"{o.par.outputresolution.val} ({o.par.outputresolution.menuNames[int(o.par.outputresolution)]})"
            
        print(f"{o.path:<50} | {res:<12} | {out_res}")
        
    print("="*80)
    print("\n[CONNECTIONS in LED_OUTPUT]")
    base = op('/AudioLinkLight_V01/LED_OUTPUT')
    if base:
        for o in base.children:
            # Correctly find the ACTUAL node it is connected FROM
            inputs = []
            for c in o.inputConnectors:
                for conn in c.connections:
                    inputs.append(conn.owner.name)
            if inputs:
                print(f"  {o.name} <--- {', '.join(inputs)}")

    print("\n[CROP PARAMETERS]")
    crop = op('/AudioLinkLight_V01/LED_OUTPUT/crop_center')
    if crop:
        params = ['cropbottom', 'croptop', 'cropbottomunit', 'croptopunit']
        for p_name in params:
            p = getattr(crop.par, p_name, None)
            if p is not None:
                val_text = p.val
                if p.isMenu:
                    val_text = f"{p.val} ({p.menuNames[int(p)]})"
                print(f"  {p_name}: {val_text}")

inspect()
