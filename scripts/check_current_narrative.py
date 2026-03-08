# check_current_narrative.py
import td

# Paths
root_path = '/AudioLinkLight_V01'
scene_path = f'{root_path}/SCENE_6'
tbl = op(f'{scene_path}/narrative_table')
glsl = op(f'{scene_path}/glsl_baseball')

print("=== Scene 6 Narrative Diagnosis ===")

if not tbl:
    print(f"Error: narrative_table not found at {scene_path}")
else:
    print(f"Table Rows: {tbl.numRows}")
    print("--- Table Content (First 40 chars per state) ---")
    for r in range(tbl.numRows):
        # Convert ASCII codes back to characters
        chars = []
        for c in range(tbl.numCols):
            val = int(tbl[r, c])
            if val == 0: break
            chars.append(chr(val))
        text = "".join(chars)
        print(f"State {r}: {text[:60]}{'...' if len(text) > 60 else ''}")

if not glsl:
    print(f"Error: glsl_baseball not found at {scene_path}")
else:
    uIdx = glsl.par.value1x.eval()
    uTime = glsl.par.value2x.eval()
    print(f"\n--- Current GLSL State ---")
    print(f"uPitchIndex (Current State): {uIdx}")
    print(f"uPitchTime (Seconds in state): {uTime:.2f}s")
    
    # Identify which text should be showing
    if tbl and 0 <= int(uIdx) < tbl.numRows:
        active_chars = []
        for c in range(tbl.numCols):
            val = int(tbl[int(uIdx), c])
            if val == 0: break
            active_chars.append(chr(val))
        print(f"Active Text: {''.join(active_chars)}")
    else:
        print("Active Text: (Index out of range or table empty)")

print("====================================")
