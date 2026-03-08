# check_params.py
path = '/AudioLinkLight_V01/LED_SOURCE_USB'
o = op(path)
out_file = 'c:/Users/0008112871/OneDrive - Sony/ドキュメント/AntiGravity/AudioLinkLight_Draft/param_check.txt'

with open(out_file, 'w', encoding='utf-8') as f:
    if not o:
        f.write(f"Node {path} not found\n")
    else:
        f.write(f"Node: {o.path} (Type: {type(o)})\n")
        f.write("Custom Pages:\n")
        for p in o.customPages:
            f.write(f"  - {p.name}\n")
            for par in p.pars:
                f.write(f"    * {par.name}: {par.eval()}\n")
        
        # Check child
        child = o.op('led_exec_x')
        if child:
            f.write(f"\nChild found: {child.path}\n")
        else:
            f.write(f"\nChild NOT found in {o.path}\n")

print("Done")
