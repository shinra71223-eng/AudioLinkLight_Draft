"""
dump_op_params.py
=================
指定したOP種別のパラメータ名を全て出力するデバッグスクリプト
TEST_SCREEN 内に一時的にOPを作成してパラメータを確認し、すぐ削除する

【実行方法 (TD Textport)】
exec(open(project.folder + '/dump_op_params.py', encoding='utf-8').read())
"""

def dump_params(op_type, op_name_str):
    tmp = root.create(op_type, 'tmp_param_dump_9999')
    print(f"\n=== {op_name_str} パラメータ一覧 ===")
    for p in tmp.pars():
        print(f"  {p.name:30s}  val={p.val}  label={p.label}")
    tmp.destroy()

dump_params(toptoCHOP, 'toptoCHOP')
