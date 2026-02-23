# 【他のAI用】TouchDesigner GLSL専用プロンプト（指示書）

このガイドラインは、他のAI（ChatGPTやClaudeなど）に「TouchDesignerのネットワーク構築」ではなく、**「私たちの88x10 LEDシステム上で動く専用のGLSLコード」だけを書かせるためのプロンプト**です。

以下の点線（---）で囲まれた部分をコピーして、他のAIに貼り付けるだけで、この環境に一発で適合する「ピクセルアート/ドット時計」のシェーダーコードを出力してくれます。

---
## 役割と目的
あなたはプロフェッショナルのGLSLシェーダーエンジニアです。
TouchDesignerの `GLSL TOP` 内で実行される「88x10 解像度のサイバーパンクLEDディスプレイ」のためのジェネラティブ・アート（またはデジタル時計）のコードを作成してください。

**重要視すること：**
TouchDesignerのノード構成（CHOPやTOPの繋ぎ方等）は絶対に提案しないでください。すでにネットワーク設計は完了しています。あなたは「GLSL TOPのピクセルシェーダーコードの中身（`glsl_pixel` DATの内容）」だけを記述してください。

## ハードウェアの仕様（制約事項）
1. **実質解像度は 88x10 です。**
2. **GLSLの出力解像度は 264x30 です。** （実質解像度の縦横3倍）
3. **物理LEDのシミュレーション構造**
   出力される264x30のキャンバスは、88x10個の「3x3ピクセルのセル」に分割されます。
   ハードウェアの物理的な隙間を再現するため、各3x3セルのうち**「中心の1ピクセル（ローカル座標 x=1, y=1）」しか発光（色を出力）させてはいけません。**
   残りの外周8ピクセルは**必ず黒 `vec4(0.0, 0.0, 0.0, 1.0)` を出力する**必要があります。
4. **入力テクスチャ**
   `sTD2DInputs[0]` に、ベースとなる 88x10 解像度の映像（Global Canvas）が入ってきます。

## ベースとなるGLSLテンプレート
あなたがコードを書く際は、以下のテンプレート構造を必ず守り、`// ★ここにジェネラティブ・アートや時計の描画ロジックを記述` の部分を構築して `finalColor` に代入してください。

```glsl
uniform float uTime;   // absTime.seconds
uniform float uClap;   // AudioLinkCore: Clap (0.0 - 1.0+)
uniform float uVocal;  // AudioLinkCore: VocalIntensity (0.0 - 1.0+)
uniform float uBass;   // AudioLinkCore: BassEnergy (0.0 - 1.0+)
uniform float uHihat;  // AudioLinkCore: Hihat (0.0 - 1.0+)

// 時計などのリアルタイム要件がある場合、以下のUniformも使用可能（Python側で渡します）
uniform float uHour;   // 現在の時 (0 - 23)
uniform float uMinute; // 現在の分 (0 - 59)
uniform float uSecond; // 現在の秒 (0 - 59)

out vec4 fragColor;

void main()
{
    // 出力解像度 (264x30)
    vec2 outRes = uTDOutputInfo.res.zw;
    // 実質キャンバス解像度 (88x10)
    vec2 inRes = uTDOutputInfo.res.zw / 3.0;
    
    // ピクセルの整数座標
    vec2 pixelCoord = floor(vUV.st * outRes);
    
    // 自分が属する88x10のセル番号 (x: 0...87, y: 0...9)
    vec2 cellIndex = floor(pixelCoord / 3.0);
    
    // 3x3セルのローカル座標 (0, 1, 2)
    vec2 posInCell = mod(pixelCoord, 3.0);
    
    if (posInCell.x == 1.0 && posInCell.y == 1.0) {
        // --- 1. ベース映像の取得 ---
        // テクセルの中央をサンプリング
        vec2 sampleUV = (cellIndex + vec2(0.5)) / inRes;
        vec4 baseColor = texture(sTD2DInputs[0], sampleUV);
        
        vec3 finalColor = baseColor.rgb;
        
        // --- 2. ピクセルアート描画ロジック ---
        // ここから下で cellIndex (0~87, 0~9) を使って、
        // どのLEDをどう光らせるかのアルゴリズムを組み立ててください。
        // 時計を作る場合は、数字を表す3x5などのドットマトリクス配列を定義し、
        // uHour, uMinute, uSecond を参照して描画してください。
        
        // ★ここにジェネラティブ・アートや時計の描画ロジックを記述
        // 例: finalColor = myClockColor + myGlitchArtColor;
        
        // -------------
        
        fragColor = vec4(finalColor, 1.0);
    } else {
        // ハードウェアLEDの隙間は常に黒
        fragColor = vec4(0.0, 0.0, 0.0, 1.0);
    }
}
```

## あなた（AI）への要求タスク
上記のテンプレートを改変し、引数 `cellIndex` と時間を活用して、88x10キャンバス上で動作するジェネラティブなサイバーパンク・デジタル時計（リアルタイム時刻同期）と、音（Bassなど）に反応するグリッチアートを組み合わせたGLSLコードを1つのブロックで出力してください。
---
