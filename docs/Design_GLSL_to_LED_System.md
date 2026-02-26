# 設計書：GLSL → WS2812B LED Matrix System
> **プロジェクト:** AudioLinkLight V03_b02  
> **バージョン:** 1.0.0  
> **作成日:** 2026-02-25  
> **対象ファイル:** `AudioLinkLight_V03_b02.toe`

---

## 1. プロジェクト概要

`TEST_SCREEN` コンポーネント内の GLSL TOP（88×10 px）で生成したオーディオリアクティブな映像データを、USBシリアル経由でESP32に送信し、2枚の WS2812B LEDマトリックス（各 5×88 = 440 LED）にリアルタイム表示するシステム。

---

## 2. 既存ノード構成（現在の TEST_SCREEN 内部）

```
sel_audio (selectCHOP)       ← AudioLinkCore/out1
sel_global (selectTOP)       ← GlobalEngine_Canvas/out1
  └─ crop_global (cropTOP)
local_bg (constantTOP)
  └─ circle_kick (circleTOP)
       └─ comp_local (compositeTOP)
            └─ cross_mix (crossTOP)   ← LED生データ 88×10
                 ├─ out_led (outTOP)  ← ★ここからSerialパイプラインへ接続
                 └─ led_glsl (glslTOP) 264×30プレビュー用
                      └─ out_preview (outTOP)
```

**重要：** `out_led` の出力（88×10 px、RGB float）が Serial パイプラインの起点。

---

## 3. 追加するパイプライン（今回の実装対象）

### 3.1 ソフトウェアパイプライン全体図（TD側）

```
cross_mix [88×10]
    │
    ▼
[level_serial] levelTOP
  ・輝度リミッター（Brightness2 パラメータで調整）
  ・60FPS時の電流保護: 全白時でも安全値に抑える
    │
    ▼
[crop_top] cropTOP  → 上段 5×88（Row 0～4）
[crop_bot] cropTOP  → 下段 5×88（Row 5～9）
    │                  │
    └──── layout_10x88 layoutTOP（縦連結: 10×88 再構成）
               │
               ▼
         [top_to_chop] TOP to CHOP
           Download Type: Next Frame（GPU負荷最小）
           Channel: r, g, b
               │
               ▼
         [shuffle_zigzag] Shuffle CHOP
           ジグザグ配線順の並べ替え（後述 §4）
               │
               ▼
         [serial_out] Serial CHOP
           Port:     自動検出（COMx）
           Baud:     921600
           Protocol: One Byte Binary
           Active:   常時 ON
```

### 3.2 ノードパラメータ詳細

| ノード名 | 種別 | 主要パラメータ |
|---|---|---|
| `level_serial` | levelTOP | `brightness2=0.8`（安全輝度）, `clamp=True`, `clamphigh2=0.85` |
| `crop_top` | cropTOP | `croptop=5`, `cropbottom=0`, unit=pixel |
| `crop_bot` | cropTOP | `croptop=10`, `cropbottom=5`, unit=pixel |
| `layout_10x88` | layoutTOP | 2入力縦連結, Output Resolution: 10×88 |
| `top_to_chop` | TOP to CHOP | `downloadtype=nextframe`, `activechops=r g b` |
| `shuffle_zigzag` | Shuffle CHOP | カスタムPythonでジグザグ生成（§4参照）|
| `serial_out` | Serial CHOP | `baudrate=921600`, `format=onebytebinary` |

---

## 4. ジグザグ（蛇行）配線マッピング

WS2812B マトリックスの物理配線は通常「蛇行（Zigzag）」型。

### 4.1 配線パターン

```
Matrix A（上段 GPIO4）: Row 0～4
  Row 0: →  LED 0,  1,  2, ... 87
  Row 1: ←  LED 87, 86, 85, ... 0  ← 折り返し
  Row 2: →  LED 0,  1,  2, ... 87
  Row 3: ←  (同様に折り返し)
  Row 4: →

Matrix B（下段 GPIO5）: Row 5～9（同パターン）
```

### 4.2 ジグザグ変換ロジック

```python
# Shuffle CHOP が参照する Python スクリプト（概要）
# 入力: top_to_chop の r/g/b チャンネル（880サンプル × 3ch）
# 出力: ジグザグ順に並べ替えた r/g/b（880サンプル × 3ch）

def zigzag_index(row, col, width=88):
    """ 物理LED番号 → ピクセル座標への逆変換 """
    if row % 2 == 0:
        return row * width + col          # 偶数行: 左→右
    else:
        return row * width + (width - 1 - col)  # 奇数行: 右→左
```

---

## 5. シリアルデータプロトコル

### 5.1 フレームフォーマット

```
[SOF: 0xFF 0x00]  2バイト（フレーム開始マーカー）
[Matrix A データ: 5×88×3 = 1320バイト]  (R, G, B 各0-255)
[Matrix B データ: 5×88×3 = 1320バイト]
合計: 2 + 2640 = 2642バイト/フレーム
```

### 5.2 帯域計算

| 項目 | 値 |
|---|---|
| 総ピクセル | 880 px |
| バイト数/フレーム | 2642 bytes |
| Baud rate | 921600 bps |
| 理論最大 FPS | 921600 ÷ (2642×10) ≈ **34.8 fps** |
| 現実的 FPS | **30 fps**（安全マージン込み）|

> ⚠️ **60fps は不可能**。TD 側の Serial CHOP は 30fps に落とすこと（`timer` で間引き）。

---

## 6. ESP32 側仕様

### 6.1 ハードウェア構成

| 項目 | 内容 |
|---|---|
| MCU | ESP32 (240MHz dual-core) |
| 通信 | USB-CDC シリアル 921600 baud |
| GPIO4 | Matrix A: 上段 5×88 = 440 LED |
| GPIO5 | Matrix B: 下段 5×88 = 440 LED |
| ライブラリ | FastLED 3.x (`fastled/FastLED @ ^3.9.0`) |
| ビルドツール | **PlatformIO** (`platformio.ini`: env `esp32dev`) |
| 電源 | 外部 5V / 最大 15A ※給電ポイント中継 推奨 |

### 6.2 ESP32 スケッチ骨子（PlatformIO）

**プロジェクト構成:**
```
scripts/esp32/
  platformio.ini      ← ボード/ライブラリ設定
  src/
    main.cpp          ← メインスケッチ
```

**ビルド & 書き込み:**
```bash
# scripts/esp32/ で実行
pio run                      # ビルド
pio run --target upload      # 書き込み
pio device monitor           # シリアルモニタ (921600 baud)
```

**`main.cpp` 骨子:**
```cpp
#include <Arduino.h>
#include <FastLED.h>

#define NUM_LEDS_A 440
#define NUM_LEDS_B 440
#define PIN_A 4
#define PIN_B 5
#define BAUD 921600

CRGB ledsA[NUM_LEDS_A];
CRGB ledsB[NUM_LEDS_B];
uint8_t buf[2642];  // SOF(2) + MatrixA(1320) + MatrixB(1320)

void setup() {
    Serial.begin(BAUD);
    FastLED.addLeds<WS2812B, PIN_A, GRB>(ledsA, NUM_LEDS_A);
    FastLED.addLeds<WS2812B, PIN_B, GRB>(ledsB, NUM_LEDS_B);
    FastLED.setMaxPowerInVoltsAndMilliamps(5, 10000);  // 10A 上限
}

void loop() {
    // SOFマーカー(0xFF 0x00)を待機
    if (Serial.available() < 2) return;
    if (Serial.peek() != 0xFF) { Serial.read(); return; }
    Serial.read(); // 0xFF
    if (Serial.read() != 0x00) return;  // 0x00 確認

    // データ本体 2640 バイト受信
    size_t received = Serial.readBytes((char*)buf, 2640);
    if (received < 2640) return;

    // Matrix A 展開
    for (int i = 0; i < NUM_LEDS_A; i++) {
        ledsA[i] = CRGB(buf[i*3], buf[i*3+1], buf[i*3+2]);
    }
    // Matrix B 展開
    for (int i = 0; i < NUM_LEDS_B; i++) {
        ledsB[i] = CRGB(buf[1320 + i*3], buf[1320 + i*3+1], buf[1320 + i*3+2]);
    }
    FastLED.show();
}
```

---

## 7. 開発フェーズ（マイルストーン）

### Phase 1 — 最小構成テスト（★今日の作業）

**目標:** 8×8 相当のダミーデータが USB 経由で反映されることを確認。

| タスク | 担当 | スクリプト |
|---|---|---|
| TD: `level_serial` → `top_to_chop` → `serial_out` ノードを構築 | TD 側 | `scripts/deploy_serial_pipeline.py` |
| ESP32: 受信→表示の最小スケッチ | PlatformIO | `scripts/esp32/src/main.cpp` |
| 接続テスト（COMポート確認 & 点灯確認） | 手動 | — |

### Phase 2 — パラレル出力実装

**目標:** GPIO4 / GPIO5 への 2 系統同時出力を確認。

- FastLED の `addLeds` を 2 系統に拡張。
- 上段/下段 データ分割の確認。

### Phase 3 — フル解像度 + ジグザグ変換

**目標:** 10×88 フル解像度 + Shuffle CHOP によるジグザグ変換が正しく動く。

- Shuffle CHOP スクリプトを調整しながら LED 実機で目視確認。
- 格子パターン（市松模様）を表示して座標変換の正確性を検証。

### Phase 4 — 輝度リミッター & 安定化

**目標:** 全白点灯時の安全確認 + 60fps→30fps 間引き実装。

- `level_serial` の `brightness2` を調整して電流を 10A 以内に収める。
- Serial CHOP の出力タイミングを 30fps に制限。
- 長時間連続運転テスト（1時間）。

---

## 8. 重要な注意事項

| 項目 | 内容 |
|---|---|
| **GND 共通** | ESP32 の GND と 外部 5V 電源の GND を必ず接続すること |
| **パワーインジェクション** | 5×88 = 440 LED は中間給電必須（端から 44 番目付近）|
| **COMポート** | TD の Serial CHOP の `port` パラメータにデバイスマネージャで確認したポート番号を設定 |
| **SOFマーカー衝突** | 画像データ中に `0xFF 0x00` が出現する確率は低いが、Phase4 で XOR エンコードへの置き換えを検討 |
| **GLSL バージョン** | TD 2025 は GLSL 4.60 標準。`#version 460 core` 明示を推奨 |

---

## 9. 関連ファイル一覧

| ファイル | 役割 |
|---|---|
| `AudioLinkLight_V03_b02.toe` | メインプロジェクト |
| `scripts/deploy_serial_pipeline.py` | TD 側 Serial パイプライン構築スクリプト（Phase1 で作成） |
| `scripts/esp32/platformio.ini` | PlatformIO ボード/ライブラリ設定 |
| `scripts/esp32/src/main.cpp` | ESP32 メインスケッチ（Phase1）|
| `docs/td_api_reference.md` | TD API パラメータ名リファレンス |
| `docs/Manual_Exac_Command.md` | TD Textport 実行方法 |
| `build_test_screen.py` | TEST_SCREEN 構築スクリプト（既存） |
