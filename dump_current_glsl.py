# dump_current_glsl.py
import traceback
import os

try:
    # 候補となるコンポーネントのパス
    target_comps = ['/TEST_SCREEN2', 'TEST_SCREEN2', '/AudioLinkLight_V03/TEST_SCREEN2', op('/').findChildren(name='TEST_SCREEN2')[0].path if op('/').findChildren(name='TEST_SCREEN2') else None]
    
    comp = None
    for path in target_comps:
        if path and op(path):
            comp = op(path)
            break
            
    if comp:
        print(f"Found COMP: {comp.path}")
        target_dat = None
        
        # 名前の中に pixel や glsl が含まれる Text DAT を検索
        dats = comp.findChildren(type=textDAT)
        for d in dats:
            if 'pixel' in d.name.lower():
                target_dat = d
                break
        
        if not target_dat:
            for d in dats:
                if 'glsl' in d.name.lower():
                    target_dat = d
                    break
                    
        if not target_dat and dats:
            target_dat = dats[0] # 見つからなければ最初のテキストDAT
            
        if target_dat:
            out_path = os.path.join(project.folder, 'current_glsl.glsl')
            with open(out_path, 'w', encoding='utf-8') as f:
                f.write(target_dat.text)
            print(f"Success: Dumped '{target_dat.path}' to '{out_path}'")
        else:
            print(f"Error: No Text DAT found inside {comp.path}")
    else:
        print("Error: TEST_SCREEN2 COMP not found.")
except Exception as e:
    traceback.print_exc()
