# diagnose_scene1.py
# Run this in TD Textport to check the state of SCENE_1 shader and GLSL errors.

def diagnose():
    scene = op('/AudioLinkLight_V01/SCENE_1')
    if not scene:
        print("SCENE_1 not found!")
        return

    print("="*60)
    print("[SCENE_1 DIAGNOSIS]")
    print("="*60)

    # 1. Check shader_code content
    shader = scene.op('shader_code')
    if shader:
        text = shader.text
        print(f"\n[shader_code] Length: {len(text)} chars")
        # Check if rain code exists
        if 'Cyber Rain' in text or 'データストリーム' in text:
            print("  ✓ Data stream (rain) code FOUND in shader")
        else:
            print("  ✗ Data stream code NOT found in shader!")
        if 'rainVirtualH' in text:
            print("  ✓ rainVirtualH variable FOUND (updated version)")
        else:
            print("  ✗ rainVirtualH NOT found (old version?)")
        # Show first 200 chars of the main() function
        idx = text.find('void main()')
        if idx >= 0:
            print(f"  main() starts at char {idx}")
            print(f"  Preview: {text[idx:idx+200]}...")
    else:
        print("  [ERROR] shader_code Text DAT not found!")

    # 2. Check GLSL TOP
    glsl = scene.op('glsl_clock')
    if glsl:
        print(f"\n[glsl_clock] Resolution: {glsl.width}x{glsl.height}")
        print(f"  pixeldat: {glsl.par.pixeldat.val}")
        
        # Check info DAT for compile errors
        info = scene.op('glsl_clock_info')
        if info:
            print(f"  [Info DAT] {info.text[:500]}")
        
        # Check if there are warnings or errors
        if hasattr(glsl, 'warnings'):
            print(f"  Warnings: {glsl.warnings()}")
        if hasattr(glsl, 'errors'):
            print(f"  Errors: {glsl.errors()}")

    # 3. List all nodes
    print(f"\n[All nodes in SCENE_1]")
    for o in scene.children:
        conn_info = ""
        if hasattr(o, 'inputConnectors'):
            inputs = []
            for c in o.inputConnectors:
                for conn in c.connections:
                    inputs.append(conn.owner.name)
            if inputs:
                conn_info = f" <-- {', '.join(inputs)}"
        print(f"  [{o.type}] {o.name} ({o.width if hasattr(o,'width') else '?'}x{o.height if hasattr(o,'height') else '?'}){conn_info}")

    print("="*60)

diagnose()
