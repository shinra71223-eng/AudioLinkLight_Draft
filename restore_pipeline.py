"""
restore_pipeline.py
===================
テストパターンを解除して cross_mix → level_serial の元の接続に戻す。

【実行方法 (TD Textport)】
exec(open(project.folder + '/restore_pipeline.py', encoding='utf-8').read())
"""

def find_test_screen():
    candidates = root.findChildren(type=baseCOMP, name='TEST_SCREEN')
    if not candidates:
        raise RuntimeError("TEST_SCREEN が見つかりません。")
    return candidates[0]

parent = find_test_screen()

cross_mix    = parent.op('cross_mix')
level_serial = parent.op('level_serial')

if cross_mix is None:
    raise RuntimeError("cross_mix が見つかりません。")
if level_serial is None:
    raise RuntimeError("level_serial が見つかりません。")

level_serial.inputConnectors[0].connect(cross_mix)
print("[restore_pipeline] level_serial の入力を cross_mix に戻しました")

# toptoCHOP を layout_10x88 に戻す
top_to_chop = parent.op('top_to_chop')
layout = parent.op('layout_10x88')
if top_to_chop and layout:
    top_to_chop.par.top = layout.path
    print("[restore_pipeline] top_to_chop → layout_10x88 に戻しました")

# テスト用ノードを削除
for name in ['test_glsl', 'test_glsl_dat']:
    op = parent.op(name)
    if op:
        op.destroy()
        print(f"[restore_pipeline] {name} を削除しました")

print("元の映像パイプラインに戻りました。")
