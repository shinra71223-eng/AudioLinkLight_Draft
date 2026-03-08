# debug_narrative_table.py
scene = op('/AudioLinkLight_V01/SCENE_6')
if not scene: scene = op('SCENE_6')

nt = scene.op('narrative_table')
if nt:
    print(f"narrative_table type: {type(nt).__name__}, OPType: {nt.OPType}")
    print(f"  numRows: {nt.numRows}, numCols: {nt.numCols}")
    # Show first 3 rows, first 10 cols
    for r in range(min(3, nt.numRows)):
        vals = [str(nt[r, c]) for c in range(min(10, nt.numCols))]
        print(f"  Row {r}: {vals}")
else:
    print("narrative_table NOT FOUND")

# Check if our batter table was created correctly
ntb = scene.op('narrative_table_batter')
if ntb:
    print(f"\nnarrative_table_batter type: {type(ntb).__name__}, OPType: {ntb.OPType}")
    print(f"  numRows: {ntb.numRows}, numCols: {ntb.numCols}")
    print(f"  First 80 chars: {ntb.text[:80]}")
else:
    print("\nnarrative_table_batter NOT FOUND")

# Check data_texture_batter errors
dtb = scene.op('data_texture_batter')
if dtb:
    print(f"\ndata_texture_batter: {dtb.width}x{dtb.height}")
    print(f"  warnings: {dtb.warnings()}")
    print(f"  errors: {dtb.errors()}")
