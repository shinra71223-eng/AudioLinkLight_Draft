/*
 * AudioLinkLight_ESP32_Phase1.ino
 * ================================
 * GLSL → USB Serial → ESP32 → WS2812B LED Matrix
 * Phase 1: 最小構成テスト
 *
 * 【ハードウェア接続】
 *   ESP32 GPIO4  → Matrix A データ線 (上段 5×88 = 440 LED)
 *   ESP32 GPIO5  → Matrix B データ線 (下段 5×88 = 440 LED)
 *   ESP32 GND    → 外部 5V 電源 GND (必ず接続！)
 *   外部 5V 10A+ → LED ストリップ VCC/GND
 *
 * 【シリアルプロトコル】
 *   SOF:      0xFF 0x00  (2バイト)
 *   Matrix A: 1320バイト (440 LED × 3ch)
 *   Matrix B: 1320バイト (440 LED × 3ch)
 *   合計:     2642バイト/フレーム
 *
 * 【必要ライブラリ】
 *   FastLED 3.x (Arduino Library Manager からインストール)
 *
 * 【Arduino IDE 設定】
 *   Board: ESP32 Dev Module
 *   Upload Speed: 921600
 *   CPU Frequency: 240MHz
 */

#include <FastLED.h>

// ────────────────────────────────────────────
// 定数定義
// ────────────────────────────────────────────
#define NUM_COLS      88
#define NUM_ROWS_A    5
#define NUM_ROWS_B    5
#define NUM_LEDS_A    (NUM_COLS * NUM_ROWS_A)   // 440
#define NUM_LEDS_B    (NUM_COLS * NUM_ROWS_B)   // 440
#define PIN_A         4
#define PIN_B         5
#define SERIAL_BAUD   921600
#define FRAME_BYTES   2640   // 2 matrices × 1320 bytes（SOFを除く）
#define MAX_POWER_MA  10000  // 電源 10A 上限（FastLED 保護）

// ────────────────────────────────────────────
// LEDバッファ
// ────────────────────────────────────────────
CRGB ledsA[NUM_LEDS_A];
CRGB ledsB[NUM_LEDS_B];

// 受信バッファ（SOFを除いたデータ分）
uint8_t recvBuf[FRAME_BYTES];

// ────────────────────────────────────────────
// デバッグ用カウンタ
// ────────────────────────────────────────────
uint32_t frameCount = 0;
uint32_t errorCount = 0;
unsigned long lastDebugMs = 0;

// ────────────────────────────────────────────
// Setup
// ────────────────────────────────────────────
void setup() {
    Serial.begin(SERIAL_BAUD);

    // FastLED 初期化（パラレル出力）
    FastLED.addLeds<WS2812B, PIN_A, GRB>(ledsA, NUM_LEDS_A);
    FastLED.addLeds<WS2812B, PIN_B, GRB>(ledsB, NUM_LEDS_B);

    // 電源保護（最大 10A）
    FastLED.setMaxPowerInVoltsAndMilliamps(5, MAX_POWER_MA);

    // 起動確認: 一瞬赤く光らせる
    fill_solid(ledsA, NUM_LEDS_A, CRGB(50, 0, 0));
    fill_solid(ledsB, NUM_LEDS_B, CRGB(50, 0, 0));
    FastLED.show();
    delay(300);
    FastLED.clear(true);

    Serial.println("[AudioLinkLight] Ready. Waiting for frames...");
}

// ────────────────────────────────────────────
// SOFマーカー (0xFF 0x00) を探す
// ────────────────────────────────────────────
bool waitForSOF() {
    // バッファに最低 2 バイトあるまで待つ
    if (Serial.available() < 2) return false;

    uint8_t b0 = Serial.read();
    if (b0 != 0xFF) {
        // SOFではない: スキップして次のバイトへ
        errorCount++;
        return false;
    }

    // 次のバイトを確認（available があれば即読み）
    unsigned long t = millis();
    while (Serial.available() < 1) {
        if (millis() - t > 10) return false;  // 10ms タイムアウト
    }
    uint8_t b1 = Serial.read();
    return (b1 == 0x00);
}

// ────────────────────────────────────────────
// フレーム受信
// ────────────────────────────────────────────
bool receiveFrame() {
    // 2640バイトを受信（タイムアウト付き）
    size_t received = 0;
    unsigned long startMs = millis();

    while (received < FRAME_BYTES) {
        if (millis() - startMs > 200) {
            // 200ms タイムアウト
            errorCount++;
            return false;
        }
        int avail = Serial.available();
        if (avail > 0) {
            int toRead = min((int)(FRAME_BYTES - received), avail);
            Serial.readBytes(recvBuf + received, toRead);
            received += toRead;
        }
    }
    return true;
}

// ────────────────────────────────────────────
// バッファ → LED バッファに展開
// ────────────────────────────────────────────
void expandToLEDs() {
    // Matrix A (先頭 1320 bytes)
    for (int i = 0; i < NUM_LEDS_A; i++) {
        ledsA[i].r = recvBuf[i * 3];
        ledsA[i].g = recvBuf[i * 3 + 1];
        ledsA[i].b = recvBuf[i * 3 + 2];
    }
    // Matrix B (1320〜2639 bytes)
    for (int i = 0; i < NUM_LEDS_B; i++) {
        ledsB[i].r = recvBuf[1320 + i * 3];
        ledsB[i].g = recvBuf[1320 + i * 3 + 1];
        ledsB[i].b = recvBuf[1320 + i * 3 + 2];
    }
}

// ────────────────────────────────────────────
// Loop
// ────────────────────────────────────────────
void loop() {
    if (!waitForSOF()) return;

    if (!receiveFrame()) {
        Serial.println("[WARN] Frame receive timeout");
        return;
    }

    expandToLEDs();
    FastLED.show();
    frameCount++;

    // デバッグ出力（5秒ごと）
    unsigned long now = millis();
    if (now - lastDebugMs >= 5000) {
        Serial.printf("[INFO] Frames: %lu, Errors: %lu, FPS~%.1f\n",
            frameCount, errorCount,
            (float)frameCount / ((now) / 1000.0f));
        lastDebugMs = now;
    }
}
