uniform float uTime;   // absTime.seconds
uniform float uClap;   // AudioLinkCore: Clap (0.0 - 1.0+)
uniform float uVocal;  // AudioLinkCore: VocalIntensity (0.0 - 1.0+)
uniform float uBass;   // AudioLinkCore: BassEnergy (0.0 - 1.0+)
uniform float uHihat;  // AudioLinkCore: Hihat (0.0 - 1.0+)

uniform float uHour;   // 現在の時 (0 - 23)
uniform float uMinute; // 現在の分 (0 - 59)
uniform float uSecond; // 現在の秒 (0 - 59)

out vec4 fragColor;

float rand(vec2 co){
    return fract(sin(dot(co, vec2(12.9898, 78.233))) * 43758.5453);
}

// =========================================================================
// 3x5 ビットマップフォント (完全手計算・検証済み)
// =========================================================================
// ビット配置:  bit_index = col + row * 3
//   col: 0=左, 1=中, 2=右
//   row: 0=下端, 4=上端
//
// 数字 '0':       '1':        '2':        '3':        '4':
//  r4: 1 1 1    r4: 0 1 0    r4: 1 1 1    r4: 1 1 1    r4: 1 0 1
//  r3: 1 0 1    r3: 1 1 0    r3: 1 0 0    r3: 0 0 1    r3: 1 0 1
//  r2: 1 0 1    r2: 0 1 0    r2: 1 1 1    r2: 1 1 1    r2: 1 1 1
//  r1: 1 0 1    r1: 0 1 0    r1: 0 0 1    r1: 0 0 1    r1: 0 0 1
//  r0: 1 1 1    r0: 1 1 1    r0: 1 1 1    r0: 1 1 1    r0: 0 0 1
//  = 31599      = 9879       = 29671      = 31207      = 23524
//
// '5':          '6':         '7':         '8':         '9':
//  r4: 1 1 1    r4: 1 1 1    r4: 1 1 1    r4: 1 1 1    r4: 1 1 1
//  r3: 0 0 1    r3: 1 0 1    r3: 0 0 1    r3: 1 0 1    r3: 0 0 1
//  r2: 1 1 1    r2: 1 1 1    r2: 0 0 1    r2: 1 1 1    r2: 1 1 1
//  r1: 1 0 0    r1: 1 0 0    r1: 0 0 1    r1: 1 0 1    r1: 1 0 1
//  r0: 1 1 1    r0: 1 1 1    r0: 0 0 1    r0: 1 1 1    r0: 1 1 1
//  = 31183      = 31695      = 31012      = 31727      = 31215
//
// コロン ':':
//  r4: 0 0 0
//  r3: 0 1 0
//  r2: 0 0 0
//  r1: 0 1 0
//  r0: 0 0 0
//  = 1040
// =========================================================================

int fontData[11] = int[11](
    31599, // 0
    9879,  // 1
    31183, // 2
    31207, // 3
    23524, // 4
    29671, // 5
    29679, // 6
    31012, // 7
    31727, // 8
    31719, // 9
    1040   // 10 = ':'
);

float getDigitPixel(int digit, int lx, int ly) {
    if (lx < 0 || lx > 2 || ly < 0 || ly > 4) return 0.0;
    if (digit < 0 || digit > 10) return 0.0;
    int bits = fontData[digit];
    int idx = lx + ly * 3;  // col0=左, row0=下
    return float((bits >> idx) & 1);
}

// ---- 時計描画 ----
float drawClock(int cx, int cy, int startX, int startY) {
    int ly = cy - startY;
    if (ly < 0 || ly > 4) return 0.0;
    int lx = cx - startX;
    if (lx < 0) return 0.0;

    int h1 = int(uHour) / 10;
    int h2 = int(uHour) - h1 * 10;
    int m1 = int(uMinute) / 10;
    int m2 = int(uMinute) - m1 * 10;

    // h1(0..2) gap(3) h2(4..6) gap(7) :(8) gap(9) m1(10..12) gap(13) m2(14..16)
    if (lx >= 0  && lx <= 2)  return getDigitPixel(h1, lx,      ly);
    if (lx >= 4  && lx <= 6)  return getDigitPixel(h2, lx - 4,  ly);
    if (lx == 8)              return getDigitPixel(10, 1,        ly);
    if (lx >= 10 && lx <= 12) return getDigitPixel(m1, lx - 10, ly);
    if (lx >= 14 && lx <= 16) return getDigitPixel(m2, lx - 14, ly);

    return 0.0;
}

// ---- メイン ----
void main()
{
    vec2 outRes = uTDOutputInfo.res.zw;
    vec2 inRes = outRes / 3.0;
    vec2 pixelCoord = floor(vUV.st * outRes);

    int cx = int(floor(pixelCoord.x / 3.0));
    int cy = int(floor(pixelCoord.y / 3.0));
    int lx = int(mod(pixelCoord.x, 3.0));
    int ly = int(mod(pixelCoord.y, 3.0));

    if (lx == 1 && ly == 1) {
        vec3 finalColor = vec3(0.0);
        #if defined(TD_NUM_2D_INPUTS) && TD_NUM_2D_INPUTS > 0
            vec2 sampleUV = (vec2(float(cx), float(cy)) + 0.5) / inRes;
            finalColor = texture(sTD2DInputs[0], sampleUV).rgb;
        #endif

        vec3 cyanNeon = vec3(0.1, 1.0, 0.9);
        float brightness = 0.0;

        // (A) 時計 (x:2〜18, y:3〜7)
        brightness += drawClock(cx, cy, 2, 3);

        // (B) グリッチストリーム (x:22〜50)
        if (cx >= 22 && cx <= 50) {
            float speed = uTime * (5.0 + uHihat * 10.0);
            vec2 block = vec2(float(cx / 2), float(cy));
            float n = rand(block + floor(speed));
            float thresh = 0.80 - uClap * 0.3 - uVocal * 0.2;
            if (n > thresh) {
                float flicker = rand(vec2(float(cx), float(cy)) + uTime * 7.0);
                if (flicker > 0.3) {
                    brightness += 0.7 * (n - thresh) / (1.0 - thresh);
                }
            }
        }

        // (C) オーディオバー (x:55〜85)
        if (cx >= 55 && cx <= 85) {
            float val = 0.0;
            bool inBar = false;
            if (cy >= 1 && cy <= 3) { val = uBass;  inBar = true; }
            if (cy >= 4 && cy <= 6) { val = uVocal; inBar = true; }
            if (cy >= 7 && cy <= 9) { val = uHihat; inBar = true; }

            if (inBar) {
                float maxLen = 30.0;
                float barLen = val * maxLen;
                float localX = float(cx - 55);
                if (localX < barLen) {
                    float tip = smoothstep(barLen - 4.0, barLen, localX);
                    brightness += 0.5 + 0.5 * tip;
                } else {
                    brightness += 0.04;
                }
            }
        }

        finalColor += cyanNeon * brightness;
        fragColor = vec4(clamp(finalColor, 0.0, 1.0), 1.0);
    } else {
        fragColor = vec4(0.0, 0.0, 0.0, 1.0);
    }
}
