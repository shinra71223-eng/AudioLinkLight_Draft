#include <FastLED.h>
#include <WiFi.h>
#include <WiFiUdp.h>

/**
 * ESP32S3_Master_Professional_UDP.ino
 * ===================================
 * 1. USBバルク・リード & 20,000,000 bps 対応
 * 2. ダブルバッファ（Ping-Pong）による描画・通信の完全非同期
 * 3. デュアルコア（Core 0: IO, Core 1: Render）
 * 4. ゼロ・コピー UDP 分割送信 (1,320 bytes x 2)
 */

// ────────────────────────────────────────────
// 定数定義 (12x81 = 972 LEDs)
// ────────────────────────────────────────────
#define NUM_COLS 81
#define NUM_ROWS 12
#define NUM_LEDS (NUM_COLS * NUM_ROWS)
#define PIN_LED 5

// データサイズ計算
#define SLAVE_DATA_SIZE (10 * 88 * 3)                             // 2640 bytes
#define MASTER_DATA_SIZE (NUM_LEDS * 3)                           // 2916 bytes
#define TOTAL_DATA_BYTES (SLAVE_DATA_SIZE * 3 + MASTER_DATA_SIZE) // 10836 bytes

// WiFi / UDP 設定
const char *ssid = "AudioLinkMaster";
const char *password = "password123";
WiFiUDP udp;
// 子機へのブロードキャストIP (SoftAPでは通常 192.168.4.255)
IPAddress broadcastIP(192, 168, 4, 255);
const int udpPort = 1234;

// ────────────────────────────────────────────
// ダブルバッファ（Ping-Pong）
// ────────────────────────────────────────────
uint8_t bufferA[TOTAL_DATA_BYTES];
uint8_t bufferB[TOTAL_DATA_BYTES];
volatile uint8_t *pWrite = bufferA;
volatile uint8_t *pRead = bufferB;
volatile bool dataReady = false;

CRGB leds[NUM_LEDS];

// ────────────────────────────────────────────
// 補助関数
// ────────────────────────────────────────────
uint16_t getSerpentineIndex(uint8_t x, uint8_t y) {
  if (y % 2 == 0)
    return (y * NUM_COLS) + x;
  else
    return (y * NUM_COLS) + (NUM_COLS - 1 - x);
}

// ────────────────────────────────────────────
// Core 0: I/O タスク (USB受信 & WiFi送信)
// ────────────────────────────────────────────
void ioTask(void *pvParameters) {
  while (true) {
    // 1. USBバルク・リード (0x55 0xAA ヘッダー待機)
    if (Serial.available() >= 4) {
      if (Serial.read() == 0x55 && Serial.read() == 0xAA) {
        Serial.read();
        Serial.read(); // dummy

        // メモリへの一括展開 (最適化点 1 & 2)
        Serial.readBytes((uint8_t *)pWrite, TOTAL_DATA_BYTES);

        // ポインタスワップ (最適化点 2)
        volatile uint8_t *temp = pWrite;
        pWrite = pRead;
        pRead = temp;
        dataReady = true;

        // 2. ゼロコピー UDP 分割送信 (最適化点 4)
        // ※各子機は自分のパケットを見分ける必要があるため、
        //   ここでは簡単のため Unicast またはヘッダー付きで送信します。
        //   今回は簡単のため、Broadcast IPに対して「SlaveID +
        //   ChunkID」を付与して送信します。
        for (int s = 0; s < 3; s++) {
          int offset = s * SLAVE_DATA_SIZE;
          for (int c = 0; c < 2; c++) {
            udp.beginPacket(broadcastIP, udpPort);
            uint8_t header[2] = {(uint8_t)s,
                                 (uint8_t)c}; // [0]:SlaveID, [1]:ChunkID
            udp.write(header, 2);
            udp.write((const uint8_t *)(pRead + offset + (c * 1320)), 1320);
            udp.endPacket();
          }
        }

        Serial.write('K'); // TouchDesigner への応答
      }
    }
    vTaskDelay(1);
  }
}

void setup() {
  // USB Rx バッファ拡張 (最適化点 1)
  Serial.setRxBufferSize(16384);
  Serial.begin(20000000);

  // FastLED 初期化
  FastLED.addLeds<WS2812B, PIN_LED, GRB>(leds, NUM_LEDS);
  FastLED.setMaxPowerInVoltsAndMilliamps(5, 5000);

  // WiFi SoftAP 構築 (最適化点 4)
  WiFi.softAP(ssid, password);
  udp.begin(udpPort);

  // Core 0 で I/O タスク（受信・通信）を開始 (最適化点 3)
  xTaskCreatePinnedToCore(ioTask, "ioTask", 8192, NULL, 1, NULL, 0);

  Serial.println("Professional UDP Master Ready.");
}

// ────────────────────────────────────────────
// Core 1: Render ループ (描画専念)
// ────────────────────────────────────────────
void loop() {
  if (dataReady) {
    dataReady = false;

    // バッファ末尾の自機データを展開 (最適化点 2)
    const uint8_t *masterData =
        (const uint8_t *)(pRead + (SLAVE_DATA_SIZE * 3));
    for (uint8_t y_img = 0; y_img < NUM_ROWS; y_img++) {
      uint8_t y_physical = (NUM_ROWS - 1) - y_img;
      for (uint8_t x = 0; x < NUM_COLS; x++) {
        uint16_t ledIdx = getSerpentineIndex(x, y_physical);
        uint16_t bufIdx = (y_img * NUM_COLS + x) * 3;
        leds[ledIdx].r = masterData[bufIdx];
        leds[ledIdx].g = masterData[bufIdx + 1];
        leds[ledIdx].b = masterData[bufIdx + 2];
      }
    }
    // 表示実行 (最適化点 3)
    FastLED.show();
  }
}
