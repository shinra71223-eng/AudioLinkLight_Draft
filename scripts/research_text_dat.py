# research_text_dat.py
def research():
    root = op('/AudioLinkLight_V01') or op('/')
    print("\n[RESEARCH] Investigating Text DAT parameters...")
    tmp = root.create(textDAT, 'tmp_text_research')
    
    candidates = ['file', 'syncfile', 'loadonstart', 'read', 'write']
    for c in candidates:
        print(f"  {c:15s} : {'FOUND' if hasattr(tmp.par, c) else 'Not found'}")
        
    print("\nAll available parameters (name | label):")
    for p in sorted(tmp.pars(), key=lambda x: x.name):
        print(f"  {p.name:20s} | {p.label}")
        
    tmp.destroy()
    print("\n[DONE]")

if __name__ == '__main__':
    research()
