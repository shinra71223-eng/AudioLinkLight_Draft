"""
deploy_test_pattern.py
======================
TEST_SCREEN に Rainbow テストパターンを注入し、
Python executeDAT 経由で ESP32 に uint8 RGB バイトを直接送信する。

serialCHOP は float/text 向けのため使わない。
代わりに executeDAT + serial モジュールで768バイト/フレームを送信。

【実行方法 (TD Textport)】
exec(open(project.folder + '/deploy_test_pattern.py', encoding='utf-8').read())

【元に戻すには】
exec(open(project.folder + '/restore_pipeline.py', encoding='utf-8').read())
"""

# ── TEST_SCREEN を直接取得 ──────────────────────────────────
parent = op('/AudioLinkLight_V01/TEST_SCREEN')
if parent is None:
    raise RuntimeError("op('/AudioLinkLight_V01/TEST_SCREEN') が見つかりません。パスを確認してください。")

print("[test_pattern] TEST_SCREEN:", parent.path)

# ─── 既存の test_glsl / serial_sender をクリーンアップ ─────
for name in ('test_glsl_dat', 'test_glsl', 'serial_sender'):
    if parent.op(name):
        parent.op(name).destroy()

# ─── テスト用 GLSL DAT ───────────────────────────────────────
glsl_dat = parent.create(textDAT, 'test_glsl_dat')
glsl_dat.text = '''\
out vec4 fragColor;
uniform float uTime;

vec3 hsv2rgb(float h, float s, float v) {
    h = mod(h, 1.0);
    int   i = int(floor(h * 6.0));
    float f = h * 6.0 - float(i);
    float p = v * (1.0 - s);
    float q = v * (1.0 - f * s);
    float t = v * (1.0 - (1.0 - f) * s);
    if (i == 0) return vec3(v, t, p);
    if (i == 1) return vec3(q, v, p);
    if (i == 2) return vec3(p, v, t);
    if (i == 3) return vec3(p, q, v);
    if (i == 4) return vec3(t, p, v);
                return vec3(v, p, q);
}

void main() {
    vec2 res = uTDOutputInfo.res.zw;
    int  ix  = int(floor(vUV.x * res.x));
    int  iy  = int(floor(vUV.y * res.y));
    int  idx = iy * int(res.x) + ix;

    float hue = mod(float(idx) / float(int(res.x) * int(res.y)) - uTime * 0.2, 1.0);

    // 輝度: 10/255 に制限（確認時は 1.0 に変えるとわかりやすい）
    const float BRIGHTNESS = 10.0 / 255.0;

    vec3 col = hsv2rgb(hue, 1.0, BRIGHTNESS);
    fragColor = vec4(col, 1.0);
}
'''
glsl_dat.nodeX = -200
glsl_dat.nodeY = -300

# ─── テスト用 GLSL TOP ──────────────────────────────────────
test_top = parent.create(glslTOP, 'test_glsl')
test_top.par.pixeldat = 'test_glsl_dat'
test_top.par.outputresolution = 'custom'
test_top.par.resolutionw = 88
test_top.par.resolutionh = 10
test_top.par.uniname0 = 'uTime'
test_top.par.value0x.mode = ParMode.EXPRESSION
test_top.par.value0x.expr = 'absTime.seconds'
test_top.nodeX = -200
test_top.nodeY = -150

# ─── serial_sender executeDAT ──────────────────────────────
#  top.numpyArray() → uint8 RGB 768バイト → COM6 送信 (30fps)
sender_dat = parent.create(executeDAT, 'serial_sender')
sender_dat.par.framestart = True   # onFrameStart() を毎フレーム実行
sender_dat.par.active = True
sender_dat.nodeX = 200
sender_dat.nodeY = -150

sender_dat.text = '''\
# serial_sender  — executeDAT (毎フレーム RGB→ESP32 送信)
# _ser を TD root storage に保存し、DAT 再コンパイル後もポートを維持する

def onFrameStart(frame):
    if int(frame) % 2 != 0:
        return

    import sys
    _p = r'C:\\Users\\shin_\\AppData\\Roaming\\Python\\Python311\\site-packages'
    if _p not in sys.path:
        sys.path.insert(0, _p)

    import serial as _serial
    import numpy as _np

    # root storage からポートオブジェクトを取得（DAT 再コンパイル後も保持）
    _ser = op('/').fetch('_led_serial', None)

    if _ser is None or not _ser.is_open:
        try:
            s = _serial.Serial()
            s.port = 'COM6'
            s.baudrate = 921600
            s.timeout = 0
            s.write_timeout = 0
            s.dtr = False
            s.rts = False
            s.open()
            op('/').store('_led_serial', s)
            _ser = s
            print('[serial_sender] COM6 opened (DTR=False)')
        except Exception as e:
            print('[serial_sender] open error:', e)
            return

    top = op('/AudioLinkLight_V01/TEST_SCREEN/test_glsl')  # 88×10=880LED, 2640バイト
    if top is None:
        return
    arr = top.numpyArray(delayed=False)
    if arr is None:
        return
    data = (_np.array(arr)[:, :, :3] * 255.0).clip(0, 255).astype(_np.uint8).reshape(-1).tobytes()
    try:
        _ser.write(data)
    except Exception as e:
        print('[serial_sender] write error:', e)
        try: _ser.close()
        except: pass
        op('/').store('_led_serial', None)
'''

print("[test_pattern] serial_sender executeDAT 作成完了")
print()
print("=" * 50)
print("テストパターン注入完了！")
print("  serial_sender (executeDAT) が毎フレーム RGB バイトを COM6 に送信します。")
print("  LED1 から順に Rainbow が流れます (輝度 10/255)")
print()
print("元に戻すには:")
print("exec(open(project.folder + '/restore_pipeline.py', encoding='utf-8').read())")
print("=" * 50)
