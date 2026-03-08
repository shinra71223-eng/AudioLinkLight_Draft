# inspect_scene5_final.py
SCENE_PATH = '/AudioLinkLight_V01/SCENE_5'
scene = op(SCENE_PATH)

if scene:
    print("="*80)
    print(f"SCENE_5 DEFINITIVE INSPECTION (Resolution & Connectivity)")
    print("="*80)
    
    nodes = sorted(scene.children, key=lambda x: x.nodeX)
    
    for o in nodes:
        conn_in = [f"In[{i}]: {o.inputs[i].name if o.inputs[i] else 'None'}" for i in range(len(o.inputs))]
        print(f"[{o.type:10}] {o.name:20} | Res: {o.width:3}x{o.height:3} | {', '.join(conn_in)}")
        
        # Check specific parameters for the "flat" issue
        if o.type == 'level':
            print(f"    -> Opacity: {o.par.opacity.val:.3f}, Brightness: {o.par.brightness1.val:.3f}")
        if o.type == 'composite':
            print(f"    -> Operation: {o.par.operand.val}")
        if o.type == 'feedback':
            print(f"    -> Target: {o.par.top.val}")
            
    print("\n" + "="*80)
else:
    print(f"SCENE_5 not found at {SCENE_PATH}")
