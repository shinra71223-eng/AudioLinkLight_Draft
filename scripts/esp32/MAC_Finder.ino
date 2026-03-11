/*
 * MAC_Address_Finder.ino
 * =======================
 * このスケッチをESP32に書き込み、シリアルモニタを開くと
 * その個体のMACアドレスが表示されます。
 * 4台それぞれのMACアドレスをメモしてください。
 */

#include <WiFi.h>

void setup() {
  Serial.begin(115200);
  WiFi.mode(WIFI_MODE_STA);
  delay(100);
  Serial.println("");
  Serial.print("ESP32 MAC Address: ");
  Serial.println(WiFi.macAddress());
}

void loop() { delay(1000); }
