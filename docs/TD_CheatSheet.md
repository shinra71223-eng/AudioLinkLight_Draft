# TouchDesigner (TD) Python Command Cheat Sheet

本プロジェクト (AudioLinkLight) で頻繁に使用するTouchDesignerの主要なPythonコマンドとアクセス方法のリストです。これまでの作業（Rhythm/Kickの解析やScript CHOPのデバッグなど）に基づき、要点を整理しました。

## 1. オペレータ (OP) の参照
- `op('node_name')` : 同じ階層にあるノードを参照
- `parent()` : 親コンポーネントを参照 （例: `parent().par.uVocalIntensity`）
- `parent(2)` : 2階層上の親コンポーネントを参照
- `op('path/to/node')` : 相対・絶対パスでの参照
- `iop.name` / `ipar.name` : 内部OP (Internal OP) や内部パラメータへのショートカット

## 2. パラメータ (Parameter) の操作
- `op('node').par.ParName` : パラメータの値の取得・設定
  - 例: `op('level1').par.brightness1 = 1.5`
- `op('node').par.ParName.expr = "..."` : エクスプレッションの設定
- `op('node').par.ParName.mode` : パラメータモードの取得・設定
  - `ParMode.CONSTANT`
  - `ParMode.EXPRESSION`
  - `ParMode.EXPORT`

## 3. クッキング (Cooking) と状態制御
- `op('node').cook(force=True)` : ノードの再計算（クック）を強制的に実行
- `op('node').bypass = True / False` : ノードのバイパス状態の切り替え（デバッグ時に多用）
- `op('node').allowCooking = True / False` : クッキングの許可・禁止

## 4. Script CHOP に関するコマンド (onCook コールバック内)
- `scriptOp.clear()` : すべてのチャンネルとサンプルをクリア
- `scriptOp.numSamples = N` : 出力するサンプル数を指定
- `chan = scriptOp.appendChan('chan_name')` : 新しいチャンネルを追加
- `scriptOp['chan_name'][index] = value` : 特定のチャンネル内のサンプル値を更新
- `scriptOp.copy(inputs[0])` : 入力CHOPのデータをそのままコピー

## 5. エラーハンドリング・デバッグ
- `op('node').addScriptError("Error Message")` : OPにスクリプトエラーを表示（ノードに赤い✕マークが付く）
- `op('node').clearScriptErrors()` : スクリプトエラーをクリア
- `op('node').addWarning("Warning Message")` : 警告（黄色い△マーク）を表示
- `debug("Message")` : テキストポートにデバッグメッセージを出力（`print()`の代わりに使用）

## 6. モジュールとエクステンション (Ext)
- `mod.module_name.FunctionName()` : 同じ階層にあるDATモジュール内の関数を呼び出す（例: `mod.mod_rhythm.get_state()`）
- `op('node').ext.ExtensionClass` : コンポーネントに割り当てられたエクステンションのリソースやメソッドにアクセス

## 7. プロジェクト固有のよく使うTOP/CHOP関連
- **CHOPデータアクセス**: `op('chop_node')['chan_name'][0]` (CHOPの現在値を取得)
- **解像度取得 (TOP)**: `op('top_node').width`, `op('top_node').height`
