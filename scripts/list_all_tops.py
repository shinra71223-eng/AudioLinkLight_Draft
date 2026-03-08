# list_all_tops.py
import td

print("=== All Available TOP Types ===")

# Try to find all attributes in td that end with 'TOP' or look like operator types
all_td = dir(td)
top_types = [s for s in all_td if s.endswith('TOP') and not s.startswith('_')]

# Attempt to create one of each as a test to see what the valid string is
root = op('/AudioLinkLight_V01')
if not root:
    print("Error: /AudioLinkLight_V01 not found.")
else:
    valid_strings = []
    print(f"Found {len(top_types)} potential TOP strings in 'td' module.")
    
    for t in sorted(top_types):
        # We want to find the string value that TD expects for create()
        # Often selectTOP (the class) .__name__ or similar is what we want
        try:
            val = getattr(td, t)
            if isinstance(val, str):
                s_val = val
            elif hasattr(val, '__name__'):
                s_val = val.__name__
            else:
                s_val = str(val)
                
            valid_strings.append(f"{t}: '{s_val}'")
        except:
            pass

    print("\nListing TOP strings found in 'td' attributes:")
    for vs in valid_strings:
        print(vs)

    print("\n--- Searching specifically for 'DAT to' variations ---")
    search_terms = ['dat', 'to', 'texture']
    for s in all_td:
        if any(term in s.lower() for term in search_terms):
            try:
                val = getattr(td, s)
                print(f"Potential match: {s} = {val} (Type: {type(val)})")
            except:
                pass

print("\n=== Check Complete ===")
