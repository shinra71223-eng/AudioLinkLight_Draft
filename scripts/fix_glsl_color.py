# fix_glsl_color.py
import td

scene = op('/AudioLinkLight_V01/SCENE_6')
if not scene:
    scene = op('SCENE_6')

if scene:
    glsl = scene.op('glsl_baseball')
    if glsl:
        print("====== GLSL Color Fix ======")
        print(f"Target: {glsl.path}")
        
        # GLSL TOPの固有パラメータ 'format0' (Color Buffer 0 Format) を強制する
        # 0: Use Input 
        # メニューから 32-bit float (RGBA) を探す
        try:
            p = glsl.par.format0
            for i, name in enumerate(p.menuNames):
                if '32-bit float (RGBA)' in name:
                    p.menuIndex = i
                    print(f"[SUCCESS] Changed format0 from {p.val} to {name}")
                    break
        except Exception as e:
            print(f"[FAIL] format0 error: {e}")
            
        print("============================")
else:
    print("SCENE_6 not found")
