# research_glsl.py
def research():
    root = op('/AudioLinkLight_V01') or op('/')
    print("\n[RESEARCH] Investigating GLSL TOP parameters...")
    tmp = root.create(glslTOP, 'tmp_glsl_research')
    
    # Check for likely candidates for pixel shader file
    candidates = ['file', 'pixelfile', 'pixelFile', 'pixelshader', 'pixel']
    print("Checking specific candidates:")
    for c in candidates:
        has = hasattr(tmp.par, c)
        print(f"  {c:15s} : {'FOUND' if has else 'Not found'}")
        
    print("\nAll available parameters (name | label):")
    pars = tmp.pars()
    pars.sort(key=lambda p: p.name)
    for p in pars:
        print(f"  {p.name:20s} | {p.label}")
        
    tmp.destroy()
    print("\n[DONE] Please copy this output.")

if __name__ == '__main__':
    research()
