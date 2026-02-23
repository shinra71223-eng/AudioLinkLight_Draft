// =========================================================================
// Cyberpunk LED Clock - THRESHOLD MASTER (Beam Flow + Fade)
// =========================================================================
uniform float uTime;
uniform float uHour;
uniform float uMinute;
uniform float uSecond;
uniform float uVocal;
uniform float uOnset;    
uniform float uWavePhase;  
uniform float uBass;
uniform vec4  uSustainVec; // X=Len, Y=Phase(0->1), Z=Alpha, W=Mode(0:Fade, 1:Flow)
uniform float uVocalScroll; 

out vec4 fragColor;

float rand(vec2 co){
    return fract(sin(dot(co, vec2(12.9898, 78.233))) * 43758.5453);
}

vec3 CYAN    = vec3(0.0, 0.95, 0.85);
vec3 MAGENTA = vec3(0.95, 0.05, 0.6);
vec3 BLUE    = vec3(0.05, 0.15, 0.9);

// --- Font & Background functions ---
int fontData[11] = int[11](31599, 9879, 31183, 31207, 23524, 29671, 29679, 31012, 31727, 31719, 1040);
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
    int h1 = int(uHour) / 10, h2 = int(uHour) % 10;
    int m1 = int(uMinute) / 10, m2 = int(uMinute) % 10;
    if (lx >= 0  && lx <= 2)  return getDigitPixel(h1, lx,      ly);
    if (lx >= 4  && lx <= 6)  return getDigitPixel(h2, lx - 4,  ly);
    if (lx == 8)              return getDigitPixel(10, 1,        ly);
    if (lx >= 10 && lx <= 12) return getDigitPixel(m1, lx - 10, ly);
    if (lx >= 14 && lx <= 16) return getDigitPixel(m2, lx - 14, ly);
    return 0.0;
}

void main() {
    vec2 uv = vUV.st;
    int cx = int(floor(uv.x * 88.0)), cy = int(floor(uv.y * 10.0));
    float fx = float(cx), fy = float(cy);
    vec3 color = vec3(0.0);

    // --- Background: Horizontal Stream (Right to Left) ---
    float rowSpeed = rand(vec2(fy * 0.37, 1.0)) * 2.5 + 2.0; 
    float scroll = uTime * rowSpeed + uVocalScroll * 10.0; 
    float scrollX = mod(fx + scroll, 88.0);
    float n = rand(vec2(floor(scrollX), fy));
    
    float density = 0.05 + uVocal * 0.08;
    if (n < density) {
        float br = smoothstep(8.0, 0.0, mod(scrollX, 10.0));
        color += mix(BLUE, CYAN, br) * (0.3 + br * 0.7);
    }

    // --- Bass Orb (Snappier & Brighter) ---
    if (uBass > 0.05) {
        vec2 orbCenter = vec2(44.0, 5.0);
        float dist = length(vec2(fx - orbCenter.x, (fy - orbCenter.y) * 3.0));
        float orbRadius = 5.0 + uBass * 40.0;
        if (dist < orbRadius) {
            float falloff = pow(1.0 - (dist / orbRadius), 4.0);
            float intensity = falloff * uBass * 2.5; 
            vec3 orbCol = mix(BLUE, CYAN, 0.5 + 0.5 * sin(uTime * 10.0));
            color += mix(orbCol, vec3(1.0), min(intensity * 0.5, 1.0)) * intensity;
        }
    }

    // --- VocalOnset WAVE ---
    if (uWavePhase > 0.0) {
        float maxWaveDist = 44.0;
        float wavePos = -5.0 + uWavePhase * (maxWaveDist + 15.0);
        float yOffset = (cy >= 3 && cy <= 6) ? 0.0 : ((cy == 0 || cy == 9) ? 2.0 : 1.0);
        float curvedWaveHead = wavePos - yOffset;
        float distFromCenter = abs(fx - 44.0);
        if (distFromCenter <= curvedWaveHead && distFromCenter > curvedWaveHead - 5.0) {
            float tailDist = curvedWaveHead - distFromCenter; 
            float tailProgress = tailDist / 5.0; 
            float fade = 1.0 - tailProgress; 
            float distanceDecay = max(1.0 - (distFromCenter / maxWaveDist), 0.0);
            float br = fade * distanceDecay * 1.5 * uOnset;
            color += MAGENTA * br; 
        }
    }

    // --- Sustain Beam (Threshold Flow/Fade Master) ---
    if (cy == 0 || cy == 9) {
        float distFromCenter = abs(fx - 44.0);
        
        float sLen   = uSustainVec.x; // 最大の長さ
        float sPhase = uSustainVec.y; // 0.0(Release前) -> 進むほど増加
        float sAlpha = uSustainVec.z; // 合計輝度 (1.2sフェード)
        float sMode  = uSustainVec.w; // 1.0=射出, 0.0=霧散
        
        // 描画範囲の決定
        float beamLength = sLen * 44.0;
        float head = beamLength + (sPhase * sMode * 60.0); 
        float tail = (sPhase * sMode * 60.0);
        
        if (distFromCenter < head && distFromCenter >= tail) {
            float progress = (distFromCenter - tail) / max(head - tail, 0.1);
            float tipGlow = pow(progress, 2.0); 
            
            // 輝度計算
            float intensity = sAlpha * (0.4 + tipGlow * 2.0);
            
            // 淡い黄色 (Cream Yellow)
            vec3 paleYellow = vec3(1.0, 0.95, 0.6);
            color += paleYellow * intensity;
        }
    }

    // --- Clock ---
    float clockPx = drawClock(cx, cy, 1, 3);
    if (clockPx > 0.0) {
        float blink = (cx - 1 == 8) ? (mod(uSecond, 2.0) < 1.0 ? 1.0 : 0.2) : 1.0;
        color = vec3(0.9, 0.95, 1.0) * blink * (0.8 + uVocal * 0.2);
    }

    fragColor = vec4(clamp(color, 0.0, 1.0), 1.0);
}
