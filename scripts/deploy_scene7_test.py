# deploy_scene7_test.py
# ================================================================
# SCENE_7: Test Pattern for LED Calibration
# ================================================================
import os

ROOT_PATH = '/AudioLinkLight_V01'
SCENE_PATH = f'{ROOT_PATH}/TEST7'

# GLSL Pixel Shader Code for generating the precise test sequence
GLSL_CODE = """
out vec4 fragColor;
void main()
{
    // Pixel coordinates (0 to 87, 0 to 49)
    int px = int(gl_FragCoord.x);
    int py = int(gl_FragCoord.y);

    // 20 second loop
    float t = mod(uTime, 20.0); 

    vec3 col = vec3(0.0);

    // 0-2: Solid Blue (fade out)
    if(t < 2.0) {
        float alpha = 1.0 - (t / 2.0);
        col = vec3(0.0, 0.0, 1.0) * alpha;
    }
    // 2-4: Solid Red (fade out)
    else if(t < 4.0) {
        float alpha = 1.0 - ((t - 2.0) / 2.0);
        col = vec3(1.0, 0.0, 0.0) * alpha;
    }
    // 4-6: Solid Green (fade out)
    else if(t < 6.0) {
        float alpha = 1.0 - ((t - 4.0) / 2.0);
        col = vec3(0.0, 1.0, 0.0) * alpha;
    }
    // 6-9: Solid Black (3 seconds)
    else if(t < 9.0) {
        col = vec3(0.0);
    }
    // 9-11: Solid White (fade out)
    else if(t < 11.0) {
        float alpha = 1.0 - ((t - 9.0) / 2.0);
        col = vec3(1.0, 1.0, 1.0) * alpha;
    }
    // 11-20: Scanning yellow lines
    else {
        float scanT = t - 11.0;
        // speed 20 pixels per second. Start at -10 so it enters smoothly
        float base_x = scanT * 20.0 - 10.0; 
        float width = 5.0;
        
        bool isYellow = false;
        
        // Y=11-20 UP (offset 0)
        if(py >= 11 && py <= 20) {
            float x_target = base_x;
            if(px >= int(x_target) && px < int(x_target + width)) isYellow = true;
        }
        // Y=21-30 CENTER (offset 10)
        else if(py >= 21 && py <= 30) {
            float x_target = base_x - 10.0;
            if(px >= int(x_target) && px < int(x_target + width)) isYellow = true;
        }
        // Y=31-40 DOWN (offset 20)
        else if(py >= 31 && py <= 40) {
            float x_target = base_x - 20.0;
            if(px >= int(x_target) && px < int(x_target + width)) isYellow = true;
        }
        
        if(isYellow) {
            col = vec3(1.0, 1.0, 0.0); // Yellow
        }
    }

    fragColor = vec4(col, 1.0);
}
"""

def deploy():
    scene = op(SCENE_PATH)
    if not scene:
        print(f'[ERROR] {SCENE_PATH} をTouchDesignerで見つけられませんでした。プロジェクトを開いた状態で実行してください。')
        return

    print('='*60)
    print(f'[deploy_scene7] {SCENE_PATH} テスト点灯用モジュールを構築中...')
    print('  - 88x50の解像度で指定のシーケンス（青->赤->緑->黒->白->黄色スキャン）を生成')
    
    # Clean up existing nodes safely
    for o in list(scene.children):
        try: o.destroy()
        except: pass

    # DAT for GLSL Code
    code_dat = scene.create(textDAT, 'glsl_code')
    code_dat.text = GLSL_CODE
    
    # GLSL TOP
    glsl = scene.create(glslTOP, 'test_pattern')
    glsl.par.outputresolution = 1
    glsl.par.resolutionw = 88
    glsl.par.resolutionh = 50
    glsl.par.pixelformat = 3 # 8-bit fixed (RGBA)
    
    glsl.par.pixelshader = code_dat.name
    
    # Send absolute time to shader
    glsl.par.unames1 = 'uTime'
    glsl.par.uvalues11.expr = 'absTime.seconds'
    
    # Final Null Output
    out = scene.create(nullTOP, 'scene_out')
    out.inputConnectors[0].connect(glsl)
    
    # Layout Nodes cleanly
    code_dat.nodeX, code_dat.nodeY = -200, 0
    glsl.nodeX, glsl.nodeY = 50, 0
    out.nodeX, out.nodeY = 250, 0
    
    print('構築完了しました！TouchDesignerで結果を確認してください。')
    print('='*60)

if __name__ == '__main__':
    deploy()
