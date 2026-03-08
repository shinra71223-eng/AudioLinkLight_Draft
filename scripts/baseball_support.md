# SCENE_6 テキスト描画システム ガイド

## 概要: ビットマップフォントシステム

SCENE_6 のメインテキストは、TouchDesigner の Text TOP ではなく、
**カスタム 8×8 ビットマップフォント**で描画されています。

### パイプライン構成

```
font_8x8.bin → data_texture (Script TOP) → glsl_baseball
                                              ↓
narrative_table (Table DAT) ────────────┘     comp_layers → scene_out
                                              ↑
font_8x8.bin → data_texture_batter (Script TOP) → glsl_batter_support
narrative_table_batter (Table DAT) ────────────┘
                                              ↑
font_8x8.bin → data_texture_pitcher (Script TOP) → glsl_pitcher_support
narrative_table_pitcher (Table DAT) ────────────┘
```

## ⚠️ 注意ポイント

### 1. Text TOP は使用禁止
`text_generator` や TD の Text TOP をシェーダーの入力にしないこと。
TD のフォントレンダリング（Courier New 等）は sub-pixel 単位で描画するため、
8×8 グリッドと正確に一致せず、文字が崩れます。

### 2. テクスチャサイズは 2048×128 固定
シェーダー内の座標計算式:
```glsl
float u = (float(lx) + 0.5) / 2048.0;
float v = (float(row * 8 + ly) + 0.5) / 128.0;
```
この式の `2048.0` と `128.0` は変更不可。変更すると全テキストが崩壊します。

### 3. inputfiltertype = nearest 必須
GLSL TOP のフィルタは必ず `nearest` (menuIndex=0) にすること。
`linear` だと隣接ピクセルが混合され、8px 文字が 7px のように見えます。

### 4. font_8x8.bin のフォーマット
- 256文字 × 8×8 ピクセル
- numpy 配列: shape (8, 256, 8), dtype uint8
- 読み込み後に `np.flip(axis=0)` で TD 座標系に変換

### 5. narrative_table のフォーマット
- Table DAT (タブ区切り)
- 行 = ステート (0-15)
- 列 = 文字位置 (0-255)  
- セル値 = ASCII コード (例: 'A' = 65)

## 座標マッピング

| レイヤー | 表示帯 (LED Y) | テキスト行 (ty) | スライド方向 | 色 |
|---|---|---|---|---|
| Pitcher | 30-39 | cy - 31 (0-7) | 左→右 | 紺 (0,0,0.4) |
| Main | 20-29 | cy - 21 (0-7) | 各種 | 白/色付き |
| Batter | 10-19 | cy - 11 (0-7) | 右→左 | エンジ (0.5,0,0) |

## タイミング
- フレーム 0-269: メイン情報のみ表示
- フレーム 270+: 応援メッセージがスライドイン (45フレームかけて)
