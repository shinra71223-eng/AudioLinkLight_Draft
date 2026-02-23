import td

def find_switch_chops():
    print("\n--- [SEARCH] Locating tier_switch CHOP ---")
    root = op('/AudioLinkLight_V01')
    if not root:
        print("ERROR: /AudioLinkLight_V01 not found.")
        return
        
    found_any = False
    
    # Recursively search for all Switch CHOPs
    for node in root.findChildren(type=switchCHOP):
        path = node.path
        name = node.name
        
        # Check if the name looks like what we want, or what inputs it has
        if "switch" in name.lower() or "tier" in name.lower():
            inputs = [inp.name for inp in node.inputs]
            print(f"✅ FOUND MATCH: {path}")
            print(f"   Name: {name}")
            print(f"   Inputs: {inputs}")
            found_any = True
            
    if not found_any:
        print("❌ Could not find any Switch CHOPs matching 'tier_switch' in the network.")
        
    print("------------------------------------------")

find_switch_chops()
