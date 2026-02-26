# ExacコマンドによるTouchDesignerの外部制御マニュアル

## 1. Exacコマンドとは？

「Exacコマンド」（Execコマンド）は、TouchDesignerの **Text Port** に直接貼り付けて実行するPythonコードのことです。
通常、TouchDesignerの外部（VSCodeやAntigravity）で書いたスクリプトファイルを、TouchDesigner内で手軽に「読み込んで実行」するために使用します。

---

## 2. 標準的な実行方法

以下のコードをコピーして、TouchDesignerのText Port (`Alt+T`) に貼り付けてください。

```python
# ファイルを読み込んで実行する基本パターン
exec(open(project.folder + '/scripts/ファイル名.py', encoding='utf-8').read())
```

### 💡 なぜこの形なのか？
- `project.folder`: プロジェクト（.toeファイル）があるフォルダを自動で指します。
- `open(..., encoding='utf-8')`: 日本語（UTF-8）が含まれていてもエラーにならないように安全にファイルを開きます。
- `read()`: ファイルの中身をテキストとして読み込みます。
- `exec(...)`: 読み込んだテキストをPythonコードとして実行（実行：Execute）します。

---

## 3. 具体的な手順

1. **スクリプトの準備**
   VSCodeやAntigravityでスクリプトファイル（例: `deploy_v3.py`）を作成・保存します。保存先はプロジェクトフォルダ内の `scripts/` 等が推奨されます。

2. **TouchDesignerでText Portを開く**
   TouchDesignerを表示し、`Alt+T` を押すか、上部メニューの `Dialogs` -> `Text Port` を開きます。

3. **コマンドの貼り付けと実行**
   上記の `exec(...)` コマンド内のファイル名を書き換えて貼り付け、**Enter** キーを押します。

---

## 4. プロジェクトでの活用例

このプロジェクト（`AudioLinkLight`）では、主に以下の用途で使用されます。

### 🎵 音楽フォルダのパス修正
```python
exec(open(project.folder + '/scripts/fix_music_paths.py', encoding='utf-8').read())
```

### 🛠️ 新しいコンポーネントの配置（デプロイ）
```python
exec(open(project.folder + '/scripts/deploy_cyber_clock_v2.py', encoding='utf-8').read())
```

---

## 5. デバッグと効率化のコツ

- **エラーの確認**:
  実行時にエラーが発生すると、Text Portに赤い文字でエラーメッセージが表示されます。ファイルパスが正しいか、スクリプトにタイプミスがないか確認してください。

- **素早い再実行**:
  一度実行したコマンドは、Text Port内で **↑キー** を押すことで履歴から呼び出せます。修正して保存したスクリプトを即座に再試行する際に便利です。

- **進捗の表示**:
  スクリプト内で `print("Deployment Complete!")` のように記述しておくと、実行完了がText Portで確認しやすくなります。
