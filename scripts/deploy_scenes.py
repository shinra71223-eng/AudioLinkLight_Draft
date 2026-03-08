import td
import math
import os

# ─────────────────────────────────────────────────────────────────
# Robust Operator Creation & Script Helpers
# ─────────────────────────────────────────────────────────────────
def _create_op(parent, type_name, name):
    """
    環境によって 'select' か 'selectTOP' かなどの仕様が異なるため、
    複数のバリエーションを試行して演算子を作成する。
    """
    # 1. 既存の同名演算子があれば消去してクリーンに
    existing = parent.op(name)
    if existing: 
        try: existing.destroy()
        except: pass

    # 2. 試行するタイプリスト
    # type_name が 'select' なら 'selectTOP', 'selectDAT' など
    base = type_name.replace('TOP','').replace('DAT','').replace('CHOP','').replace('COMP','')
    
    variants = [
        type_name,
        base + 'TOP',
        base + 'DAT',
        base + 'CHOP',
        base + 'COMP',
        type_name.lower(),
        type_name + 'TOP',
        type_name + 'DAT'
    ]
    
    # 重複削除
    checked = []
    for v in variants:
        if v not in checked: checked.append(v)

    # 3. 試行回数
    for v in checked:
        try:
            return parent.create(v, name)
        except:
            continue
            
    # 4. クラスオブジェクトでの試行（念のため）
    try:
        if hasattr(td, type_name):
            cls = getattr(td, type_name)
            if not isinstance(cls, str):
                return parent.create(cls, name)
    except: pass
                
    raise Exception(f"FAILED to create op '{name}' with type '{type_name}'. Checked: {checked}")

def _set_script_code(node, code):
    """scriptTOP などのコードを設定する (callbacksパラメータが指すDATに書き込む)"""
    dat = None
    # callbacks または script パラメータが指している DAT を取得
    if hasattr(node.par, 'callbacks'):
        dat = node.par.callbacks.eval()
    elif hasattr(node.par, 'script'):
        dat = node.par.script.eval()
    
    if dat and hasattr(dat, 'text'):
        dat.text = code
    else:
        # パラメータで見つからない場合は、名前規則から推測、または新規作成
        cb_name = node.name + '_script'
        dat = node.parent().op(cb_name) or _create_op(node.parent(), 'textDAT', cb_name)
        dat.text = code
        # パラメータにバインド
        try:
            if hasattr(node.par, 'callbacks'): node.par.callbacks = dat
            elif hasattr(node.par, 'script'): node.par.script = dat
        except: pass

def _create_ui_button(parent):
    """メインネットワークにデプロイ用のUIボタンを作成する"""
    btn_name = 'DEPLOY_SCENES'
    btn = parent.op(btn_name) or _create_op(parent, 'buttonCOMP', btn_name)
    if not btn: 
        print(f"FAILED to create UI Button in {parent.path}")
        return
    
    btn.par.display = 1
    # ボタンタイプを 'Momentary' (0) に設定して確実に発火させる
    if hasattr(btn.par, 'buttontype'): btn.par.buttontype = 0
    
    # 座標設定 (右側の見やすい場所に配置)
    btn.nodeX, btn.nodeY = -2000, 1200 
    if hasattr(btn.par, 'hmode'): btn.par.hmode = 0 # Fixed width
    if hasattr(btn.par, 'vmode'): btn.par.vmode = 0 # Fixed height
    if hasattr(btn.par, 'w'): btn.par.w = 220
    if hasattr(btn.par, 'h'): btn.par.h = 80
    
    # ラベル設定
    for p in ['label', 'Buttonlabel', 'Text', 'Text1']:
        if hasattr(btn.par, p): 
            try: setattr(btn.par, p, "DEPLOY ALL SCENES")
            except: pass
    
    # コールバック設定
    # __file__ は exec 内部では定義されない場合があるため、絶対パスを構築する
    script_path = (PROJECT_FOLDER + '/scripts/deploy_scenes.py').replace('\\', '/')
    cb_code = f"""# DEPLOY_SCENES Callbacks
def onOffToOn(panelValue):
    print(">>> UI Button: Triggering Deployment...")
    project_file = r'{script_path}'
    try:
        if not os.path.exists(project_file):
            print(f"Error: Script not found at {{project_file}}")
            return
        exec(open(project_file, encoding='utf-8').read())
    except Exception as e:
        print("UI Deployment Error: " + str(e))
    return
"""
    _set_script_code(btn, cb_code)
    print(f"    + UI Button READY: {btn.path}")

# ─────────────────────────────────────────────────────────────────
# 定数定義
# ─────────────────────────────────────────────────────────────────
LED_COLS = 88
LED_ROWS = 10
PROJECT_NAME = "AudioLinkLight_V01"
PROJECT_FOLDER = project.folder 
SCENE1_SOURCE = f'/{PROJECT_NAME}/TEST_SCREEN2/cyber_clock_v2'

# ─────────────────────────────────────────────────────────────────
# ヘルパー: Rectangle TOP パラメータ設定
# ─────────────────────────────────────────────────────────────────
def _set_rect_params(rect, size=None, center_expr=None, color=None, dynamic_color=False):
    if hasattr(rect.par, 'sizeunit'): rect.par.sizeunit = 1 
    if hasattr(rect.par, 'centerunit'): rect.par.centerunit = 1
    if hasattr(rect.par, 'bgalpha'): rect.par.bgalpha = 0
    if hasattr(rect.par, 'softness'): rect.par.softness = 0
    if hasattr(rect.par, 'antialias'): rect.par.antialias = 0
    
    for p_name in ['justifyh', 'justifyv']:
        if hasattr(rect.par, p_name):
            try: rect.par[p_name] = 'center'
            except: rect.par[p_name] = 1

    if size:
        if hasattr(rect.par, 'sizex'): rect.par.sizex, rect.par.sizey = size
        elif hasattr(rect.par, 'size'): rect.par.size = size

    if center_expr:
        expr_clean = center_expr.strip('[]')
        parts = expr_clean.split(',')
        if len(parts) == 2:
            if hasattr(rect.par, 'centerx'):
                rect.par.centerx.expr = parts[0].strip()
                rect.par.centery.expr = parts[1].strip()
            elif hasattr(rect.par, 'center'):
                rect.par.center.expr = center_expr

    if dynamic_color:
        if hasattr(rect.par, 'fillcolorr'):
            rect.par.fillcolorr.expr = 'math.sin(absTime.seconds * 0.2 + 0.0) * 0.125 + 0.125'
            rect.par.fillcolorg.expr = 'math.sin(absTime.seconds * 0.2 + 2.0) * 0.125 + 0.125'
            rect.par.fillcolorb.expr = 'math.sin(absTime.seconds * 0.2 + 4.0) * 0.125 + 0.125'
            rect.par.fillalpha = 1
    elif color:
        if hasattr(rect.par, 'fillcolorr'):
            rect.par.fillcolorr, rect.par.fillcolorg, rect.par.fillcolorb, rect.par.fillalpha = color
        elif hasattr(rect.par, 'fillcolor'):
            rect.par.fillcolor = color

# ─────────────────────────────────────────────────────────────────
# シーン構築関数
# ─────────────────────────────────────────────────────────────────

def _build_scene1(scene_base):
    sel = _create_op(scene_base, 'selectTOP', 'scene_source')
    sel.par.top = SCENE1_SOURCE
    out = scene_base.op('scene_out') or _create_op(scene_base, 'nullTOP', 'scene_out')
    out.inputConnectors[0].connect(sel)

def _build_scene2(scene_base):
    pat = _create_op(scene_base, 'noiseTOP', 'pat_noise')
    pat.par.resolutionw, pat.par.resolutionh = LED_COLS, LED_ROWS
    pat.par.type = 'simplex3d'; pat.par.mono = False; pat.par.seed = 150; pat.par.period = 5.0
    if hasattr(pat.par, 'harmon'): pat.par.harmon = 2
    if hasattr(pat.par, 'amp'):    pat.par.amp = 0.4
    if hasattr(pat.par, 'tz'): pat.par.tz.expr = 'absTime.seconds * 0.15'
    out = scene_base.op('scene_out') or _create_op(scene_base, 'nullTOP', 'scene_out')
    out.inputConnectors[0].connect(pat)
    print(f'    + SCENE_2: Liquid Mixing Motion (Restored)')

def _build_scene3(scene_base):
    pat = _create_op(scene_base, 'noiseTOP', 'pat_noise')
    pat.par.resolutionw, pat.par.resolutionh = LED_COLS, LED_ROWS
    pat.par.type = 'simplex3d'; pat.par.mono = False; pat.par.period = 2.5
    if hasattr(pat.par, 'harmon'): pat.par.harmon = 4
    if hasattr(pat.par, 'tz'): pat.par.tz.expr = 'absTime.seconds * 0.6'
    out = scene_base.op('scene_out') or _create_op(scene_base, 'nullTOP', 'scene_out')
    out.inputConnectors[0].connect(pat)
    print(f'    + SCENE_3: Shimmering Plasma Motion (Restored)')

def _build_scene4(scene_base):
    for o in list(scene_base.children):
        if o.name != 'scene_out': o.destroy()
    v_lines = []
    DIM = 0.25 
    v_colors = [[0, DIM, DIM, 1], [DIM, 0, DIM, 1], [DIM, DIM, 0, 1], None]
    for i in range(4):
        rect = _create_op(scene_base, 'rectangleTOP', f'rect_v{i}')
        rect.par.resolutionw, rect.par.resolutionh = LED_COLS, LED_ROWS
        cexp = f'[(math.sin(absTime.seconds * {0.5+i*0.1} + {i*2.0}) * 0.35 + math.sin(absTime.seconds * {0.3+i*0.05} + {i*4.5}) * 0.15), 0.0]'
        _set_rect_params(rect, size=[2.0/88, 1.0], center_expr=cexp, color=v_colors[i], dynamic_color=(i==3))
        v_lines.append(rect)
    comp_v = _create_op(scene_base, 'compositeTOP', 'comp_v')
    if hasattr(comp_v.par, 'operand'): comp_v.par.operand = 'max'
    for i, line in enumerate(v_lines): comp_v.inputConnectors[i].connect(line)
    
    # Shooting stars
    h_lines = []
    star_defs = [(0.6,18,1,-0.35,0,0.0),(2.0,45,-1,-0.15,1,0.3),(1.2,28,1,0.05,2,0.7),(1.5,22,-1,0.25,0,1.1)]
    for i, (spd, length, dir, y, ci, off) in enumerate(star_defs):
        rect = _create_op(scene_base, 'rectangleTOP', f'rect_star{i}')
        rect.par.resolutionw, rect.par.resolutionh = LED_COLS, LED_ROWS
        p_expr = f'((absTime.seconds * {spd} + {off}) % 2.0) / 2.0'
        u_expr = f'(0.3 * {p_expr} + 0.7 * ({p_expr}**2.0))'
        if hasattr(rect.par, 'centerx'): rect.par.centerx.expr = f'({u_expr} * 2.0 - 1.0) * {dir}'
        if hasattr(rect.par, 'centery'): rect.par.centery = y
        if hasattr(rect.par, 'sizex'): rect.par.sizex = length/88.0
        if hasattr(rect.par, 'sizey'): rect.par.sizey = 0.1
        _set_rect_params(rect, color=v_colors[ci % 3])
        h_lines.append(rect)
    comp_h = _create_op(scene_base, 'compositeTOP', 'comp_h')
    if hasattr(comp_h.par, 'operand'): comp_h.par.operand = 'max'
    for i, line in enumerate(h_lines): comp_h.inputConnectors[i].connect(line)
    blur_h = _create_op(scene_base, 'blurTOP', 'blur_tail')
    blur_h.par.size = 20; blur_h.inputConnectors[0].connect(comp_h)
    comp_final = _create_op(scene_base, 'compositeTOP', 'comp_final')
    if hasattr(comp_final.par, 'operand'): comp_final.par.operand = 'add'
    comp_final.inputConnectors[0].connect(comp_v); comp_final.inputConnectors[1].connect(blur_h)
    out = scene_base.op('scene_out') or _create_op(scene_base, 'nullTOP', 'scene_out')
    out.inputConnectors[0].connect(comp_final)
    print(f'    + SCENE_4: Cyberpunk Shooting Star Ready')

def _build_scene5(scene_base):
    out = scene_base.op('scene_out') or _create_op(scene_base, 'nullTOP', 'scene_out')
    print(f'    + SCENE_5: Placeholder Created')

def _build_scene6(scene_base):
    # 1. Shader Code
    shader_dat = _create_op(scene_base, 'textDAT', 'shader_code')
    try:
        with open(PROJECT_FOLDER + '/scripts/baseball_scene.glsl', 'r', encoding='utf-8') as f:
            shader_dat.text = f.read()
    except: shader_dat.text = '// Shader Load Error'

    # 1.1 Narrative Data
    narr_txt = _create_op(scene_base, 'textDAT', 'narrative_data')
    # Use reliable PROJECT_FOLDER for path resolution
    narrative_file = (PROJECT_FOLDER + '/scripts/baseball_narrative.md').replace('\\', '/')
    try:
        with open(narrative_file, 'r', encoding='utf-8') as f:
            narr_txt.text = f.read()
            narr_txt.cook(force=True)
    except Exception as e:
        print(f"Error loading narrative file {narrative_file}: {e}")

    # 1.2 Narrative Table (16 rows)
    # Rows 0-8: Result/display text (before first ':' in val)
    # Rows 9-14: Detail/scroll text (after first ':' in val) for States 1-6
    # Format: "[ID]: [RESULT]:[DETAIL]" or "[ID]: HITTING:[HIT_RESULT]:[PITCH_DETAIL]"
    narr_tbl = _create_op(scene_base, 'tableDAT', 'narrative_table')
    narr_tbl.clear()
    result_data = {}   # Row 0-8: result text
    detail_data = {}   # Row 9-14: detail text (mapped from state 1-6)
    lines = narr_txt.text.split('\n')
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'): continue
        
        # First ':' separates StateID from content
        idx = -1
        val = ""
        if ':' in line:
            parts = line.split(':', 1)
            try: 
                idx = int(parts[0].strip())
                val = parts[1].strip()
            except: pass
        else:
            parts = line.split(None, 1)
            try: 
                idx = int(parts[0].strip())
                if len(parts) > 1: val = parts[1].strip()
            except: pass
            
        if idx >= 0:
            # For states 1-6: split on ':' for result/detail
            if idx >= 1 and idx <= 6 and ':' in val:
                fields = val.split(':')
                result_part = fields[0].strip()  # STRIKE, BALL, or HITTING
                
                if result_part.upper().startswith('HITTING') and len(fields) >= 3:
                    # HITTING:[HIT_RESULT]:[PITCH_DETAIL]
                    # e.g. "HITTING:FOUL:142km/h SPLITTER..."
                    # e.g. "HITTING:Center... Home Run! :138km/h SLIDER..."
                    hit_result = fields[1].strip()   # FOUL or Center... Home Run!
                    pitch_detail = fields[2].strip() if len(fields) > 2 else ""
                    result_data[idx] = result_part
                    # Concatenate hit result + pitch detail for scroll
                    detail_data[idx] = hit_result + "  " + pitch_detail if pitch_detail else hit_result
                else:
                    # STRIKE:[DETAIL] or BALL:[DETAIL]
                    result_data[idx] = result_part
                    detail_data[idx] = ':'.join(fields[1:]).strip()  # Rejoin any remaining ':' in detail
            else:
                # No split (Intro, HR Stats, Outro)
                if idx in result_data: result_data[idx] = result_data[idx] + "  " + val
                else: result_data[idx] = val

    # Build 16-row table
    for r in range(16):
        if r <= 8:
            txt = result_data.get(r, "")[:255]
        else:
            # Row 9-14 = detail for State 1-6 (r-8)
            txt = detail_data.get(r - 8, "")[:255]
        narr_tbl.appendRow([ord(c) for c in txt] + [0]*(256-len(txt)))
    narr_tbl.cook(force=True)
    
    print(f"    + Narrative parsed: {len(result_data)} states from {narrative_file}")
    for sid in sorted(result_data.keys()):
        r = result_data.get(sid, "")[:30]
        d = detail_data.get(sid, "")[:30]
        if d: print(f"      State {sid}: [{r}] / [{d}]")
        else: print(f"      State {sid}: [{r}]")

    # 1.3 Pixel Atlas (Pixel-perfect pre-rendered text)
    # 256 chars * 8px = 2048px wide. 16 states * 8px = 128px high.
    data_top = _create_op(scene_base, 'scriptTOP', 'data_texture')
    data_top.par.outputresolution = 'custom'
    data_top.par.resolutionw, data_top.par.resolutionh = 2048, 128
    if hasattr(data_top.par, 'format'): data_top.par.format = 'r8'

    font_path = (PROJECT_FOLDER + '/scripts/font_8x8.bin').replace('\\', '/')
    script_content = f"""import numpy as np
_f_cells = None

def onCook(scriptOp):
    global _f_cells
    if _f_cells is None:
        try:
            with open('{font_path}', 'rb') as f:
                raw = f.read()
                # Font is (8, 2048). Reshape to (256, 8, 8) and flip once for TD.
                raw_arr = np.frombuffer(raw, dtype=np.uint8).reshape(8, 256, 8)
                _f_cells = np.flip(raw_arr, axis=0).transpose(1, 0, 2).copy() # (char, y, x)
        except: pass

    tbl = op('narrative_table')
    arr = np.zeros((128, 2048, 1), dtype=np.uint8)
    lengths = [0] * 16

    if tbl and _f_cells is not None:
        for state_row in range(min(tbl.numRows, 16)):
            max_x = 0
            for char_col in range(min(tbl.numCols, 256)):
                try:
                    char_code = int(tbl[state_row, char_col])
                    if char_code == 0: continue
                    dst_x, dst_y = char_col * 8, state_row * 8
                    arr[dst_y:dst_y+8, dst_x:dst_x+8, 0] = _f_cells[char_code]
                    max_x = dst_x + 8
                except: pass
            lengths[state_row] = max_x

    # Render "HOME RUN!" to Row 15
    hr_text = "HOME RUN!"
    for i, char in enumerate(hr_text):
        dst_x = i * 8
        arr[15*8 : 15*8+8, dst_x : dst_x+8, 0] = _f_cells[ord(char)]
    lengths[15] = len(hr_text) * 8

    try:
        if hasattr(scriptOp, 'copyNumpyArray'):
            scriptOp.copyNumpyArray(np.ascontiguousarray(arr))
        # Store lengths as a uniform-ready format
        scriptOp.parent().store('pitch_lens', lengths)
    except Exception as e:
        print("Pixel Atlas cook error: " + str(e))
"""
    _set_script_code(data_top, script_content)
    # Set filtering to Nearest for pixel-perfect CRISP rendering
    if hasattr(data_top.par, 'filtertype'): data_top.par.filtertype = 0 # Nearest
    if hasattr(data_top.par, 'inputfiltertype'): data_top.par.inputfiltertype = 0
    data_top.cook(force=True)

    # 1.4 Font Atlas
    font_top = _create_op(scene_base, 'scriptTOP', 'font_atlas')
    font_top.par.outputresolution = 'custom'; font_top.par.resolutionw, font_top.par.resolutionh = 2048, 8
    if hasattr(font_top.par, 'format'): font_top.par.format = 'r8'
    
    font_path = (PROJECT_FOLDER + '/scripts/font_8x8.bin').replace('\\', '/')
    font_script = f"""import numpy as np
_f_cache = None
def onCook(scriptOp):
    global _f_cache
    if _f_cache is None:
        try:
            with open('{font_path}', 'rb') as f:
                _f_cache = f.read()
        except Exception as e:
            print("Font Load Error: " + str(e))
            return
            
    if _f_cache:
        try:
            # (8, 2048, 1) to satisfy copyNumpyArray
            arr = np.frombuffer(_f_cache, dtype=np.uint8).reshape(8, 2048, 1)
            # Ensure C-contiguous for stability in TD 2025
            scriptOp.copyNumpyArray(np.ascontiguousarray(np.flipud(arr)))
        except Exception as e:
            print("Font cook Error: " + str(e))
"""
    _set_script_code(font_top, font_script)
    if hasattr(font_top.par, 'filtertype'): font_top.par.filtertype = 1 # Linear for smooth sub-pixel sampling
    if hasattr(font_top.par, 'inputfiltertype'): font_top.par.inputfiltertype = 1
    font_top.cook(force=True)

    # 2. GLSL setup
    glsl = _create_op(scene_base, 'glslTOP', 'glsl_baseball')
    glsl.par.pixeldat = shader_dat; glsl.par.outputresolution = 'custom'
    glsl.par.resolutionw, glsl.par.resolutionh = LED_COLS, LED_ROWS
    # Connect Pixel Atlas (Input 0)
    glsl.inputConnectors[0].connect(data_top)
    # Ensure Input 1 (previously font) is disconnected
    if len(glsl.inputConnectors) > 1:
        glsl.inputConnectors[1].disconnect()
    
    # 3. Uniforms
    glsl.par.uniname0, glsl.par.value0x.expr = 'uTime', 'absTime.seconds'
    glsl.par.uniname1, glsl.par.value1x.expr = 'uPitchIndex', "int((absTime.frame % 8100) / 900)"
    glsl.par.uniname2, glsl.par.value2x.expr = 'uStateFrame', "absTime.frame % 900"
    
    # Pass 16 text lengths via 4 vec4s (uLenA, uLenB, uLenC, uLenD)
    for i, name in enumerate(['uLenA', 'uLenB', 'uLenC', 'uLenD']):
        setattr(glsl.par, f'uniname{i+3}', name)
        for j, comp in enumerate(['x','y','z','w']):
            idx = i * 4 + j
            expr = f"me.parent().fetch('pitch_lens', [0]*16)[{idx}]"
            setattr(glsl.par, f'value{i+3}{comp}', 0) # Default
            getattr(glsl.par, f'value{i+3}{comp}').expr = expr
    
    # 4. Output
    out = scene_base.op('scene_out') or _create_op(scene_base, 'nullTOP', 'scene_out')
    out.inputConnectors[0].connect(glsl)
    print(f'    + SCENE_6: Dynamic Baseball System (8x8 Font) Ready')

def dep():
    root = op('/AudioLinkLight_V01')
    if not root: return
    print("="*60)
    print("[deploy_scenes] デプロイを開始します")
    print("="*60)
    for i in range(1, 7):
        s_base = root.op(f'SCENE_{i}') or _create_op(root, 'baseCOMP', f'SCENE_{i}')
        if i == 1: _build_scene1(s_base)
        elif i == 2: _build_scene2(s_base)
        elif i == 3: _build_scene3(s_base)
        elif i == 4: _build_scene4(s_base)
        elif i == 5: _build_scene5(s_base)
        elif i == 6: _build_scene6(s_base)
    
    # UIボタンを作成/更新
    _create_ui_button(root)
    
    print("\n[COMPLETE] すべてのシーンが更新されました")

if __name__ == '__main__':
    dep()
