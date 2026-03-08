# update_scene6_text.py
# ================================================================
# Text Update Script for SCENE_6
# Safely updates narrative_table (main), narrative_table_batter, 
# and narrative_table_pitcher without breaking any COMP connections.
# ================================================================
import td

SCENE_PATH = '/AudioLinkLight_V01/SCENE_6'
NARRATIVE_FILE = project.folder + '/scripts/baseball_narrative.md'

def parse_main_narrative(text):
    result_data = {}
    detail_data = {}
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'): continue
        if 'STRETCHERS(Batter)' in line: break # Stop at support sections
        
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
            if idx >= 1 and idx <= 6 and ':' in val:
                fields = val.split(':')
                result_part = fields[0].strip()
                if result_part.upper().startswith('HITTING') and len(fields) >= 3:
                    hit_result = fields[1].strip()
                    pitch_detail = fields[2].strip() if len(fields) > 2 else ""
                    result_data[idx] = result_part
                    detail_data[idx] = hit_result + "  " + pitch_detail if pitch_detail else hit_result
                else:
                    result_data[idx] = result_part
                    detail_data[idx] = ':'.join(fields[1:]).strip()
            else:
                if idx in result_data: result_data[idx] = result_data[idx] + "  " + val
                else: result_data[idx] = val
    return result_data, detail_data

def parse_support_narrative(text):
    batter_msgs = [""] * 16
    pitcher_msgs = [""] * 16
    current_section = "main"
    lines = text.split('\n')
    for line in lines:
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
                    if current_section == "batter": batter_msgs[idx] = msg
                    elif current_section == "pitcher": pitcher_msgs[idx] = msg
            except ValueError: pass
            
    for i in range(16):
        if not batter_msgs[i]: batter_msgs[i] = "Go! Go!"
        if not pitcher_msgs[i]: pitcher_msgs[i] = "Fight!"
    return batter_msgs, pitcher_msgs

def update():
    scene = op(SCENE_PATH)
    if not scene: scene = op('SCENE_6')
    if not scene:
        print(f"Error: SCENE_6 not found."); return

    print("="*60)
    print(f"UPDATING NARRATIVE TEXT: {scene.path}")
    print("="*60)

    try:
        with open(NARRATIVE_FILE, 'r', encoding='utf-8') as f:
            raw_text = f.read()
    except Exception as e:
        print(f"Error reading narrative file {NARRATIVE_FILE}: {e}")
        return

    # 1. Update narrative_data (DAT)
    narr_txt = scene.op('narrative_data')
    if narr_txt:
        narr_txt.text = raw_text
        narr_txt.cook(force=True)

    # 2. Parse texts
    result_data, detail_data = parse_main_narrative(raw_text)
    b_msgs, p_msgs = parse_support_narrative(raw_text)

    # 3. Update main narrative_table
    narr_tbl = scene.op('narrative_table')
    if narr_tbl:
        narr_tbl.clear()
        for r in range(16):
            if r <= 8: txt = result_data.get(r, "")[:255]
            else: txt = detail_data.get(r - 8, "")[:255]
            row_data = [str(ord(c)) for c in txt] + ['0']*(256-len(txt))
            narr_tbl.appendRow(row_data)
        narr_tbl.cook(force=True)
        print(f"  + Main text updated (narrative_table)")

        dt_main = scene.op('data_texture')
        if dt_main: dt_main.cook(force=True)

    # 4. Update Support tables
    def update_support_table(table_name, dt_name, msgs):
        tbl = scene.op(table_name)
        if tbl:
            tbl.clear()
            for msg in msgs:
                row_data = []
                for col_idx in range(256):
                    if col_idx < len(msg): row_data.append(str(ord(msg[col_idx])))
                    else: row_data.append('0')
                tbl.appendRow(row_data)
            tbl.cook(force=True)
            print(f"  + Support text updated ({table_name})")
            
            dt = scene.op(dt_name)
            if dt: dt.cook(force=True)

    update_support_table('narrative_table_batter', 'data_texture_batter', b_msgs)
    update_support_table('narrative_table_pitcher', 'data_texture_pitcher', p_msgs)

    print("="*60)
    print("TEXT UPDATE COMPLETE")
    print("="*60)

update()
