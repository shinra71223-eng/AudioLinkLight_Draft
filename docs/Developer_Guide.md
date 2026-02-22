# AudioLinkLight V01 Developer Guide
**エンジニア・ハッカー向け完全仕様書**

このドキュメントは、提供された `AudioLinkLight` (音声解析エンジン) の内部構造を理解し、**「独自の楽器解析アルゴリズムの追加」「センサー値の統合（マルチモーダル化）」「ESP32等へのLED制御データの送信」**を行うためのテクニカルガイドです。

---

## 1. 全体アーキテクチャ概要
`AudioLinkLight` は、TouchDesignerの内部で「音声波形」を「描画用・ハードウェア用のリアルタイムパラメータ」へ変換するミドルウェアとして機能します。

```text
[Audio Input] -> [Demucs Separator] -> [AudioLinkLight] -> [Merge (out1)] -> [Visual / ESP32]
```

1. **Demucs 分離エンジン（外部）**: 生のオーディオ信号を `Bass`, `Drums`, `Other(Melody)`, `Vocals` の4つの波形 (CHOP) に分離します。（`demucs_spectrum` ノードとして入力されます）。
2. **AudioLinkLight（コア）**: 4つの波形それぞれに対して**2048サンプルの高解像度FFT**をかけ、成分ごとに最適化された特化型Pythonスクリプト群（Script CHOP）がリアルタイムに感情やリズムをZ-Score・EMAで解析します。
3. **マージノード (out1)**: 各 `parse_*` ノードの出力を1つに束ねます。後段のビジュアルやネットワーク送信は、この `out1` を参照するだけで完結します。

---

## 2. 解析ロジックのハッキングガイド

もし新しい解析を追加したい場合（例：シンバルのクラッシュ専用のトリガーを作りたい等）、既存の `parse_*_callbacks` スクリプトをコピーして内部を改造します。

### 📌 超重要コンポーネント: `ZScoreDetector` と `get_state()`

`AudioLinkLight` の強さの秘訣は、音量が単純に大きい/小さいではなく、**「動的に変化する曲の盛り上がりに合わせて、どれだけ異常値（鋭い立ち上がり）が出たか」**を検知する機能にあります。

*   **`ZScoreDetector` クラス**
    スクリプトの冒頭でインライン定義されています。過去 `N` フレームの平均（Avg）と分散（Std）を記録し、現在の値が「標準偏差何個分ズレているか（Z-Score）」を返します。
    *   `lag=15`: 過去15フレーム分のデータを記憶し、ベースラインとします。
    *   `threshold=1.5`: 標準偏差の1.5倍の「異常な立ち上がり」があった時にトリガー（1.0）を出力します。

*   **`get_state(op_path)` による状態保持**
    TouchDesignerの Python `onCook` コールバックは「毎フレーム呼ばれ、ローカル変数がリセットされる」という仕様です。そのため、前フレームの情報を引き継いだり（EMA計算など）、Z-Scoreの過去配列を保存するためには、この `get_state()` を通じて `scriptOp.storage` （グローバル辞書）にアクセスしてデータを書き込みます。

> **⚠️ 注意事項**: ZScoreDetectorクラス内に `import numpy` は絶対に書かないでください！TouchDesignerのメモリ空間でクラス参照が壊れ、解析が死にます。ネイティブPythonの `sum()` 等を使用してください。

---

## 3. マルチモーダル化への拡張 (Multi-modal Expansion)

現在は「音」だけをソースにしていますが、これを簡単に「LiDARセンサー」や「シリアル通信からの心拍データ（OSC / Serial DAT）」と統合できます。

### 拡張の推奨フロー
1. `AudioLinkLight` 外部（あるいは内部）に `OSC In CHOP` や `Serial DAT -> DAT to CHOP` でセンサーデータを受信します。
2. センサーデータを 0.0〜1.0 に `Math CHOP` で正規化（Normalize）します。
3. `AudioLinkLight` 内の最終段 `out1`（Merge CHOP）の直前に、そのセンサーデータのCHOPを**Merge**で繋ぎ込みます。
4. これにより、フロントエンドの Visual Engine 側は「音データもセンサーデータも、すべて `AudioLinkLight/out1` から同時に取得できる」という美しい設計（単一責任の原則）を保てます。

---

## 4. ESP32 / カスタムLED基板への送信プロトコル

`out1` から出力される0.0〜1.0に正規化された「無駄のない感情データ」は、ESP32のようなマイコンを使ったLEDドライバの制御信号に最適です。

### ハードウェア送信（UDP / OSC）の推奨アーキテクチャ

TouchDesignerの負荷を減らし、かつESP32側でパース（解析）しやすくするため、**JSON形式でのOSC送信、またはシンプル配列のUDPダイレクト送信**を推奨します。

**実装例 (`CHOP Execute DAT` を使用):**
1. `out1` に `Null CHOP` (名前: `to_esp32_null`) を繋げます。
2. そこに `CHOP Execute DAT` を設定し、`Value Change` をオンにします。
3. 以下のようなPythonスクリプトで、毎フレーム（または特定間隔で）ネットワーク送信を行います。

```python
import json

def onValueChange(channel, sampleIndex, val, prev):
    # CHOPの全チャンネル名と値の辞書を作成
    chop = op('to_esp32_null')
    payload = {}
    for i in range(chop.numChans):
        # 0.0 - 1.0 の値を送信サイズ削減のため小数点第3位等に丸める
        payload[chop[i].name] = round(chop[i][0], 3)
        
    # JSON文字列化
    msg = json.dumps(payload)
    
    # UDP Out DAT を通じて ESP32のIPアドレス・ポートへ送信
    op('udp_out_dat').send(msg)
```

**ESP32 側の受信用 C++ (Arduino) 疑似コード:**
```cpp
// ESP32側でJSONをデシリアライズし、LEDへマッピング
StaticJsonDocument<512> doc;
deserializeJson(doc, incomingPacket);

// ボーカルの熱量で全体の色味/明るさをスケーリング
float intensity = doc["uVocalIntensity"]; 
// キックとクラップでフラッシュ
bool isKick = doc["Kick"] > 0.8;
bool isClap = doc["Clap"] > 0.8;

// LEDの更新処理（FastLED等）...
```

### なぜこのデータがLED制御に強いのか？
`uVocalIntensity` は「EMA（指数移動平均）」で極めて滑らかに数値が推移するため、LEDの明るさ（Brightness）に直接代入しても**「チカチカするノイズ」が全く発生しません。**
逆に `Kick` や `Clap` 信号は意図的に「Z-Score」で鋭く立ち上がって「-0.15/frame」で急速に減衰するため、LEDのストロボやフラッシュとして完璧な「キレ」をハードウェアにもたらします。
