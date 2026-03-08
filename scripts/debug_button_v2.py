# debug_button_v2.py
import td
btn = op('/AudioLinkLight_V01/DEPLOY_SCENES')
print("=== DEPLOY_SCENES Button Deep Dive ===")
if not btn:
    print("CRITICAL: Button node not found at /AudioLinkLight_V01/DEPLOY_SCENES")
else:
    print(f"Node found: {btn.path}")
    print(f"Type: {btn.type}")
    print(f"Display: {btn.par.display.eval()}")
    
    # Check parameters
    par_names = [p.name for p in btn.pars()]
    print(f"Available relevant parameters: {[p for p in par_names if 'callback' in p or 'script' in p or 'button' in p]}")
    
    if hasattr(btn.par, 'buttontype'):
        print(f"Button Type: {btn.par.buttontype.eval()} (0=Momentary, 1=Toggle, etc)")
    
    dat = None
    if hasattr(btn.par, 'callbacks'):
        dat = btn.par.callbacks.eval()
        print(f"par.callbacks points to: {dat.path if dat else 'None'}")
    if hasattr(btn.par, 'script'):
        dat_s = btn.par.script.eval()
        print(f"par.script points to: {dat_s.path if dat_s else 'None'}")
        if not dat: dat = dat_s

    if dat:
        print("--- Callback Script Content ---")
        print(dat.text)
        print("-------------------------------")
        
        # Test if onOffToOn is defined
        try:
            # We would need to exec the text to check, but let's just grep
            if 'def onOffToOn' in dat.text:
                print("SUCCESS: 'def onOffToOn' found in callback text.")
            else:
                print("WARNING: 'def onOffToOn' NOT found in callback text.")
        except: pass
    else:
        print("ERROR: No callback DAT linked.")

print("=== Check Complete ===")
