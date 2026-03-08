# fix_panel_assignment.py
import td

led_out = op('/AudioLinkLight_V01/LED_OUTPUT')
if not led_out: led_out = op('LED_OUTPUT')

pe = led_out.op('scene_btn_exec')
if pe:
    print(f"Connecting panels to: {pe.path}")
    
    # Collect button OPs
    btns = []
    btn_paths = []
    for i in range(1, 7):
        b = led_out.op(f'button{i}')
        if b:
            btns.append(b)
            btn_paths.append(b.path)
            
    print(f"Found {len(btns)} buttons.")
    
    # Try setting by list of OPs
    try:
        pe.par.panels = btns
        print("Set par.panels to list of OPs")
    except Exception as e1:
        # Try setting by space-separated absolute paths
        try:
            pe.par.panels = " ".join(btn_paths)
            print("Set par.panels to string of absolute paths")
        except Exception as e2:
            print(f"Failed both methods: {e1}, {e2}")

    # Set value parameter
    pe.par.panelvalue = 'state'
    pe.par.offtoon = 1
    
    print("\nResulting parameters:")
    for p in pe.pars():
        if p.name in ['panels', 'panelvalue', 'offtoon']:
            # par.eval() might return a list of objects, so we print safely
            val = p.eval()
            if isinstance(val, list):
                print(f"  {p.name}: {[o.name for o in val]}")
            else:
                print(f"  {p.name}: {val}")
