# verify_td_params.py
def inspect_op_params(op_type, label):
    print(f"\n--- Inspecting {label} ({op_type}) ---")
    # Create a temporary operator in /tmp (or inside SCENE_5 if /tmp doesn't exist)
    target = op('/AudioLinkLight_V01/SCENE_5')
    if not target:
        target = op('/')
    # Node names in TD cannot have spaces
    safe_name = f'tmp_inspect_{label.replace(" ", "_")}'
    # Use the type object itself instead of string if possible, 
    # but since types are passed as arguments, we'll try to resolve them.
    try:
        tmp_op = target.create(op_type, safe_name)
    except Exception as e:
        print(f"Failed to create {op_type} with string. Error: {e}")
        return

    try:
        # pars is a method that returns a list when given a pattern
        found = []
        all_params = tmp_op.pars('*') 
        
        keywords = ['displace', 'weight', 'src', 'index', 'fit', 'pos', 'color', 'bright', 'gamma', 'contrast', 'opac', 'resolution', 'operand']
        
        for p in all_params:
            for kw in keywords:
                if kw in p.name.lower():
                    found.append(f"{p.name} (label: {p.label})")
                    break
        
        if found:
            print("Found relevant parameters:")
            for item in sorted(set(found)):
                print(f"  - {item}")
        else:
            print("No matching keywords found. Listing first 20 parameters:")
            for p in list(all_params)[:20]:
                print(f"  - {p.name} ({p.label})")
    finally:
        tmp_op.destroy()

# Inspect nodes used in SCENE_5 V3
print("="*60)
print("TOUCHDESIGNER PARAMETER INSPECTION (V3 Edition)")
print("="*60)

inspect_op_params(displaceTOP, 'Displace TOP')
inspect_op_params(lookupTOP, 'Lookup TOP')
inspect_op_params(rampTOP, 'Ramp TOP')
inspect_op_params(fitTOP, 'Fit TOP')

print("\n" + "="*60)
