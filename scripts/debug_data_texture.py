# debug_data_texture.py
# Investigate what data_texture actually is
scene = op('/AudioLinkLight_V01/SCENE_6')
if not scene: scene = op('SCENE_6')

dt = scene.op('data_texture')
if not dt:
    print("data_texture NOT FOUND")
else:
    print(f"=== data_texture ===")
    print(f"  Type: {type(dt).__name__}")
    print(f"  OPType: {dt.OPType}")
    print(f"  Family: {dt.family}")
    print(f"  Path: {dt.path}")
    print(f"  Resolution: {dt.width}x{dt.height}")
    print(f"  Inputs: {[str(i) for i in dt.inputs]}")
    
    # Check common parameters
    for pname in ['outputresolution', 'resolutionw', 'resolutionh',
                   'filter', 'inputfiltertype', 'inputfilter',
                   'format', 'cook', 'dat', 'file',
                   'interpolate', 'extend',
                   'top', 'chop', 'script', 'text',
                   'fillmode', 'bgcolorr', 'bgcolorg', 'bgcolorb']:
        p = getattr(dt.par, pname, None)
        if p is not None:
            val = str(p)
            if hasattr(p, 'menuIndex'): val += f" (menuIndex={p.menuIndex})"
            print(f"  {pname} = {val}")

    # Check the chain from text_generator to data_texture
    print(f"\n=== Tracing path: text_generator -> ... -> data_texture ===")
    current = dt
    depth = 0
    while current and depth < 10:
        inputs = current.inputs
        if not inputs: break
        inp = inputs[0]
        print(f"  <- {inp.name} (type={type(inp).__name__}, OPType={inp.OPType}, res={inp.width}x{inp.height})")
        current = inp
        depth += 1
