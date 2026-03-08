# enhance_scene2.py
# ================================================================
# Scene 2 の Noise TOP を「ぬめぬめ」動くアニメーションに変更し、
# 動画書き出し用の Movie File Out TOP を追加するスクリプト
# ================================================================
# 【実行方法 (TD Textport)】
#   exec(open(project.folder + '/scripts/enhance_scene2.py', encoding='utf-8').read())
# ================================================================

SCENE_PATH = '/AudioLinkLight_V01/SCENE_2'
NOISE_NAME = 'pat_noise'
MOVIE_OUT_NAME = 'movie_out'

def enhance():
    scene = op(SCENE_PATH)
    if scene is None:
        print(f'[ERROR] {SCENE_PATH} が見つかりません。先に deploy_scenes.py を実行してください。')
        return

    n = scene.op(NOISE_NAME)
    if n is None:
        print(f'[ERROR] {NOISE_NAME} が見つかりません。')
        return

    print(f'>>> {SCENE_PATH}/{NOISE_NAME} のパラメータを更新中...')

    # 1. 液体のような滑らかな動きの設定 (調査済み名称: amp, exp, harmon, rough, rz)
    n.par.type = 'simplex3d'
    n.par.period = 8.0
    n.par.seed = 150

    # ユーザーの調整値を記憶
    safe_aesthetic_params = {
        'harmon': 2,
        'spread': 2,
        'gain': 0.35,
        'rough': 0.5,
        'exp': 0.6,
        'amp': 0.4,
        'offset': 0.5
    }
    for p_name, p_val in safe_aesthetic_params.items():
        if hasattr(n.par, p_name):
            try:
                getattr(n.par, p_name).val = p_val
            except:
                pass

    # アニメーション (ぬめぬめ + わずかな回転)
    if hasattr(n.par, 'tz'):
        n.par.tz.expr = 'absTime.seconds * 0.15'
    if hasattr(n.par, 'rz'):
        n.par.rz.expr = 'absTime.seconds * 2.0'
    
    # 2. ランダムな色の変化設定 (より混ざり合うイメージ)
    n.par.mono = False
    
    color_exprs = [
        '0.5 + 0.4 * math.sin(absTime.seconds * 0.07)',
        '0.5 + 0.4 * math.sin(absTime.seconds * 0.13)',
        '0.5 + 0.4 * math.sin(absTime.seconds * 0.19)'
    ]
    
    # offset1, 2, 3 または offsetr, g, b を試す
    for i, expr in enumerate(color_exprs):
        p_name = f'offset{i+1}'
        if hasattr(n.par, p_name):
            getattr(n.par, p_name).expr = expr
        else:
            p_name_alt = f'offset{"rgb"[i]}'
            if hasattr(n.par, p_name_alt):
                getattr(n.par, p_name_alt).expr = expr

    print(f'  [OK] アニメーションと色の設定を完了しました。')

    # 3. 動画書き出し設定 (scene2_noise_秒数.mp4)
    m = scene.op('movie_out')
    if m is None:
        m = scene.create(moviefileoutTOP, 'movie_out')
    
    # 入力接続
    if len(m.inputs) == 0 or m.inputs[0] != n:
        m.inputConnectors[0].connect(n)

    # 書き出し設定の最適化
    m.par.file = project.folder + f'/media/scene2_noise_{int(absTime.seconds)}.mp4'
    
    # バージョン間の互換性を考慮 (moviecontainer, videocodec)
    if hasattr(m.par, 'moviecontainer'):
        try:
            m.par.moviecontainer = 'mp4'
        except:
            pass
    if hasattr(m.par, 'videocodec'):
        try:
            m.par.videocodec = 'h264'
        except:
            pass
    
    # 4. 動画書き出し (Movie File Out TOP) の追加
    m = scene.op(MOVIE_OUT_NAME)
    if m is None:
        m = scene.create(moviefileoutTOP, MOVIE_OUT_NAME)
        m.nodeX = 600
        m.nodeY = 0
        print(f'  [NEW] {MOVIE_OUT_NAME} を作成しました。')
    else:
        print(f'  [EXISTS] {MOVIE_OUT_NAME} は既に存在します。')

    # インプットの接続
    # pat_noise -> movie_out
    if len(m.inputs) == 0 or m.inputs[0] != n:
        m.inputConnectors[0].connect(n)
        print(f'  [INFO] {NOISE_NAME} を {MOVIE_OUT_NAME} に接続しました。')

    # 書き出し設定の最適化
    m.par.file = project.folder + f'/media/scene2_noise_{int(absTime.seconds)}.mp4'
    
    # バージョン間の互換性を考慮した安全なパラメータ設定
    for p_name, p_val in [('filetype', 'mpeg4'), ('codec', 'h264'), ('subtype', 'mp4')]:
        if hasattr(m.par, p_name):
            try:
                getattr(m.par, p_name).val = p_val
            except:
                pass
    
    print('=' * 60)
    print('【完了】Scene 2 の強化が完了しました！')
    print('=' * 60)
    print('使い方:')
    print(f' 1. TouchDesigner上で {SCENE_PATH} ネットワークに入ります。')
    print(f' 2. {MOVIE_OUT_NAME} ノードの "Record" パラメータを ON にすると録画が始まります。')
    print(f' 3. 録画を止めたいときは "Record" を OFF にしてください。')
    print('=' * 60)

if __name__ == '__main__':
    enhance()
