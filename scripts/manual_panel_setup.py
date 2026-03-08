# manual_panel_setup.py
import td

led_out = op('/AudioLinkLight_V01/LED_OUTPUT')
if not led_out: led_out = op('LED_OUTPUT')

pe = led_out.op('scene_btn_exec')
if pe:
    print(f"Assigning panels to: {pe.path}")
    
    # Method 1: par.panels
    try:
        pe.par.panels = 'button1 button2 button3 button4 button5 button6'
        print("Set par.panels manually.")
    except Exception as e:
        print(f"Error setting panels: {e}")
        
    # Method 2: For newer TD versions, the parameter is 'panelv' or 'panelvalue'
    try:
        pe.par.panelv = 'state'
        print("Set panelv = 'state'")
    except Exception as e1:
        try:
            pe.par.panelvalue = 'state'
            print("Set panelvalue = 'state'")
        except Exception as e2:
            print(f"Error setting value par: {e1}, {e2}")
            
    # Method 3: 'panel' for older versions
    try:
        pe.par.panel = 'state'
        print("Set panel = 'state'")
    except: pass
    
    print("\nCheck parameters now:")
    for p in pe.pars():
        if p.name in ['panels', 'panelv', 'panelvalue', 'panel', 'offtoon']:
            print(f"  {p.name}: {p.eval()}")
