# inspect_parse_scripts.py
import os

CORE_PATH = '/AudioLinkLight_V01/AudioLinkCore'
core = op(CORE_PATH)

if core:
    print("="*60)
    print("INSPECTING PARSE SCRIPTS")
    print("="*60)
    
    # We look for scripts inside or attached to the parse components
    # Based on the screenshot, they are components with internal scripts
    targets = ['parse_kick', 'parse_snare', 'parse_bass', 'parse_vocal', 'parse_melody']
    
    for name in targets:
        comp = core.op(name)
        if comp:
            print(f"\n[Component] {name}")
            # List internal DATs that look like scripts
            scripts = comp.findChildren(type=dat, depth=2)
            for s in scripts:
                if 'callback' in s.name.lower() or 'script' in s.name.lower() or s.name.startswith('parse'):
                    print(f"  Script Found: {s.name}")
                    # Print first 20 lines to understand the logic
                    lines = s.text.splitlines()[:20]
                    for i, l in enumerate(lines):
                        print(f"    {i+1:2}: {l}")
        else:
            print(f"\n[Component] {name} NOT FOUND")
    
    print("\n" + "="*60)
else:
    print("AudioLinkCore not found")
