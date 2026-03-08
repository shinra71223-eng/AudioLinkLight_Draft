# AudioLinkCore: `parse_soundenergy` 追加ガイド

既存の解析ロジック（KickやSnareなど）に影響を与えず、純粋な音の「エネルギー量（音量感）」を抽出するノードを追加する手順です。

---

## ステップ 1: ノードの作成と接続
1.  **AudioLinkCore** の中に入ります。
2.  **Script CHOP** を新規作成し、名前を **`parse_soundenergy`** に変更します。
3.  **`demucs_spectrum`** (または `in1`) から、作成した `parse_soundenergy` へ線をつなぎます。
4.  解析結果を外部に送るため、`parse_soundenergy` の出力を **`Merge CHOP` (out1)** に接続します。

## ステップ 2: パラメータ設定
1.  `parse_soundenergy` の Common タブなどにある **`Script`** パラメータの `Setup` ボタン、または `Callbacks` DAT を開きます。
2.  以下の Python コードを貼り付けてください。

### 解析用 Python コード (Callbacks)
このコードは、入力された全サンプルの自乗平均平方根 (RMS) を計算し、音の「重み（エネルギー）」を 1つ の数値として出力します。

```python
import numpy as np

def onCook(scriptOp):
    # 入力CHOPの取得
    in_chop = scriptOp.inputs[0]
    if not in_chop:
        return

    # 重要: 出力を 1 サンプルに固定する (最新TDの推奨設定)
    # これをしないと入力(22,050サンプル)を継承してしまい、式でエラーが出ます
    scriptOp.numSamples = 1
    scriptOp.timeSlice = True # タイムスライスを有効にする

    # 出力チャンネルの準備
    if 'SoundEnergy' not in [c.name for c in scriptOp.chans()]:
        scriptOp.appendChan('SoundEnergy')

    # NumPy配列としてデータを一括取得 (22,050サンプルを高速処理)
    samples = in_chop.numpyArray()
    
    # エネルギー計算 (RMS: 自乗平均平方根)
    rms = np.sqrt(np.mean(np.square(samples)))
    
    # スペクトルデータは値が非常に小さいため、感度調整（ゲイン）と
    # ノイズ対策（しきい値処理）を組み合わせます
    gain = 2500.0
    threshold = 0.00001
    
    if rms >= threshold:
        final_val = rms * gain
    else:
        final_val = 0
    
    # 出力値の書き込み
    scriptOp.chan('SoundEnergy')[0] = final_val
```

> [!IMPORTANT]
> **なぜNumPyが必要なのか？**
> `demucs_spectrum` は1フレームに **22,050個** ものサンプルを出力しています。
> 通常の Python 形式 (`for s in c:`) でこれを回すと、毎秒60回、計130万回以上のループが発生し、**TouchDesignerの動作が劇的に重くなります（カクつきます）。**
> `numpyArray()` を使えば、この22,050サンプルをC言語レベルの速度で一瞬で計算できるため、パフォーマンスへの影響をほぼゼロにできます。

## ステップ 3: 動作確認
1.  **AudioLinkCore/out1** (Merge CHOP) を確認し、新しく `SoundEnergy` というチャンネルが増えていることを確認します。
2.  音が鳴っている時に、この値が 0.0〜1.0 付近で動いていれば成功です。

---

## ステップ 4: SCENE_5 での利用
SCENE_5 内の **`select_audio`** (Select CHOP) の `Channel Names` に **`SoundEnergy`** を追記することで、シーン側でもこの純粋なエネルギー値を参照できるようになります。
