#include <Arduino.h>
#include <FastLED.h>

// --- 定数定義 (12x81 = 972 LEDs) ---
#define NUM_COLS 81
#define NUM_ROWS 12
#define NUM_LEDS (NUM_COLS * NUM_ROWS) // 972
#define PIN_LED 5                      // UNIT4 データピン
#define BAUD 2000000

CRGB leds[NUM_LEDS];
uint8_t imageBuf[NUM_LEDS * 3]; // 2916 bytes

void expandToLEDs() {
  for (int y_img = 0; y_img < NUM_ROWS; y_img++) {
    for (int x = 0; x < NUM_COLS; x++) {
      int col_in_strip = (y_img % 2 == 0) ? x : (NUM_COLS - 1 - x);
      int ledIdx = y_img * NUM_COLS + col_in_strip;
      int src = (y_img * NUM_COLS + x) * 3;
      leds[ledIdx].r = imageBuf[src];
      leds[ledIdx].g = imageBuf[src + 1];
      leds[ledIdx].b = imageBuf[src + 2];
    }
  }
}

void setup() {
  Serial.begin(BAUD);
  Serial.setRxBufferSize(8192);
  FastLED.addLeds<WS2812B, PIN_LED, GRB>(leds, NUM_LEDS);
  FastLED.setMaxPowerInVoltsAndMilliamps(5, 4000);
  FastLED.setBrightness(50);
  fill_solid(leds, NUM_LEDS, CRGB::Blue);
  FastLED.show();
  delay(500);
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
      if (numBytes == sizeof(imageBuf)) {
        size_t received = Serial.readBytes(imageBuf, numBytes);
        if (received == numBytes) {
          expandToLEDs();
          FastLED.show();
        }
      }
    }
  }
}
