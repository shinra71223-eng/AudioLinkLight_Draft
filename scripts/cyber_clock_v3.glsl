// =========================================================================
// Cyberpunk LED Clock v3 (88x50 Canvas, 8x8 Pro Font)
// =========================================================================
// ・88x50 キャンバス対応 (LED出力は中央 rows 20-29)
// ・Scene6 と同じ 8x8 テクスチャフォントを使用
// ・VocalOnset 弓なりマゼンタ波動
// =========================================================================

uniform float uTime;
uniform float uHour;
uniform float uMinute;
uniform float uSecond;
uniform float uVocal;
uniform float uOnset;
uniform float uBass;
uniform float uHihat;
uniform float uClap;
uniform float uMelody;
uniform float uMonth;
uniform float uDay;

// Input 0: Font Atlas (2048x8) - 256 chars, 8px wide each
out vec4 fragColor;

// ---- Constants ----
const float CANVAS_W = 88.0;
const float CANVAS_H = 50.0;
const float LED_CENTER_Y = 24.5; // Center of rows 20-29

vec3 CYAN    = vec3(0.0, 0.95, 0.85);
vec3 MAGENTA = vec3(0.95, 0.05, 0.6);
vec3 BLUE    = vec3(0.05, 0.15, 0.9);

float rand(vec2 co){
    return fract(sin(dot(co, vec2(12.9898, 78.233))) * 43758.5453);
}

// ---- 8x8 Font Atlas Lookup ----
// Font Atlas: 2048px wide (256 chars * 8px), 8px high
float getFontPx(int charCode, int lx, int ly) {
    if (charCode < 0 || charCode >= 256 || lx < 0 || lx >= 8 || ly < 0 || ly >= 8) return 0.0;
    float u = (float(charCode * 8 + lx) + 0.5) / 2048.0;
    float v = (float(ly) + 0.5) / 8.0;
    return texture(sTD2DInputs[0], vec2(u, v)).r;
}

// ---- Draw Clock with 8x8 font ----
// "HH:MM" → 5 characters, each 8px wide, 1px gap → total 44px wide
float drawClock8x8(int cx, int cy, int startX, int startY) {
    int ly = cy - startY;
    if (ly < 0 || ly >= 8) return 0.0;
    int lx = cx - startX;
    if (lx < 0) return 0.0;

    int h1 = int(uHour) / 10;
    int h2 = int(uHour) - h1 * 10;
    int m1 = int(uMinute) / 10;
    int m2 = int(uMinute) - m1 * 10;

    // Char 0: H tens   (pos 0-7)
    // Char 1: H units  (pos 9-16)
    // Char 2: Colon    (pos 18-25)
    // Char 3: M tens   (pos 27-34)
    // Char 4: M units  (pos 36-43)
    int spacing = 9; // 8px char + 1px gap

    if (lx >= 0        && lx < 8)            return getFontPx(48 + h1, lx,              ly);
    if (lx >= spacing  && lx < spacing + 8)  return getFontPx(48 + h2, lx - spacing,    ly);
    if (lx >= spacing*2 && lx < spacing*2+8) return getFontPx(58,      lx - spacing*2,  ly); // ':' = ASCII 58
    if (lx >= spacing*3 && lx < spacing*3+8) return getFontPx(48 + m1, lx - spacing*3,  ly);
    if (lx >= spacing*4 && lx < spacing*4+8) return getFontPx(48 + m2, lx - spacing*4,  ly);
    return 0.0;
}

// ---- Draw Date with 8x8 font ----
// "DD/MM" → 5 characters
float drawDate8x8(int cx, int cy, int startX, int startY) {
    int ly = cy - startY;
    if (ly < 0 || ly >= 8) return 0.0;
    int lx = cx - startX;
    if (lx < 0) return 0.0;

    int d1 = int(uDay) / 10;
    int d2 = int(uDay) - d1 * 10;
    int mon1 = int(uMonth) / 10;
    int mon2 = int(uMonth) - mon1 * 10;

    int spacing = 9;

    // MM/DD format
    if (lx >= 0        && lx < 8)            return getFontPx(48 + mon1, lx,              ly);
    if (lx >= spacing  && lx < spacing + 8)  return getFontPx(48 + mon2, lx - spacing,    ly);
    if (lx >= spacing*2 && lx < spacing*2+8) return getFontPx(47,         lx - spacing*2,  ly); // '/'
    if (lx >= spacing*3 && lx < spacing*3+8) return getFontPx(48 + d1,   lx - spacing*3,  ly);
    if (lx >= spacing*4 && lx < spacing*4+8) return getFontPx(48 + d2,   lx - spacing*4,  ly);
    return 0.0;
}

void main()
{
    vec2 uv = vUV.st;
    int cx = int(floor(uv.x * CANVAS_W));
    int cy = int(floor(uv.y * CANVAS_H));
    float fx = float(cx);
    float fy = float(cy);

    vec3 color = vec3(0.0);
    float alpha = 0.0;  // Transparent background for compositing over rain

    // ボーカル歪みとグリッチ
    float vocalDistort = sin(fy * 0.08 + uTime * 5.0) * uVocal * 1.2;
    float glitchOffset = (uClap > 0.4) ? (rand(vec2(fy, uTime * 0.5)) - 0.5) * 3.0 * uClap : 0.0;
    float fx_distorted = fx + vocalDistort + glitchOffset;

    {
        // --- Bass Orb ---
        if (uBass > 0.2) {
            vec2 orbCenter = vec2(44.0, LED_CENTER_Y);
            float dist = length(vec2(fx - orbCenter.x, (fy - orbCenter.y) * (88.0 / CANVAS_H)));
            float orbRadius = 6.0 + uBass * 35.0;
            if (dist < orbRadius) {
                float falloff = pow(1.0 - (dist / orbRadius), 2.0);
                float intensity = falloff * uBass * (0.8 + 0.2 * sin(uTime * 20.0));
                color += mix(CYAN, vec3(0.9, 0.95, 1.0), min(intensity, 1.0)) * min(intensity, 1.0);
                alpha = max(alpha, min(intensity, 1.0));
            }
        }

        // --- VocalOnset 弓なりマゼンタ波動 ---
        if (uOnset > 0.7) {
            float waveSpeed = 50.0;
            float maxDist = 44.0;
            float wavePos = mod(uTime * waveSpeed, maxDist + 15.0);

            float yFromCenter = abs(fy - LED_CENTER_Y);
            float yOffset = 0.0;
            if (yFromCenter <= 1.5)      yOffset = 0.0;
            else if (yFromCenter <= 3.5) yOffset = 1.0;
            else if (yFromCenter <= 5.0) yOffset = 2.0;
            else                         yOffset = 3.0;

            float curvedWavePos = wavePos - yOffset;
            float distFromCenter = abs(fx - 44.0);

            if (distFromCenter <= curvedWavePos && curvedWavePos > 0.0) {
                float behindWave = curvedWavePos - distFromCenter;
                float trailLength = 5.0;

                if (behindWave < trailLength) {
                    float brightness = uOnset * (1.0 - behindWave / trailLength);
                    float distanceDecay = max(1.0 - (distFromCenter / maxDist), 0.0);
                    vec3 waveColor = vec3(1.0, 0.4, 0.9);
                    color += waveColor * brightness * distanceDecay * 0.8;
                    alpha = max(alpha, brightness * distanceDecay * 0.8);
                }
            }
        }
    }

    // --- 日付オーバーレイ (MM/DD) ---
    // Rows 30-39 area (Y=31)
    int dateStartX = 0; 
    int dateStartY = 31;
    float datePx = drawDate8x8(cx, cy, dateStartX, dateStartY);
    if (datePx > 0.5) {
        float melodyGlow = 0.7 + uMelody * 0.3;
        float pixelNoise = rand(vec2(fx * 7.3, fy * 11.7 + floor(uTime * 15.0)));
        float pixelBrightness = 1.0 + pixelNoise * 0.6;
        vec3 pixelColor = mix(vec3(0.9, 0.95, 1.0), vec3(0.5, 0.8, 1.0), pixelNoise * 0.3);
        color = pixelColor * melodyGlow * pixelBrightness; 
        alpha = 1.0;
    }

    // --- 時計オーバーレイ (HH:MM) ---
    // Rows 20-29 area (Y=21)
    int clockStartX = 0; 
    int clockStartY = 21;
    float clockPx = drawClock8x8(cx, cy, clockStartX, clockStartY);
    if (clockPx > 0.5) {
        float blink = 1.0;
        int colonLx = cx - clockStartX;
        if (colonLx >= 18 && colonLx < 26) {
            blink = (mod(uSecond, 2.0) < 1.0) ? 1.0 : 0.2;
        }
        float melodyGlow = 0.7 + uMelody * 0.3;
        float pixelNoise = rand(vec2(fx * 7.3, fy * 11.7 + floor(uTime * 15.0)));
        float pixelBrightness = 1.0 + pixelNoise * 0.6;
        vec3 pixelColor = mix(vec3(0.9, 0.95, 1.0), vec3(0.5, 0.8, 1.0), pixelNoise * 0.3);
        color = pixelColor * blink * melodyGlow * pixelBrightness;
        alpha = 1.0; 
    }

    fragColor = vec4(clamp(color, 0.0, 1.0), alpha);
}
