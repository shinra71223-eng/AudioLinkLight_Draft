# diagnose_script_top.py
import td

print("=== scriptTOP Diagnosis ===")

root = op('/AudioLinkLight_V01')
if not root:
    print("Error: /AudioLinkLight_V01 not found.")
else:
    try:
        # Create a scriptTOP
        s = root.create(scriptTOP, 'diag_script_tmp')
        print(f"Created: {s.name} ({type(s)})")
        
        # List all parameters to find where the script is stored
        print("\nParameters:")
        for p in s.pars():
            print(f"  {p.name}: {p.val}")
            
        # Check if it has a'script' parameter
        if hasattr(s.par, 'script'):
            print("\nFound 'script' parameter. Current value:", s.par.script)
            
        # Check common DAT-like attributes just in case
        for attr in ['text', 'script', 'code']:
            print(f"Has attribute '{attr}': {hasattr(s, attr)}")

        s.destroy()
    except Exception as e:
        print(f"Error: {e}")

print("\n=== Check Complete ===")
