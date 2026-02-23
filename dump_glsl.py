# dump_glsl.py
def dump():
    temp = root.create(baseCOMP, 'temp_dump_glsl')
    g = temp.create(glslTOP, 'g')
    
    print("=== glslTOP parameters ===")
    for par in g.pars():
        print(f"  par.{par.name} ({par.label}) = {par.val}")
        if par.menuNames:
            for i, (name, label) in enumerate(zip(par.menuNames, par.menuLabels)):
                print(f"    [{i}] name='{name}' label='{label}'")
    
    temp.destroy()

dump()
