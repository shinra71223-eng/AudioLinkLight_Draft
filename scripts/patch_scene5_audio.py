# patch_scene5_audio.py
# ================================================================
# SCENE_5 ローカル音声統合パッチ (Hihat + SoundEnergy 版)
# ================================================================

AUDIO_CORE_OUT = '/AudioLinkLight_V01/AudioLinkCore/out1'
SCENE_PATH = '/AudioLinkLight_V01/SCENE_5'

def patch():
    scene = op(SCENE_PATH)
    if not scene:
        print(f"Error: {SCENE_PATH} not found")
        return

    # 1. SCENE_5 内に音声を「取り込む」ための CHOP 構成
    sel = scene.op('select_audio') or scene.create(selectCHOP, 'select_audio')
    null = scene.op('audio_data') or scene.create(nullCHOP, 'audio_data')
    
    sel.par.chop = AUDIO_CORE_OUT
    # 修正: Hihat と SoundEnergy だけを抽出 (uBassEnergyは除外)
    sel.par.channames = 'Hihat SoundEnergy' 
    null.inputConnectors[0].connect(sel)
    
    sel.nodeX, sel.nodeY = -1400, 500
    null.nodeX, null.nodeY = -1200, 500

    print(f"Updated local audio bridge in SCENE_5: {null.path}")

    # 2. ローカルの 'audio_data' を参照するように各ノードを更新
    # shape_pulse (脈動) -> SoundEnergy を使用
    pulse = scene.op('shape_pulse')
    if pulse:
        expr = "0.4 + (op('audio_data')['SoundEnergy'] * 0.4)"
        pulse.par.sx.expr = expr
        pulse.par.sy.expr = expr
        print(f"Patched {pulse.name} to reference SoundEnergy")

    # organic_warp (歪み) -> Hihat を使用
    warp = scene.op('organic_warp')
    if warp:
        expr = "0.01 + (op('audio_data')['Hihat'] * 0.15)"
        warp.par.displaceweightx.expr = expr
        warp.par.displaceweighty.expr = expr
        print(f"Patched {warp.name} to reference Hihat")

if __name__ == '__main__':
    patch()
