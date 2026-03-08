# inspect_scene5_deep.py
SCENE_PATH = '/AudioLinkLight_V01/SCENE_5'
scene = op(SCENE_PATH)

def log_par(o, p_name):
    if hasattr(o.par, p_name):
        print(f"    {p_name}: {getattr(o.par, p_name).val} (expr: {getattr(o.par, p_name).expr})")

if scene:
    print("="*60)
    print(f"DEEP INSPECTION: {SCENE_PATH}")
    print("="*60)
    for o in scene.children:
        print(f"\n[{o.type}] {o.name}")
        print(f"  Resolution: {o.width}x{o.height}")
        log_par(o, 'outputresolution')
        log_par(o, 'resolutionw')
        log_par(o, 'resolutionh')
        
        if o.type == 'noise':
            log_par(o, 'type')
            log_par(o, 'amp')
            log_par(o, 'period')
        elif o.type == 'feedback':
            log_par(o, 'top')
        elif o.type == 'transform':
            log_par(o, 'sx')
            log_par(o, 'sy')
            log_par(o, 'rz')
        elif o.type == 'level':
            log_par(o, 'opacity')
            log_par(o, 'brightness1')
            log_par(o, 'gamma1')
        elif o.type == 'composite':
            log_par(o, 'operand')
            print(f"    Inputs: {[i.owner.name for i in o.inputs]}")
    print("\n" + "="*60)
else:
    print(f"SCENE_5 not found at {SCENE_PATH}")
