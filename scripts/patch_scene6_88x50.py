# patch_scene6_88x50.py
# ================================================================
# DEFINITIVE FIX: Use the SAME bitmap font system (font_8x8.bin)
# for both main AND support messages via Script TOPs.
#
# Root Cause: glsl_baseball reads from data_texture (Script TOP)
# which uses font_8x8.bin for pixel-perfect 8x8 rendering.
# Support GLSLs were reading from TD's Text TOPs (different system).
# ================================================================
import td
from td import glslTOP, textTOP, textDAT, scriptTOP, compositeTOP
import os

SCENE_PATH = '/AudioLinkLight_V01/SCENE_6'
NARRATIVE_FILE = project.folder + '/scripts/baseball_narrative.md'
SUPP_GLSL_FILE = project.folder + '/scripts/baseball_support.glsl'
FONT_FILE = project.folder + '/scripts/font_8x8.bin'

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
                if 'STRETCHERS(Batter)' in line: current_section = "batter"; continue
                elif 'FLEXIBLES(Pitcher)' in line: current_section = "pitcher"; continue
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
        print(f"  Error reading narrative: {e}")
    for i in range(16):
        if not main_msgs[i]: main_msgs[i] = " "
        if not batter_msgs[i]: batter_msgs[i] = "Go! Go!"
        if not pitcher_msgs[i]: pitcher_msgs[i] = "Fight!"
    return main_msgs, batter_msgs, pitcher_msgs

def create_narrative_table(scene, name, msgs):
    """Create a Table DAT with ASCII character codes (same format as narrative_table)"""
    from td import tableDAT
    tbl = scene.op(name)
    if not tbl: tbl = scene.create(tableDAT, name)
    tbl.clear()
    for msg in msgs:
        row_data = []
        for col_idx in range(256):
            if col_idx < len(msg):
                row_data.append(str(ord(msg[col_idx])))
            else:
                row_data.append('0')
        tbl.appendRow(row_data)
    print(f"  {name}: {tbl.numRows}x{tbl.numCols} Table DAT")
    return tbl

def create_support_script_top(scene, name, table_name):
    """Create a Script TOP that renders text using font_8x8.bin (same as data_texture)"""
    # Callback script
    cb_name = name + '_callbacks'
    cb = scene.op(cb_name)
    if not cb: cb = scene.create(textDAT, cb_name)
    
    cb.text = f'''import numpy as np
_f_cells = None

def onCook(scriptOp):
    global _f_cells
    if _f_cells is None:
        try:
            with open('{FONT_FILE.replace(chr(92), "/")}', 'rb') as f:
                raw = f.read()
                raw_arr = np.frombuffer(raw, dtype=np.uint8).reshape(8, 256, 8)
                _f_cells = np.flip(raw_arr, axis=0).transpose(1, 0, 2).copy()
        except: pass

    tbl = op('{table_name}')
    arr = np.zeros((128, 2048, 1), dtype=np.uint8)

    if tbl and _f_cells is not None:
        for state_row in range(min(tbl.numRows, 16)):
            for char_col in range(min(tbl.numCols, 256)):
                try:
                    char_code = int(tbl[state_row, char_col])
                    if char_code == 0: continue
                    dst_x, dst_y = char_col * 8, state_row * 8
                    arr[dst_y:dst_y+8, dst_x:dst_x+8, 0] = _f_cells[char_code]
                except: pass

    try:
        if hasattr(scriptOp, 'copyNumpyArray'):
            scriptOp.copyNumpyArray(np.ascontiguousarray(arr))
    except Exception as e:
        print("Support atlas cook error: " + str(e))
'''

    # Script TOP
    st = scene.op(name)
    if not st: st = scene.create(scriptTOP, name)
    st.par.outputresolution.menuIndex = 9  # custom
    st.par.resolutionw = 2048
    st.par.resolutionh = 128
    st.par.inputfiltertype.menuIndex = 0  # nearest
    st.par.fillmode.menuIndex = 4  # best
    if hasattr(st.par, 'script'): st.par.script = cb
    
    # Force cook
    st.cook(force=True)
    print(f"  {name}: Script TOP (2048x128, nearest, font_8x8.bin)")
    return st

def patch():
    scene = op(SCENE_PATH)
    if not scene: scene = op('SCENE_6')
    if not scene:
        print(f"Error: SCENE_6 not found."); return

    print("="*60)
    print(f"PATCHING SCENE_6 (BITMAP FONT FIX): {scene.path}")
    print("="*60)

    # Detect expressions
    glsl_main = scene.op('glsl_baseball')
    stateframe_expr = "absTime.frame % 900"
    pitchindex_expr = "int((absTime.frame % 8100) / 900)"
    if glsl_main:
        for i in range(7):
            vname = getattr(glsl_main.par, f'vec{i}name', None)
            if vname:
                vn = str(vname)
                if 'StateFrame' in vn or 'stateframe' in vn.lower():
                    vexpr = getattr(glsl_main.par, f'vec{i}valuex', None)
                    if vexpr and hasattr(vexpr, 'expr') and vexpr.expr:
                        stateframe_expr = vexpr.expr
                if 'PitchIndex' in vn or 'pitchindex' in vn.lower():
                    vexpr = getattr(glsl_main.par, f'vec{i}valuex', None)
                    if vexpr and hasattr(vexpr, 'expr') and vexpr.expr:
                        pitchindex_expr = vexpr.expr

    # 1. Parse narrative
    m_msgs, b_msgs, p_msgs = parse_narrative(NARRATIVE_FILE)
    print(f"  Parsed {len(m_msgs)} main, {len(b_msgs)} batter, {len(p_msgs)} pitcher")

    # 2. Create Table DATs for support messages (same format as narrative_table)
    tbl_b = create_narrative_table(scene, 'narrative_table_batter', b_msgs)
    tbl_p = create_narrative_table(scene, 'narrative_table_pitcher', p_msgs)

    # 3. Create Script TOPs (same system as data_texture)
    dt_b = create_support_script_top(scene, 'data_texture_batter', tbl_b.path)
    dt_p = create_support_script_top(scene, 'data_texture_pitcher', tbl_p.path)

    # 4. Support GLSLs → connect to Script TOPs (NOT Text TOPs)
    with open(SUPP_GLSL_FILE, 'r', encoding='utf-8') as f:
        supp_code = f.read()

    def setup_supp(name, direction, color, data_src):
        g = scene.op(name)
        if not g: g = scene.create(glslTOP, name)
        code_dat = scene.op(name + '_code')
        if not code_dat: code_dat = scene.create(textDAT, name + '_code')
        code_dat.text = supp_code
        g.par.pixeldat = ""; g.par.pixeldat = code_dat
        # Connect to Script TOP (bitmap font), NOT Text TOP
        g.inputConnectors[0].connect(data_src)
        
        g.par.vec0name = 'uStateFrame'; g.par.vec0valuex.expr = stateframe_expr
        g.par.vec1name = 'uDirection'; g.par.vec1valuex = float(direction)
        g.par.vec2name = 'uColor'
        g.par.vec2valuex = color[0]; g.par.vec2valuey = color[1]; g.par.vec2valuez = color[2]
        g.par.vec3name = 'uPitchIndex'; g.par.vec3valuex.expr = pitchindex_expr
        
        g.par.outputresolution.menuIndex = 9
        g.par.resolutionw = 88; g.par.resolutionh = 50
        g.par.format.menuIndex = 4
        g.par.inputfiltertype.menuIndex = 0  # nearest
        print(f"  {name} → {data_src.name} (dir={direction}, nearest)")
        return g

    glsl_p = setup_supp('glsl_pitcher_support', 1.0, (0.2, 0.4, 1.0), dt_p)
    glsl_b = setup_supp('glsl_batter_support', -1.0, (1.0, 0.1, 0.1), dt_b)

    # 5. Composite
    comp = scene.op('comp_layers')
    if not comp: comp = scene.create(compositeTOP, 'comp_layers')
    if comp:
        comp.par.operand = 0
        comp.par.resolutionw = 88; comp.par.resolutionh = 50
        comp.par.outputresolution.menuIndex = 9
        
        layers = [glsl_main, glsl_b, glsl_p]
        for i, lyr in enumerate(layers):
            if lyr:
                try: comp.inputConnectors[i].connect(lyr)
                except: pass
        
        out = scene.op('scene_out')
        if out: out.inputConnectors[0].connect(comp)

    print("="*60)
    print("SCENE_6 PATCH COMPLETE (BITMAP FONT - PIXEL PERFECT)")
    print("="*60)

patch()
