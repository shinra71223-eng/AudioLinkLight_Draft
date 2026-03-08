# research_scene6.py
# ================================================================
# Comprehensive diagnostic for Scene 6 issues
# ================================================================

def research():
    root = op('/AudioLinkLight_V01')
    if not root:
        print("[ERROR] Root not found")
        return
    
    s6 = root.op('SCENE_6')
    if not s6:
        print("[ERROR] SCENE_6 not found")
        return
    
    print("\n" + "="*60)
    print("[DIAG] SCENE_6 Current State")
    print("="*60)
    
    # 1. List all children
    print("\n--- Children of SCENE_6 ---")
    for c in s6.children:
        print(f"  {c.name:20s} type={c.type:15s} errors={c.errors()[:80] if c.errors() else 'None'}")
    
    # 2. Check GLSL TOP errors specifically
    glsl = s6.op('glsl_baseball')
    if glsl:
        print(f"\n--- GLSL TOP Details ---")
        print(f"  pixeldat = {glsl.par.pixeldat.val if hasattr(glsl.par, 'pixeldat') else 'N/A'}")
        print(f"  errors   = {glsl.errors()}")
        print(f"  warnings = {glsl.warnings()}")
        # Check if shader is loaded
        sd = s6.op('shader_code')
        if sd:
            txt = sd.text
            print(f"  shader_code lines = {len(txt.splitlines()) if txt else 0}")
            print(f"  shader_code first 100 chars = {txt[:100] if txt else 'EMPTY'}")
    
    # 3. Check scene_out connections
    out = s6.op('scene_out')
    if out:
        conns = out.inputConnectors
        print(f"\n--- scene_out ---")
        print(f"  # of input connectors = {len(conns)}")
        for i, c in enumerate(conns):
            print(f"    [{i}] connections = {[cn.owner.name for cn in c.connections] if c.connections else 'EMPTY'}")
    
    # 4. Research Text TOP for alternative approach
    print("\n--- Text TOP Research ---")
    tmp_text = root.create(textTOP, 'tmp_text_top')
    print("  Created textTOP. Parameters:")
    
    # Look for font-related params
    keywords = ['font', 'text', 'string', 'size', 'bold', 'italic', 'align', 'resolution', 'dat']
    found_pars = []
    for p in tmp_text.pars():
        for kw in keywords:
            if kw in p.name.lower() or kw in p.label.lower():
                found_pars.append(p)
                break
    
    for p in sorted(found_pars, key=lambda x: x.name):
        val = ''
        try: val = p.val
        except: val = '?'
        print(f"    {p.name:25s} | {p.label:20s} = {val}")
    
    tmp_text.destroy()
    
    print("\n" + "="*60)
    print("[DONE] Please copy this output.")

if __name__ == '__main__':
    research()
