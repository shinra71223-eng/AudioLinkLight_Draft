# SCENE_5 "Audio Bloom" 調整ガイド (TD 2025.32050 最適化版)

SCENE_5 の「Audio Bloom」演出を、意図した通りの美しさに仕上げるための手動調整マニュアルです。
現在の「真っ白（飽和）」または「真っ暗」な状態から、キレのあるオーディオリアクティブへと復活させます。

---

## ステップ 0: 音声データの取り込み (Hihat + SoundEnergy)
使うパラメータを `Hihat` と `SoundEnergy` の2つに絞ります。
1.  **SCENE_5** 内の `select_audio` (Select CHOP) を選択。
2.  **`Channel Names`** パラメータを、**`Hihat SoundEnergy`** に書き換えてください。
    *   ※ `uBassEnergy` は今回使用しないため削除します。

## ステップ 1: 音全体のパワーで脈動させる (`shape_pulse` 調整)
1.  **`shape_pulse` (Transform TOP)** を選択。
2.  **Scale X (および Y)** に以下の式を入力してください：
    ```python
    0.4 + (op('select_audio')['SoundEnergy'][0] * 0.4)
    ```
3.  **【真っ白になる問題の最終解決】**
    画像を見ると、背景色はすでに正しく設定されていますが、以下の2点を確認してください：
    *   **場所の確認**: `Background Color` の **4番目の数値ボックス** が Alpha（透明度）です。ここを **`0`** にします。
    *   **Pre-Multiply RGB by Alpha**: これを **`On`** に切り替えてみてください。
    *   **Tile タブ**: 隣の `Tile` タブを開き、**`Extend`** が `Zero`（または `Hold`）になっているか確認してください。ここが `Repeat` だと画面が白く埋まることがあります。
    *   **Pivot**: 0.5に戻しても白くなる場合は 0.4 のままで大丈夫ですが、基本は `0.5` （中心）が推奨です。

1.  **`organic_warp` (Displace TOP)** を選択。
2.  **Displace Weight X (および Y)** に以下の式を入力します：
    ```python
    # select_audio から Hihat の1サンプル目を参照
    0.01 + (op('select_audio')['Hihat'][0] * 0.15)
## ステップ 2: 輪郭をクッキリさせる (`neon_edge` 調整)
円が動くようになったのに `neon_edge` の先が真っ暗な場合は、境界線がボケすぎています。
1.  **`base_shape` (Circle TOP)** を選択。
    *   **`Softness`** を **`0.01`〜`0.05`** 程度まで下げて、境界をパキッとさせます。
2.  **`neon_edge` (Edge TOP)** を選択。
    *   **`Strength`** を大きく（`5.0` など）上げてください。
    *   **`Sample Step`** は `1` にしておきます。
    これで、動く円の縁（フチ）だけが白く光るようになります。

## ステップ 3: フィードバックと残像の調整
1.  **`fb_level` (Level TOP)** :
    *   **`Opacity`** を **`0.9`** 前後に設定します（残像の長さを決めます）。
    *   **`Brightness`** や **`Gamma`** を上げて、残像を明るく保つように調整してください。
2.  **`comp_feedback` (Composite TOP)** :
    *   **`Operation` が **`Maximum`** になっていることを確認してください。
    これで、新しく生まれた光（コア）が、古い光（過去の残像）の上に力強く重なるようになります。

## ステップ 4: 色彩に深みを出す (`color_look` 調整)
1.  **`color_ramp` (Ramp TOP)** の配色を調整します。
    *   左側（暗部用）を完全な黒にし、中間から右側にかけて好きな色（シアン、紫、オレンジなど）を配置します。
    *   一番右端（ハイライト）を白に近い色にすると、コアが発光して見えます。

## ステップ 5: 歪みのアクセント (`organic_warp` 調整)
1.  **`displace1` (Displace TOP)** の `Weight` が、高音（Hihat）で反応しすぎている場合は、倍率を下げて「ピリピリ」と震える程度にします。

---

### 最終チェックリスト
- [ ] 全てのノードの Common タブで **Resolution** が **88x50** になっているか？
- [ ] `comp_feedback` の **Operation** が `Maximum` になっているか？（Add だと白飛びしやすいため）
- [ ] 音がない時に、中央に小さな円（または何もなし）が見える状態か？
