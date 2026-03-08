# debug_glsl_params.py
# Compare ALL parameters between working glsl_baseball and broken support GLSLs
scene = op('/AudioLinkLight_V01/SCENE_6')
if not scene: scene = op('SCENE_6')

print("="*60)
print("FULL PARAMETER COMPARISON: Main vs Support GLSLs")
print("="*60)

# Important GLSL TOP parameters to check
params_to_check = [
    'outputresolution', 'resolutionw', 'resolutionh',
    'format', 'filter', 'inputfiltertype', 'inputfilter',
    'inputsmoothtype', 'inputsmooth', 'inputextend',
    'inputextendx', 'inputextendy', 'inputextendz',
    'pixeldat', 'computedat',
    'vec0name', 'vec0valuex', 'vec0valuey',
    'vec1name', 'vec1valuex',
    'vec2name', 'vec2valuex', 'vec2valuey', 'vec2valuez',
    'vec3name', 'vec3valuex',
]

nodes = ['glsl_baseball', 'glsl_batter_support', 'glsl_pitcher_support']

for nname in nodes:
    n = scene.op(nname)
    if not n:
        print(f"\n{nname}: NOT FOUND")
        continue
    print(f"\n--- {nname} ---")
    print(f"  Path: {n.path}")
    print(f"  Inputs: {[str(i) for i in n.inputs]}")
    for pname in params_to_check:
        p = getattr(n.par, pname, None)
        if p is not None:
            val = str(p)
            extras = []
            if hasattr(p, 'menuIndex'):
                extras.append(f"menuIndex={p.menuIndex}")
            if hasattr(p, 'expr') and p.expr:
                extras.append(f"expr={p.expr}")
            if extras:
                val += f" ({', '.join(extras)})"
            print(f"  {pname} = {val}")

# Also check text generators
print("\n--- TEXT GENERATOR COMPARISON ---")
for tname in ['text_generator', 'text_batter_support', 'text_pitcher_support']:
    t = scene.op(tname)
    if not t:
        print(f"\n{tname}: NOT FOUND")
        continue
    print(f"\n{tname}:")
    print(f"  resolution: {t.par.resolutionw}x{t.par.resolutionh}")
    # Get first 80 chars of text
    txt = str(t.par.text)[:80]
    print(f"  text (first 80): {txt}")
    for pname in ['fontsizey', 'fontsizeyunit', 'fontsizex', 'fontsizexunit',
                   'font', 'bold', 'aligny', 'alignx', 'linespacing',
                   'linespacingunit', 'antialiasing', 'filter', 'inputfilter']:
        p = getattr(t.par, pname, None)
        if p is not None:
            val = str(p)
            if hasattr(p, 'menuIndex'):
                val += f" (menuIndex={p.menuIndex})"
            print(f"  {pname} = {val}")

print("\n" + "="*60)
