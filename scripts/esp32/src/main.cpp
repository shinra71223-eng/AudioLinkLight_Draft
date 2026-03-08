#include <Arduino.h>
#include <FastLED.h>

// --- 定数定義 ---
#define NUM_COLS 88
#define NUM_ROWS_A 5
#define NUM_ROWS_B 5
#define NUM_LEDS_A 440
#define NUM_LEDS_B 440
#define TOTAL_LEDS 880

// ピン設定 (とりあえず 1, 3 と、Masterで使われる 5, 4 も定義しておく)
// ユーザが物理的にどこに繋いでいるか不明なため、setupで複数定義するか検討
#define PIN_A 1
#define PIN_B 3
#define PIN_STATUS 21 // Stamp S3 Onboard LED
#define BAUD 2000000

CRGB ledsA[NUM_LEDS_A];
CRGB ledsB[NUM_LEDS_B];
uint8_t imageBuf[TOTAL_LEDS * 3];

void expandToLEDs() {
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
  Serial.begin(BAUD);
  Serial.setRxBufferSize(8192);

  pinMode(PIN_STATUS, OUTPUT);
  digitalWrite(PIN_STATUS,
               HIGH); // 消灯(StampS3はActive Lowの場合があるが一旦HIGH)

  FastLED.addLeds<WS2812B, PIN_A, GRB>(ledsA, NUM_LEDS_A);
  FastLED.addLeds<WS2812B, PIN_B, GRB>(ledsB, NUM_LEDS_B);

  FastLED.setMaxPowerInVoltsAndMilliamps(5, 4000);
  FastLED.setBrightness(100);

  // 起動確認: 青色に全点灯
  fill_solid(ledsA, NUM_LEDS_A, CRGB::Blue);
  fill_solid(ledsB, NUM_LEDS_B, CRGB::Blue);
  FastLED.show();
  delay(500);
  FastLED.clear(true);
  FastLED.show();
}

uint32_t lastFrameMs = 0;
bool statusLed = false;

void loop() {
  // 同期処理: 0x55 0xAA を探す
  while (Serial.available() > 0) {
    if (Serial.peek() != 0x55) {
      Serial.read(); // 0x55 以外は捨てる
      continue;
    }

    // 0x55 が見つかったが、バッファに4バイト以上ない場合は次周へ
    if (Serial.available() < 4)
      return;

    Serial.read(); // 0x55
    if (Serial.read() == 0xAA) {
      uint8_t lsb = Serial.read();
      uint8_t msb = Serial.read();
      uint16_t numPixels = lsb | (msb << 8);
      uint16_t numBytes = numPixels * 3;

      if (numBytes == 2640) {
        size_t received = Serial.readBytes(imageBuf, numBytes);
        if (received == numBytes) {
          expandToLEDs();
          FastLED.show();

          // ステータスLEDを反転 (受信している証拠)
          statusLed = !statusLed;
          digitalWrite(PIN_STATUS, statusLed ? LOW : HIGH);
          lastFrameMs = millis();
        }
      }
    }
  }

  // 1秒以上受信がない場合は青色のまま（または消灯）
  if (millis() - lastFrameMs > 1000) {
    // digitalWrite(PIN_STATUS, HIGH);
  }
}
