# test_parser_output.py


NARRATIVE_FILE = project.folder + '/scripts/baseball_narrative.md'

with open(NARRATIVE_FILE, 'r', encoding='utf-8') as f:
    text = f.read()

print("File first 200 chars:")
print(text[:200])

print("\nSearching for STRETCHERS(Batter):")
idx = text.find("STRETCHERS(Batter)")
if idx >= 0:
    print(text[idx:idx+150])

print("\nChecking Table:")
scene = op('/AudioLinkLight_V01/SCENE_6')
if not scene: scene = op('SCENE_6')

tbl_b = scene.op('narrative_table_batter')
if tbl_b:
    print(f"Table locked? {tbl_b.lock}")
    if tbl_b.numRows > 0:
        chars = []
        for c in range(min(20, tbl_b.numCols)):
            try: chars.append(chr(int(tbl_b[0, c].val)))
            except: pass
        print(f"Table row 0: {''.join(chars)}")
