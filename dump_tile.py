# dump_tile.py
def dump():
    temp = root.create(baseCOMP, 'temp_dump_tile')
    
    t = temp.create(tileTOP, 't')
    r = temp.create(rectangleTOP, 'r')
    
    print("=== tileTOP ===")
    for p in t.pars():
        print(f"{p.name} ({p.label}) = {p.val}")
        
    print("\n=== rectangleTOP ===")
    for p in r.pars():
        print(f"{p.name} ({p.label}) = {p.val}")
        
    temp.destroy()

dump()
