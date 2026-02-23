# dump_composite_menu.py
# Dumps all menu options for Composite TOP's operand parameter
# and other key parameters we've been guessing at.

def dump():
    temp = root.create(baseCOMP, 'temp_dump_comp')
    
    c = temp.create(compositeTOP, 'c')
    
    print("=== compositeTOP: operand ===")
    p = c.par.operand
    print(f"  Current value: {p.val}")
    print(f"  Menu names (Python values): {p.menuNames}")
    print(f"  Menu labels (UI labels):    {p.menuLabels}")
    
    print("\n=== compositeTOP: ALL menu parameters ===")
    for par in c.pars():
        if par.menuNames:
            print(f"\n  par.{par.name} ({par.label}):")
            print(f"    Current: {par.val}")
            for i, (name, label) in enumerate(zip(par.menuNames, par.menuLabels)):
                print(f"    [{i}] name='{name}' label='{label}'")
    
    print("\n=== resolutionTOP: key menu parameters ===")
    r = temp.create(resolutionTOP, 'r')
    for par in r.pars():
        if par.menuNames:
            print(f"\n  par.{par.name} ({par.label}):")
            print(f"    Current: {par.val}")
            for i, (name, label) in enumerate(zip(par.menuNames, par.menuLabels)):
                print(f"    [{i}] name='{name}' label='{label}'")
    
    print("\n=== scriptTOP: key parameters ===")
    s = temp.create(scriptTOP, 'st')
    for par in s.pars():
        print(f"  par.{par.name} ({par.label}) = {par.val}")
        if par.menuNames:
            for i, (name, label) in enumerate(zip(par.menuNames, par.menuLabels)):
                print(f"    [{i}] name='{name}' label='{label}'")

    temp.destroy()

dump()
