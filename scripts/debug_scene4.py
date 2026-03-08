# debug_scene4.py
import td

def debug_scene(path):
    scene = op(path)
    if not scene:
        print(f"Error: {path} not found")
        return

    print("="*60)
    print(f"DEBUG REPORT: {path}")
    print("="*60)

    for o in scene.children:
        print(f"\n[{o.type}] {o.name}")
        # Connections
        inputs = [c.owner.name for c in o.inputConnectors if c.connections]
        if inputs: print(f"  Inputs: {', '.join(inputs)}")
        
        # Parameters of interest
        params = ['operand', 'size', 'direction', 'amp', 'offset', 'type', 'mono', 'justifyh', 'justifyv', 'centerx', 'centery', 'bgalpha']
        for p_name in params:
            if hasattr(o.par, p_name):
                p = getattr(o.par, p_name)
                print(f"  par.{p_name}: {p.val} (expr: {p.expr})")
        
        if o.type == 'composite':
            print(f"  TOPs: {o.par.TOPs.val}")

debug_scene('/AudioLinkLight_V01/SCENE_4')
