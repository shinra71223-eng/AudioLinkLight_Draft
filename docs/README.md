# AudioLinkLight Quick Start Guide

`AudioLinkLight` は、TouchDesigner内で音声信号を**「人間の感情・熱量（Intensity）」**や**「鋭利なリズムトリガー」**として抽出する、軽量で高速なオーディオ解析エンジンです。

---

## 🚀 1. セットアップ（新しいPCの場合）

### 必要なもの
* **TouchDesigner** 2025.3以降
* **Python** 3.10以降（システムにインストール済みであること）
* **インターネット接続**（初回セットアップ時のみ）

### 手順

1. **リポジトリをクローン**（または `.toe` ファイルをコピー）
2. **`setup_env.bat` をダブルクリック**して実行
   - Python仮想環境（`.venv`）が自動作成されます
   - Demucs 4.0.1 + PyTorch 等の依存パッケージがインストールされます
   - **FFmpeg** が自動ダウンロード・配置されます
   - `separated/` `media/music/` 等のフォルダが作成されます
3. **`media/music/` に音楽ファイルを配置**（MP3, WAV, FLAC）
4. **`AudioLinkLight_V00.toe`** をTouchDesignerで開く
5. Textportで以下を実行して音楽フォルダのパスを設定：
   ```python
   exec(open(project.folder + '/scripts/fix_music_paths.py', encoding='utf-8').read())
   ```

> **⚠️ 注意**: `.venv`、`separated/`、`bin/` はGit管理外です。新しいPCでは必ず `setup_env.bat` を実行してください。

---

## 🎵 2. Demucs 自動分離の仕組み

AudioLinkLightは **Demucs** を使って音声を `Vocal` と `Non-Vocal`（Instruments）の2つの波形に自動分離します。

1. `Audio_File_IN_IO` で曲を再生開始
2. `watch_file_io` がファイル変更を自動検知
3. `DemucsBridge` が `separated/` フォルダ内にキャッシュを確認
4. **キャッシュあり** → 即座に分離データを読み込み
5. **キャッシュなし** → Demucsプロセスがバックグラウンドで分離を実行 → 完了後に自動読み込み

> 分離品質は2段階（FAST → HQ）で自動アップグレードされます。

---

## 🎛️ 3. 出力信号一覧

`out1` からは以下のチャンネルが毎フレーム（60fps）出力されます。値は全て **0.0 〜 1.0 に正規化** されています。

### 🎤 ボーカル＆メロディ系
* **`uVocalIntensity`**: ボーカルの「感情曲線」。サスティンや息継ぎ、手数の多さを統合した熱量。
* **`uMelodyIntensity`**: ギターやシンセ等の熱量。

### 🥁 リズム系
* **`Kick`** / **`Snare`** / **`Hihat`** / **`Clap`**: 鋭角的なリズムトリガー。

### 🎸 ベース系
* **`uBassEnergy`**: メインベースライン（動的正規化）
* **`uSubBass`**: 重低音（40Hz付近）
* **`uSidechain`**: キック連動のダッキング信号

---

## 📁 4. プロジェクト構造

```
AudioLinkLight/
├── AudioLinkLight_V00.toe    # メインプロジェクト
├── AudioLinkCore_V01.tox     # コアエンジン（コンポーネント）
├── requirements.txt          # Python依存パッケージ一覧
├── setup_env.bat             # 環境構築スクリプト（新PC用）
├── .gitignore
├── docs/
│   ├── README.md             # このファイル
│   └── Developer_Guide.md   # エンジニア向け技術仕様書
├── scripts/
│   ├── demucs_separator.py   # Demucs分離スクリプト
│   └── dats/                 # parse_*_callbacks のPythonソース
├── .venv/                    # Python仮想環境（Git管理外）
└── separated/                # Demucs分離キャッシュ（Git管理外）
    ├── fast/
    └── hq/
```

---

## 🛠️ 5. 次のステップ

* **中の仕組みを知りたい方** → `Developer_Guide.md` をお読みください
* **VisualEngineへの接続** → `Select CHOP` で `../AudioLinkLight_V01/AudioLinkCore/out1` を参照するだけ！
