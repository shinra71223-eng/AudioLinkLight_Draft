// =========================================================================
// Cyberpunk LED Clock v3 (Safe Mode - No Array)
// =========================================================================
// ・10本制限以内の個別Vector Uniformsを使用（フリーズ回避）
// ・VocalOnset 弓なりマゼンタ波動を搭載
// ・粒子密度を50%削減（クリーン化）
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

out vec4 fragColor;

float rand(vec2 co){
    return fract(sin(dot(co, vec2(12.9898, 78.233))) * 43758.5453);
}

vec3 CYAN    = vec3(0.0, 0.95, 0.85);
vec3 MAGENTA = vec3(0.95, 0.05, 0.6);
vec3 BLUE    = vec3(0.05, 0.15, 0.9);

// ---- 3x5 フォント ----
int fontData[11] = int[11](
    31599, 9879, 31183, 31207, 23524,
    29671, 29679, 31012, 31727, 31719,
    1040
);

float getDigitPixel(int digit, int lx, int ly) {
    if (lx < 0 || lx > 2 || ly < 0 || ly > 4) return 0.0;
    if (digit < 0 || digit > 10) return 0.0;
    return float((fontData[digit] >> (lx + ly * 3)) & 1);
}

float drawClock(int cx, int cy, int startX, int startY) {
    int ly = cy - startY;
    if (ly < 0 || ly > 4) return 0.0;
    int lx = cx - startX;
    if (lx < 0) return 0.0;
    int h1 = int(uHour) / 10;
    int h2 = int(uHour) - h1 * 10;
    int m1 = int(uMinute) / 10;
    int m2 = int(uMinute) - m1 * 10;
    if (lx >= 0  && lx <= 2)  return getDigitPixel(h1, lx,      ly);
    if (lx >= 4  && lx <= 6)  return getDigitPixel(h2, lx - 4,  ly);
    if (lx == 8)              return getDigitPixel(10, 1,        ly);
    if (lx >= 10 && lx <= 12) return getDigitPixel(m1, lx - 10, ly);
    if (lx >= 14 && lx <= 16) return getDigitPixel(m2, lx - 14, ly);
    return 0.0;
}

void main()
{
    vec2 uv = vUV.st;
    int cx = int(floor(uv.x * 88.0));
    int cy = int(floor(uv.y * 10.0));
    float fx = float(cx);
    float fy = float(cy);

    vec3 color = vec3(0.0);

    // ボーカル歪みとグリッチ（マイルドに設定）
    float vocalDistort = sin(fy * 0.4 + uTime * 5.0) * uVocal * 1.2; 
    float glitchOffset = (uClap > 0.4) ? (rand(vec2(fy, uTime * 0.5)) - 0.5) * 3.0 * uClap : 0.0;
    float fx_distorted = fx + vocalDistort + glitchOffset;

    {
        // --- 背景データストリーム ---
        float colSpeed = rand(vec2(floor(fx_distorted) * 0.37, 1.0)) * 3.0 + 1.0;
        float scroll = uTime * (colSpeed + uVocal * 0.5); 
        float scrollY = mod(fy + scroll, 10.0);
        float n = rand(vec2(floor(fx_distorted), floor(scrollY)));

        // 密度削減（クリーンな印象にするためPhase 2の半分程度）
        float density = 0.04 + uVocal * 0.08 + uBass * 0.05 + uHihat * 0.08; 

        if (n < density) {
            float headDist = mod(scrollY, 5.0);
            float brightness = smoothstep(4.0, 0.0, headDist);

            vec3 baseCol = mix(BLUE, CYAN, brightness);
            vec3 vocalCol = mix(MAGENTA, vec3(1.0, 0.5, 0.0), brightness);
            
            float colorShift = clamp(uVocal * 1.3, 0.0, 1.0);
            vec3 streamColor = mix(baseCol, vocalCol, colorShift);

            color += streamColor * (0.3 + brightness * 0.7);
        }

        // --- Bass Orb ---
        if (uBass > 0.2) {
            vec2 orbCenter = vec2(44.0, 5.0);
            float dist = length(vec2(fx - orbCenter.x, (fy - orbCenter.y) * 3.0));
            float orbRadius = 6.0 + uBass * 35.0;
            if (dist < orbRadius) {
                float falloff = pow(1.0 - (dist / orbRadius), 2.0);
                float intensity = falloff * uBass * (0.8 + 0.2 * sin(uTime * 20.0));
                color += mix(CYAN, vec3(0.9, 0.95, 1.0), min(intensity, 1.0)) * min(intensity, 1.0);
            }
        }

        // --- VocalOnset 弓なりマゼンタ波動 ---
        if (uOnset > 0.7) {
            float waveSpeed = 50.0;
            float maxDist = 44.0;
            float wavePos = mod(uTime * waveSpeed, maxDist + 15.0);

            // 指示通りのY軸遅延（弓なり形状）
            float yOffset = 0.0;
            if (cy >= 3 && cy <= 6)      yOffset = 0.0; 
            else if (cy == 1 || cy == 2 || cy == 7 || cy == 8) yOffset = 1.0; 
            else if (cy == 0 || cy == 9) yOffset = 2.0; 

            float curvedWavePos = wavePos - yOffset;
            float distFromCenter = abs(fx - 44.0);

            if (distFromCenter <= curvedWavePos && curvedWavePos > 0.0) {
                float behindWave = curvedWavePos - distFromCenter;
                float trailLength = 5.0; // テイル5px

                if (behindWave < trailLength) {
                    float brightness = uOnset * (1.0 - behindWave / trailLength);
                    float distanceDecay = max(1.0 - (distFromCenter / maxDist), 0.0);
                    vec3 waveColor = vec3(1.0, 0.4, 0.9); // 鮮やかな薄マゼンタ
                    color += waveColor * brightness * distanceDecay * 0.8; 
                }
            }
        }
    }

    // --- 時計オーバーレイ ---
    float clockPx = drawClock(cx, cy, 1, 3);
    if (clockPx > 0.0) {
        float blink = (cx - 1 == 8) ? (mod(uSecond, 2.0) < 1.0 ? 1.0 : 0.2) : 1.0;
        float melodyGlow = 0.7 + uMelody * 0.3;
        float pixelNoise = rand(vec2(fx * 7.3, fy * 11.7 + floor(uTime * 15.0))); 
        float pixelBrightness = 1.0 + pixelNoise * 0.6; 
        vec3 pixelColor = mix(vec3(0.9, 0.95, 1.0), vec3(0.5, 0.8, 1.0), pixelNoise * 0.3);
        color = pixelColor * blink * melodyGlow * pixelBrightness;
    }

    fragColor = vec4(clamp(color, 0.0, 1.0), 1.0);
}
