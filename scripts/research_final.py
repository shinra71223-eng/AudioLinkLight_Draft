# research_final.py
def research():
    root = op('/AudioLinkLight_V01') or op('/')
    print("\n" + "="*50)
    print("[FINAL RESEARCH] Target: Text DAT & GLSL TOP")
    print("="*50)
    
    # 1. Text DAT Inspection
    print("\n--- Text DAT ---")
    t = root.create(textDAT, 'tmp_text')
    t_pars = {p.name: p.label for p in t.pars()}
    for k in ['file', 'syncfile', 'loadonstart', 'read', 'write', 'refresh']:
        if k in t_pars:
            print(f"  {k:15s} : FOUND ({t_pars[k]})")
        else:
            print(f"  {k:15s} : Not found")
    t.destroy()

    # 2. GLSL TOP Uniforms Inspection
    print("\n--- GLSL TOP Uniforms ---")
    g = root.create(glslTOP, 'tmp_glsl')
    # Try to find where 'uTime' should go
    g_pars = [p.name for p in g.pars()]
    
    # Check if vec0name exists (as seen in previous list)
    if 'vec0name' in g_pars:
        print("  Found 'vec0name'. Checking component count...")
        # Check how many components vec0 has
        for suffix in ['x', 'y', 'z', 'w']:
            if f'vec0value{suffix}' in g_pars:
                print(f"    - vec0value{suffix} exists")
    
    # Some versions use 'float0name' instead of 'uniname' or 'vec'
    for prefix in ['float', 'uniname', 'val', 'u']:
        found = [p for p in g_pars if p.startswith(prefix)]
        if found:
            print(f"  Found potential uniform prefix '{prefix}': {found[:3]}...")

    g.destroy()
    print("\n" + "="*50)
    print("[DONE] Please copy the output above.")

if __name__ == '__main__':
    research()
