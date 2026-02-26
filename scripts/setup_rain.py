# setup_rain.py
# Run in TD Textport:
#   exec(open(project.folder + '/scripts/setup_rain.py', encoding='utf-8').read())
#
# 実行後: led_source の入力を手動で pat_rain に繋ぎ替えると光の雨が表示されます

TARGET = '/AudioLinkLight_V01/TEST_SCREEN'
base = op(TARGET)

if base is None:
    print(f'[ERROR] {TARGET} not found')
else:
    # ---- 既存ノードを削除 ----
    for name in ('pat_rain', 'pat_rain_glsl'):
        o = base.op(name)
        if o is not None:
            o.destroy()

    GLSL_CODE = open(project.folder + '/scripts/rain_shader.glsl', encoding='utf-8').read()

    # ---- シェーダーDAT ----
    shader_dat = base.create(textDAT, 'pat_rain_glsl')
    shader_dat.text = GLSL_CODE
    shader_dat.nodeX = 0
    shader_dat.nodeY = -450

    # ---- GLSL TOP ----
    glsl = base.create(glslTOP, 'pat_rain')
    glsl.par.pixeldat = shader_dat
    glsl.par.outputresolution = 'custom'
    glsl.par.resolutionw = 88
    glsl.par.resolutionh = 10
    glsl.nodeX = 0
    glsl.nodeY = -330

    # ---- uTime uniform ----
    glsl.par.uniname1 = 'uTime'
    glsl.par.value1x.expr = 'absTime.seconds'
    glsl.par.value1x.mode = ParMode.EXPRESSION  # 式評価モードに切り替え（必須）

    print('=' * 40)
    print('[setup_rain] Done!')
    print(f'  pat_rain : {glsl.width} x {glsl.height}')
    print(f'  uTime    : {glsl.par.value1x.expr}')
    print()
    print('--- 次の手順 ---')
    print('  led_source の入力を pat_rain に手動で繋ぎ直してください')
    print('  (rainbow に戻すには pat_rainbow に繋ぎ直してください)')
    print('  密度変更: rain_shader.glsl の density 値を編集して')
    print('  pat_rain_glsl DAT を再ロードしてFlush Cacheを押してください')
    print('=' * 40)