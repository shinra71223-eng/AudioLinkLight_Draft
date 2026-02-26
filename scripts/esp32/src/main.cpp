#include <Arduino.h>
#include <FastLED.h>

static constexpr int  NUM_LEDS_A     = 440;
static constexpr int  NUM_LEDS_B     = 440;
static constexpr int  NUM_LEDS_TOTAL = 880;
static constexpr int  PIN_A          = 4;
static constexpr int  PIN_B          = 5;
static constexpr int  MAX_MA         = 3000;
static constexpr long SERIAL_BAUD    = 921600;

CRGB ledsA[NUM_LEDS_A];
CRGB ledsB[NUM_LEDS_B];

static uint8_t rxBuf[NUM_LEDS_TOTAL * 3];
static uint32_t framesReceived = 0;

static constexpr int  COLS          = 88;
static constexpr int  ROWS_PER_STRIP = 5;  // each strip covers 5 rows

void applyFrame(uint16_t count) {
    // ledsA: rows 0-4, each strip is its own serpentine
    for (int i = 0; i < NUM_LEDS_A && i < (int)count; i++) {
        int row_in_strip = i / COLS;           // 0..4
        int col_in_row   = i % COLS;           // 0..87
        int canvas_col   = (row_in_strip % 2 == 0) ? col_in_row : (COLS - 1 - col_in_row);
        int canvas_row   = row_in_strip;       // 0..4
        int src = (canvas_row * COLS + canvas_col) * 3;
        ledsA[i] = CRGB(rxBuf[src], rxBuf[src+1], rxBuf[src+2]);
    }
    // ledsB: rows 5-9, same serpentine pattern within this strip
    for (int i = 0; i < NUM_LEDS_B && (NUM_LEDS_A + i) < (int)count; i++) {
        int row_in_strip = i / COLS;           // 0..4
        int col_in_row   = i % COLS;           // 0..87
        int canvas_col   = (row_in_strip % 2 == 0) ? col_in_row : (COLS - 1 - col_in_row);
        int canvas_row   = ROWS_PER_STRIP + row_in_strip;  // 5..9
        int src = (canvas_row * COLS + canvas_col) * 3;
        ledsB[i] = CRGB(rxBuf[src], rxBuf[src+1], rxBuf[src+2]);
    }
    FastLED.show();
}

void setup() {
    FastLED.addLeds<WS2812B, PIN_A, GRB>(ledsA, NUM_LEDS_A);
    FastLED.addLeds<WS2812B, PIN_B, GRB>(ledsB, NUM_LEDS_B);
    FastLED.setMaxPowerInVoltsAndMilliamps(5, MAX_MA);
    FastLED.setBrightness(10);   // global brightness cap (0-255)
    FastLED.clear(true);

    Serial.begin(SERIAL_BAUD);
    Serial.setTimeout(500);  // readBytes timeout = 500ms
    unsigned long t0 = millis();
    while (!Serial && (millis() - t0) < 3000) { delay(10); }

    // Startup: brief white flash
    fill_solid(ledsA, NUM_LEDS_A, CRGB(30, 30, 30));
    fill_solid(ledsB, NUM_LEDS_B, CRGB(30, 30, 30));
    FastLED.show(); delay(300);
    FastLED.clear(true);
}

void loop() {
    // Step 1: Wait for magic byte 0x55
    if (Serial.available() < 1) return;
    uint8_t b1 = Serial.read();
    if (b1 != 0x55) return;

    // Step 2: Wait for 0xAA (with short timeout)
    unsigned long t0 = millis();
    while (!Serial.available()) {
        if (millis() - t0 > 100) return;
    }
    uint8_t b2 = Serial.read();
    if (b2 != 0xAA) return;

    // Step 3: Read count (2 bytes)
    uint8_t hdr[2];
    size_t got = Serial.readBytes(hdr, 2);
    if (got < 2) return;

    uint16_t count = hdr[0] | ((uint16_t)hdr[1] << 8);
    if (count == 0 || count > NUM_LEDS_TOTAL) return;

    // Step 4: Bulk read all RGB data at once
    uint16_t need = count * 3;
    size_t received = Serial.readBytes(rxBuf, need);

    if (received == need) {
        applyFrame(count);
        framesReceived++;
        // NOTE: Do NOT drain here - next frame may have buffered in USB-CDC during show()
        // Send ACK so host knows we are ready for next frame
        Serial.write('K');
    }
}