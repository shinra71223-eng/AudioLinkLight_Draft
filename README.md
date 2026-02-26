# AudioLinkLight

TouchDesigner + ESP32-S3 + WS2812B LED (880個) のリアルタイム映像配信システム。

音楽をDemucsでリアルタイム分離し、各パート（vocals / bass / drums / melody）に反応するビジュアルをTDで生成、ESP32-S3を経由して880個のLEDに送出します。

---

## システム構成

```
音源 (MP3)
  └─ Demucs (Python) ─→ 分離音声ストリーム (vocal / bass / hihat / clap / melody)
       └─ AudioLinkCore (TD COMPonent) ─→ Uniforms
            └─ GLSL TOP (cyber_clock_v2 等) ─→ 88×10px 映像
                 └─ led_exec (Execute DAT, pyserial)
                      └─ ESP32-S3 (COM6, 921600baud)
                           ├─ GPIO4 → WS2812B ledsA (440個, 行 0-4, サーペンタイン)
                           └─ GPIO5 → WS2812B ledsB (440個, 行 5-9, サーペンタイン)
```

### LED配線（サーペンタイン）

各ストリップ（ledsA / ledsB）内で独立したサーペンタイン配線:

- 偶数行 (0, 2, 4) : 左 → 右
- 奇数行 (1, 3) : 右 → 左

---

## 必要なもの

### ハードウェア
- ESP32-S3 (USB-CDC対応モデル)
- WS2812B LED ストリップ × 880個（88列 × 10行）
- 5V 電源（LED用、最大 880 × 60mA = 52.8A ただし輝度=10/255なので実際は低い）

### ソフトウェア
- [TouchDesigner](https://derivative.ca/) 2023.11760 以降
- Python 3.11（TD内蔵）
- [PlatformIO](https://platformio.org/)（ESP32ファームウェアビルド用）

---

## セットアップ

### 1. リポジトリをクローン

```bash
git clone https://github.com/<your-account>/AudioLinkLight.git
cd AudioLinkLight
```

### 2. Python仮想環境のセットアップ

```bat
setup_env.bat
```

これで `.venv/` が作成され、Demucs・pyserial 等がインストールされます。

### 3. ESP32ファームウェアのフラッシュ

```bash
cd scripts/esp32

# COMポートを platformio.ini の upload_port に合わせて変更してから:
pio run --target upload
```

> **注意**: フラッシュ時はTD (pyserial) を停止させてからCOMポートを解放してください。  
> pyserialが占有している場合は ESP32の BOOT + RST でブートローダーモード（別COMポート）に入ってからフラッシュします。

### 4. COMポートの設定

`scripts/dats/led_sender_pyserial.py` の先頭にある設定を環境に合わせて変更:

```python
PORT    = 'COM6'    # ← 自分の環境のCOMポートに変更
BAUD    = 921600
```

PlatformIO でも `scripts/esp32/platformio.ini` の `upload_port` を同様に変更してください。

### 5. TDでプロジェクトを開く

`AudioLinkLight_V01.toe` を TouchDesigner で開きます。

### 6. 音楽ファイルの配置

`media/music/` ディレクトリを作成し、MP3ファイルを配置してください（リポジトリには含まれていません）。

### 7. LEDパターンのセットアップ

TDのTextportで以下のいずれかを実行してパターンを作成します:

```python
# 光の雨（データストリーム）
exec(open(project.folder + '/scripts/setup_rain.py', encoding='utf-8').read())

# レインボースクロール
exec(open(project.folder + '/scripts/setup_rainbow.py', encoding='utf-8').read())
```

その後、`TEST_SCREEN` 内の `led_source` の入力を任意のパターンTOPに繋ぎ替えてください。

---

## パターン切り替え

| 表示 | led_source の入力 |
|------|-----------------|
| 光の雨（データストリーム） | `pat_rain` |
| レインボースクロール | `pat_rainbow` |
| サイバー時計 | `clock_source` |

---

## LED通信プロトコル

```
[0x55][0xAA][count_lo][count_hi][R][G][B] × 880
```

- ヘッダ: `0x55 0xAA`
- 総バイト数: 2644 bytes / フレーム
- ACKプロトコル: ESP32が `FastLED.show()` 完了後に `'K'` を返送
- TD側は 60ms 以内に ACK を受信してから次フレームを送信

---

## 他PCで動かすときの注意点

1. **COMポート番号が異なる**  
   デバイスマネージャーで ESP32-S3 の COMポートを確認し、以下の2ファイルを更新してください:
   - `scripts/dats/led_sender_pyserial.py` の `PORT = 'COMx'`
   - `scripts/esp32/platformio.ini` の `upload_port = COMx`

2. **pyserialのパスが異なる**  
   `led_sender_pyserial.py` の先頭に `sys.path` を追加している場合は環境に合わせて変更してください。  
   デフォルトは PlatformIO のpenv（`~/.platformio/penv/Lib/site-packages`）を参照しています。

3. **ESP32のUSB-CDCドライバ**  
   初回接続時は Windows がドライバを自動インストールしますが、認識されない場合は [Silicon Labs CP210x](https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers) または [CH343](https://www.wch-ic.com/downloads/CH343SER_ZIP.html) ドライバをインストールしてください（ESP32-S3のモデルによる）。

4. **DTR/RTS を False に設定**  
   pyserial で ESP32-S3 に接続する際は必ず `dtr=False, rts=False` を指定してください。設定しないとリセットが誤作動します。

5. **PlatformIO の環境確認**  
   `pio run` 前に `pio pkg update` を実行してパッケージを最新にしてください。

6. **TouchDesignerのバージョン**  
   TD 2023.11760 以降を推奨します。古いバージョンでは GLSL コンパイラの挙動が異なる場合があります。

7. **音楽ファイルは含まれていません**  
   `media/music/` ディレクトリを作成して MP3 を配置してください。

8. **Demucsのモデルダウンロード**  
   初回実行時に Demucs のモデルファイル（約1GB）が自動ダウンロードされます。ネットワーク接続が必要です。

9. **OneDriveやDropboxの同期フォルダに置かない**  
   `.pio/` の大量ビルドファイルが同期されてパフォーマンスが低下します。ローカルドライブに clone することを推奨します。

10. **TDのプロジェクトパス**  
    スクリプト内のパス `/AudioLinkLight_V01/...` はTDのコンポーネント内部パスです。`.toe` ファイルを開いた後、Textportでスクリプトを実行してください。

---

## ファイル構成

```
scripts/
  esp32/            ESP32ファームウェア (PlatformIO)
    src/main.cpp    メインファームウェア (FastLED + USB-CDC ACK)
    platformio.ini
  dats/
    led_sender_pyserial.py   TD Execute DAT (LED送信ループ)
  cyber_clock_v2.glsl        サイバー時計 GLSL シェーダー
  rain_shader.glsl            光の雨 GLSL シェーダー
  setup_rain.py               光の雨パターン セットアップスクリプト
  setup_rainbow.py            レインボーパターン セットアップスクリプト
  deploy_led_sender.py        led_exec Execute DAT デプロイスクリプト
  deploy_cyber_clock_v2.py   cyber_clock_v2 GLSL TOP デプロイスクリプト
media/
  music/            音楽ファイル置き場 (gitignore済み、各自用意)
requirements.txt    Python依存パッケージ
setup_env.bat       環境構築バッチ
```