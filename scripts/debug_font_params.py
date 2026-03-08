# debug_font_params.py
# Diagnose exactly what font parameters the working text_generator has
scene = op('/AudioLinkLight_V01/SCENE_6')
if not scene:
    scene = op('SCENE_6')

print("--- Font Parameter Diagnosis ---")

gen = scene.op('text_generator')
if gen:
    print(f"text_generator exists: {gen.path}")
    print(f"  resolution: {gen.par.resolutionw}x{gen.par.resolutionh}")
    # Check all possible font size params
    for pname in ['fontsizey', 'fontsizex', 'fontsizeyunit', 'fontsizexunit', 
                   'size', 'fontsize', 'fontsizeunit', 'font', 'bold',
                   'aligny', 'alignx', 'linespacing', 'linespacingunit',
                   'antialiasing']:
        p = getattr(gen.par, pname, None)
        if p is not None:
            val = str(p)
            if hasattr(p, 'menuIndex'):
                val += f" (menuIndex={p.menuIndex})"
            if hasattr(p, 'expr') and p.expr:
                val += f" (expr={p.expr})"
            print(f"  {pname} = {val}")

# Check if support text generators exist and their params
for name in ['text_batter_support', 'text_pitcher_support']:
    t = scene.op(name)
    if t:
        print(f"\n{name} exists: {t.path}")
        print(f"  resolution: {t.par.resolutionw}x{t.par.resolutionh}")
        for pname in ['fontsizey', 'fontsizeyunit', 'font', 'aligny', 'alignx',
                       'linespacing', 'antialiasing']:
            p = getattr(t.par, pname, None)
            if p is not None:
                val = str(p)
                if hasattr(p, 'menuIndex'):
                    val += f" (menuIndex={p.menuIndex})"
                print(f"  {pname} = {val}")
    else:
        print(f"\n{name}: NOT FOUND")

print("--- End Font Diagnosis ---")
