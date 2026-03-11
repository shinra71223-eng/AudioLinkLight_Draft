/*
 * ESP32S3_Sub_WiFi.ino
 * =====================
 * ESP-NOW → ESP32-S3 → WS2812B LED Matrix (10x88)
 * 子機用（WiFi受信）
 */

#include <FastLED.h>
#include <WiFi.h>
#include <esp_now.h>

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

// ────────────────────────────────────────────
// LEDバッファ
// ────────────────────────────────────────────
CRGB ledsA[NUM_LEDS_A];
CRGB ledsB[NUM_LEDS_B];
uint8_t imageBuf[FRAME_BYTES];

// ────────────────────────────────────────────
// ターゲット設定（子機ごとに書き換えてください）
// 1: Sub U1, 2: Sub None, 3: Sub D1
// ────────────────────────────────────────────
#define MY_UNIT_ID 1

// ────────────────────────────────────────────
// ESP-NOW パケット構造
// ────────────────────────────────────────────
typedef struct {
  uint8_t targetId;
  uint8_t frameId;
  uint8_t chunkIdx;
  uint8_t data[240];
} __attribute__((packed)) esp_packet_t;

volatile bool frameReady = false;
uint16_t chunksReceivedMask = 0; // 11 chunks = 0b11111111111
uint8_t lastFrameId = 255;

// データ受信時のコールバック
void OnDataRecv(const esp_now_recv_info *recv_info, const uint8_t *incomingData,
                int len) {
  if (len < sizeof(esp_packet_t))
    return;
  esp_packet_t *pkt = (esp_packet_t *)incomingData;

  // 自分宛ではないBroadcastパケットは無視
  if (pkt->targetId != MY_UNIT_ID)
    return;

  // ラグ解消の要：新しいフレーム(TDからの新しい映像)が来たら強制的にマスクをリセット
  if (pkt->frameId != lastFrameId) {
    chunksReceivedMask = 0;
    lastFrameId = pkt->frameId;
  }

  int offset = pkt->chunkIdx * 240;
  int dataLen = len - 3; // header is 3 bytes

  if (offset + dataLen <= FRAME_BYTES) {
    memcpy(imageBuf + offset, pkt->data, dataLen);
    chunksReceivedMask |= (1 << pkt->chunkIdx);

    if (chunksReceivedMask == 0x07FF) {
      frameReady = true;
      // frameReadyを立てるだけで、次のフレームIDが来るまで維持
    }
  }
}

// サーペンタイル（S字）インデックス変換ロジック
void expandToLEDs() {
  // TouchDesignerの画像(imageBuf)は、y=0 が画像の一番下(BOTTOM)。
  // ledsA が上段、ledsB
  // が下段。物理的にも正しい見た目にするためY軸を反転させる。

  // Matrix A (上段5行)
  for (int row_in_a = 0; row_in_a < 5; row_in_a++) {
    int y_physical = row_in_a;  // 上から0〜4番目
    int y_img = 9 - y_physical; // 画像の対応するY座標（反転）

    for (int col = 0; col < NUM_COLS; col++) {
      int col_in_strip = (row_in_a % 2 == 0) ? col : (NUM_COLS - 1 - col);
      int ledIdx = row_in_a * NUM_COLS + col_in_strip;
      int src = (y_img * NUM_COLS + col) * 3;

      ledsA[ledIdx].r = imageBuf[src];
      ledsA[ledIdx].g = imageBuf[src + 1];
      ledsA[ledIdx].b = imageBuf[src + 2];
    }
  }

  // Matrix B (下段5行)
  for (int row_in_b = 0; row_in_b < 5; row_in_b++) {
    int y_physical = 5 + row_in_b; // 上から5〜9番目
    int y_img = 9 - y_physical;    // 画像の対応するY座標（反転）

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
  WiFi.mode(WIFI_STA);

  FastLED.addLeds<WS2812B, PIN_A, GRB>(ledsA, NUM_LEDS_A);
  FastLED.addLeds<WS2812B, PIN_B, GRB>(ledsB, NUM_LEDS_B);
  FastLED.setMaxPowerInVoltsAndMilliamps(5, 5000);

  if (esp_now_init() != ESP_OK)
    return;
  esp_now_register_recv_cb(OnDataRecv);

  Serial.println("Sub Node Ready (10x88 Serpentine, GPIO 1, 3).");
}

void loop() {
  if (frameReady) {
    frameReady = false;
    expandToLEDs();
    FastLED.show();
  }
}
