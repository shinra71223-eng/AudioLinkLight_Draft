# debug_button.py
import td
btn = op('/AudioLinkLight_V01/DEPLOY_SCENES')
print("=== DEPLOY_SCENES Button Check ===")
if not btn:
    print("Error: /AudioLinkLight_V01/DEPLOY_SCENES not found.")
else:
    print(f"Path: {btn.path}")
    print(f"Type: {btn.type}")
    print(f"Button Type (par.buttontype): {btn.par.buttontype.eval() if hasattr(btn.par, 'buttontype') else 'N/A'}")
    
    # Check for callbacks DAT
    dat = None
    if hasattr(btn.par, 'callbacks'): dat = btn.par.callbacks.eval()
    elif hasattr(btn.par, 'script'): dat = btn.par.script.eval()
    
    if dat:
        print(f"Callback DAT: {dat.path}")
        print("--- Content ---")
        print(dat.text)
        print("---------------")
    else:
        print("No Callback DAT found linked to parameters.")
        # Try to find a DAT named DEPLOY_SCENES_script or similar
        potential = btn.parent().op('DEPLOY_SCENES_script') or btn.op('callbacks')
        if potential:
            print(f"Found potential DAT: {potential.path}")
            print(potential.text)
        else:
            print("No potential callback DATs found.")

print("=== Check Complete ===")
