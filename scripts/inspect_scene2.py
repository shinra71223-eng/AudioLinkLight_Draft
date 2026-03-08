# inspect_scene2.py
SCENE_PATH = '/AudioLinkLight_V01/SCENE_2'
scene = op(SCENE_PATH)

if scene:
    print("="*60)
    print(f"NODES IN {SCENE_PATH}")
    print("-" * 60)
    for o in scene.children:
        res = f"{o.width}x{o.height}" if hasattr(o, 'width') else "N/A"
        out_res = "N/A"
        if hasattr(o.par, 'outputresolution'):
            out_res = o.par.outputresolution.val
        
        inputs = []
        if hasattr(o, 'inputConnectors'):
            for c in o.inputConnectors:
                for conn in c.connections:
                    inputs.append(conn.owner.name)
        conn_str = f" <-- {', '.join(inputs)}" if inputs else ""
        
        print(f"[{o.type}] {o.name:15} | Res: {res:8} | OutResMode: {out_res:10}{conn_str}")
    print("="*60)
else:
    print(f"SCENE_2 not found at {SCENE_PATH}")
