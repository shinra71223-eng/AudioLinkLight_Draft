# debug_data_flow.py
scene = op('/AudioLinkLight_V01/SCENE_6')
if not scene: scene = op('SCENE_6')

print("="*60)
print("CHECKING DATA FLOW FOR SUPPORT MESSAGES")
print("="*60)

# Check the Batter Table
tbl_b = scene.op('narrative_table_batter')
if tbl_b:
    print(f"\n--- narrative_table_batter ---")
    print(f"NumRows: {tbl_b.numRows}")
    # Decode first row to string
    if tbl_b.numRows > 0:
        chars = []
        for c in range(min(50, tbl_b.numCols)):
            val = tbl_b[0, c].val
            try:
                char_code = int(val)
                if char_code > 0: chars.append(chr(char_code))
            except: pass
        print(f"Row 0 decoded text: {''.join(chars)}")
else:
    print("narrative_table_batter not found")

# Check the Batter Script TOP
dt_b = scene.op('data_texture_batter')
if dt_b:
    print(f"\n--- data_texture_batter (Script TOP) ---")
    print(f"Path: {dt_b.path}")
    print(f"Resolution: {dt_b.width}x{dt_b.height}")
    print(f"Is cooking: {dt_b.isCooking}")
    
    # Let's manually trigger a cook to see if it updates
    try:
        dt_b.cook(force=True)
        print("Forced cook executed.")
    except Exception as e:
        print(f"Cook error: {e}")
        
    # Check if there's any text TOP lying around that might be overriding things
    txt_b = scene.op('text_batter_support')
    if txt_b:
        print(f"\nWARNING: text_batter_support (Text TOP) exists!")
        print(f"Text content: {txt_b.par.text.eval()[:50]}...")
else:
    print("data_texture_batter not found")

# Check what the GLSL is ACTUALLY connected to
glsl_b = scene.op('glsl_batter_support')
if glsl_b:
    print(f"\n--- glsl_batter_support ---")
    inputs = glsl_b.inputs
    if inputs:
        print(f"Input 0 is connected to: {inputs[0].path} (Type: {type(inputs[0]).__name__})")
        if inputs[0].name != 'data_texture_batter':
            print(">>> ERROR: GLSL is NOT connected to the Script TOP!")
    else:
        print(">>> ERROR: GLSL has no inputs connected!")
else:
    print("glsl_batter_support not found")
