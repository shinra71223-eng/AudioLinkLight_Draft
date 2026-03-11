#include <Arduino.h>
#include <FastLED.h>

// --- 定数定義 (10x88 = 880 LEDs) ---
#define NUM_COLS 88
#define NUM_ROWS_A 5
#define NUM_ROWS_B 5
#define NUM_LEDS_A 440
#define NUM_LEDS_B 440
#define TOTAL_LEDS 880

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
      int col_in_strip = (row_in_b % 2 == 0)
                             ? col
                             : (NUM_COLS - 1 - col); // Correction: row_in_b % 2
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
  digitalWrite(PIN_STATUS, HIGH);

  FastLED.addLeds<WS2812B, PIN_A, GRB>(ledsA, NUM_LEDS_A);
  FastLED.addLeds<WS2812B, PIN_B, GRB>(ledsB, NUM_LEDS_B);
  FastLED.setMaxPowerInVoltsAndMilliamps(5, 4000);
  FastLED.setBrightness(100);

  // --- 診断用テスト点灯 (青色で1秒間) ---
  fill_solid(ledsA, NUM_LEDS_A, CRGB::Blue);
  fill_solid(ledsB, NUM_LEDS_B, CRGB::Blue);
  FastLED.show();
  delay(1000);
  // ------------------------------------

  FastLED.clear(true);
  FastLED.show();
}

void loop() {
  while (Serial.available() > 0) {
    if (Serial.peek() != 0x55) {
      Serial.read();
      continue;
    }
    if (Serial.available() < 4)
      return;
    Serial.read();
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
          digitalWrite(PIN_STATUS, !digitalRead(PIN_STATUS));
        }
      }
    }
  }
}
