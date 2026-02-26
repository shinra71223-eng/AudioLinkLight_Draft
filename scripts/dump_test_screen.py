# dump_test_screen.py
# ================================================================
# TD Textport で実行 → TEST_SCREEN BASE の中身を詳細ダンプ
# 使い方:
#   exec(open(r'C:\Users\shin_\...\scripts\dump_test_screen.py').read())
# ================================================================

TARGET = '/AudioLinkLight_V01/TEST_SCREEN'

def dump():
    base = op(TARGET)
    if base is None:
        print(f"[ERROR] {TARGET} が見つかりません")
        # 近いパスを探す
        for c in op('/').findChildren(name='TEST_SCREEN', recurse=True):
            print(f"  候補: {c.path}")
        return

    print("=" * 60)
    print(f"BASE: {base.path}  type={base.type}")
    print("=" * 60)

    children = base.findChildren(depth=1)
    print(f"子ノード数: {len(children)}")
    print()

    for ch in sorted(children, key=lambda x: x.name):
        print(f"  [{ch.type:12s}] {ch.name}")
        # Serial DAT の場合はパラメータを詳細表示
        if ch.type in ('serialdat', 'Serial DAT', 'serialDAT'):
            try:
                print(f"            port={ch.par.port}  baud={ch.par.baudrate}  active={ch.par.active}  mode={ch.par.mode}")
            except Exception as e:
                print(f"            (par read error: {e})")
        # Execute DAT
        if ch.type in ('executedat', 'Execute DAT', 'executeDAT'):
            try:
                print(f"            framestart={ch.par.framestart}  active={ch.par.active}")
                lines = ch.text.splitlines()
                preview = lines[:5]
                for l in preview:
                    print(f"            | {l}")
                if len(lines) > 5:
                    print(f"            | ... ({len(lines)} lines total)")
            except Exception as e:
                print(f"            (text read error: {e})")
        # TOP系
        if ch.family == 'TOP':
            try:
                print(f"            res={ch.width}x{ch.height}")
            except:
                pass
        # CHOP系
        if ch.family == 'CHOP':
            try:
                print(f"            numChans={ch.numChans}")
            except:
                pass

    print()
    print("─" * 60)
    # ワイヤー接続の確認
    print("接続状況:")
    for ch in sorted(children, key=lambda x: x.name):
        try:
            ins  = [i.owner.name for i in ch.inputConnectors if i.owner]
            outs = [o.owner.name for o in ch.outputConnectors if o.owner]
            if ins or outs:
                print(f"  {ch.name}  ← {ins}  → {outs}")
        except:
            pass

dump()
