/**
 * ESP32S3_Sub_Professional_UDP.ino
 * ================================
 * 1. WiFi STA モードで親機(AudioLinkMaster)に接続
 * 2. UDP ポート 1234 で待機
 * 3. 2分割されたパケット (1320 bytes x 2) を受信して合体
 * 4. 受信完了後、即座に描画 (10x88, GPIO 1 & 3)
 */

#include <FastLED.h>
#include <WiFi.h>
#include <WiFiUdp.h>

// ────────────────────────────────────────────
// 定数定義 (子機: 10x88)
// ────────────────────────────────────────────
#define NUM_COLS 88
#define NUM_ROWS_A 5
#define NUM_ROWS_B 5
#define NUM_LEDS_A (NUM_COLS * NUM_ROWS_A)   // 440
#define NUM_LEDS_B (NUM_COLS * NUM_ROWS_B)   // 440
#define TOTAL_LEDS (NUM_LEDS_A + NUM_LEDS_B) // 880
#define PIN_A 1                              // GPIO 1 (D+)
#define PIN_B 3                              // GPIO 3 (D-)
#define FRAME_BYTES (TOTAL_LEDS * 3)         // 2640 bytes

// ネットワーク設定
const char *ssid = "AudioLinkMaster";
const char *password = "password123";
WiFiUDP udp;
const int udpPort = 1234;

// バッファ
CRGB ledsA[NUM_LEDS_A];
CRGB ledsB[NUM_LEDS_B];
uint8_t imageBuf[FRAME_BYTES];
bool chunkReceived[2] = {false, false};

void expandToLEDs() {
  // Y軸反転等のロジックは従来通り継承
  for (int row_in_a = 0; row_in_a < 5; row_in_a++) {
    int y_physical = row_in_a;
    int y_img = 9 - y_physical;
    for (int col = 0; col < NUM_COLS; col++) {
      int col_in_strip = (row_in_a % 2 == 0) ? col : (NUM_COLS - 1 - col);
      int ledIdx = row_in_a * NUM_COLS + col_in_strip;
      int src = (y_img * NUM_COLS + col) * 3;
      ledsA[ledIdx].r = imageBuf[src];
      ledsA[ledIdx].g = imageBuf[src + 1];
      ledsA[ledIdx].b = imageBuf[src + 2];
    }
  }
  for (int row_in_b = 0; row_in_b < 5; row_in_b++) {
    int y_physical = 5 + row_in_b;
    int y_img = 9 - y_physical;
    for (int col = 0; col < NUM_COLS; col++) {
      int col_in_strip = (row_in_b % 2 == 0) ? col : (NUM_COLS - 1 - col);
      int ledIdx = row_in_b * NUM_COLS + col_in_strip;
      int src = (y_img * NUM_COLS + col) * 3;
      ledsB[ledIdx].r = imageBuf[src];
      ledsB[ledIdx].g = imageBuf[src + 1];
      ledsB[ledIdx].b = imageBuf[src + 2];
    }
  }
}

void setup() {
  Serial.begin(115200);

  // WiFi 接続
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConnected to Master.");
  udp.begin(udpPort);

  FastLED.addLeds<WS2812B, PIN_A, GRB>(ledsA, NUM_LEDS_A);
  FastLED.addLeds<WS2812B, PIN_B, GRB>(ledsB, NUM_LEDS_B);
  FastLED.setMaxPowerInVoltsAndMilliamps(5, 5000);
}

void loop() {
  int packetSize = udp.parsePacket();
  if (packetSize > 0) {
    // パケット受信
    uint8_t packetBuffer[1500];
    udp.read(packetBuffer, 1500);

    // ヘッダー解析 ([0]: chunkIdx)
    uint8_t chunkIdx = packetBuffer[0];
    if (chunkIdx < 2) {
      memcpy(imageBuf + (chunkIdx * 1320), packetBuffer + 1, 1320);
      chunkReceived[chunkIdx] = true;
    }

    // 両方のチャンクが揃ったら描画
    if (chunkReceived[0] && chunkReceived[1]) {
      chunkReceived[0] = false;
      chunkReceived[1] = false;
      expandToLEDs();
      FastLED.show();
    }
  }
}
