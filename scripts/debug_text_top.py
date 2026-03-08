# debug_text_top.py
import td
from td import textTOP

scene_path = '/AudioLinkLight_V01/SCENE_6'
scene = op(scene_path)
if not scene: scene = op('SCENE_6')

print(f"--- Diagnostic for Text TOP in {scene.path} ---")
gen = scene.op('text_generator')
if gen:
    print(f"Parameters for {gen.name}:")
    for p in gen.pars():
        if any(x in p.name.lower() for x in ['text', 'font', 'size', 'align']):
            print(f"  {p.name}: {p.label} (Value: {p.val})")
    
    print(f"Text length: {len(gen.par.text)}")
    print(f"Text snippet: {gen.par.text[:50]}...")
else:
    print("text_generator not found!")

# Also debug the parser result
def parse_narrative(filepath):
    main_msgs = [""] * 16
    batter_msgs = [""] * 16
    pitcher_msgs = [""] * 16
    current_section = "main"
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'): continue
                if 'STRETCHERS(Batter)' in line: current_section = "batter"
                elif 'FLEXIBLES(Pitcher)' in line: current_section = "pitcher"
                if ':' in line:
                    parts = line.split(':', 1)
                    try:
                        idx = int(parts[0].strip())
                        msg = parts[1].strip()
                        if idx < 16:
                            if current_section == "main": main_msgs[idx] = msg
                            elif current_section == "batter": batter_msgs[idx] = msg
                            elif current_section == "pitcher": pitcher_msgs[idx] = msg
                    except ValueError: pass
    except Exception as e:
        print(f"Parse Error: {e}")
    return main_msgs, batter_msgs, pitcher_msgs

narrative_path = project.folder + '/scripts/baseball_narrative.md'
m, b, p = parse_narrative(narrative_path)
print(f"--- Parser Result ---")
print(f"Main count: {len([x for x in m if x])}")
print(f"Batter count: {len([x for x in b if x])}")
print(f"Pitcher count: {len([x for x in p if x])}")
if b: print(f"Sample Batter[0]: {b[0]}")
