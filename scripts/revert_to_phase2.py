# revert_to_phase_2.py - Emergency Restore Script
import traceback
import os

STABLE_GLSL = """// =========================================================================
// Cyberpunk LED Clock Phase 2 (Stable Restore)
// =========================================================================
uniform float uTime;
uniform float uClap;
uniform float uVocal;
uniform float uBass;
uniform float uHihat;
uniform float uHour;
uniform float uMinute;
uniform float uSecond;

out vec4 fragColor;

float rand(vec2 co){
    return fract(sin(dot(co, vec2(12.9898, 78.233))) * 43758.5453);
}

vec3 CYAN    = vec3(0.0, 0.95, 0.85);
vec3 MAGENTA = vec3(0.95, 0.05, 0.6);
vec3 BLUE    = vec3(0.05, 0.15, 0.9);

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

void main() {
    vec2 uv = vUV.st;
    int cx = int(floor(uv.x * 88.0));
    int cy = int(floor(uv.y * 10.0));
    float fx = float(cx);
    float fy = float(cy);
    vec3 color = vec3(0.0);

    // --- Background (Data Stream) ---
    float colSpeed = rand(vec2(fx * 0.37, 1.0)) * 3.0 + 1.0;
    float scroll = uTime * colSpeed;
    float scrollY = mod(fy + scroll, 10.0);
    float n = rand(vec2(fx, floor(scrollY)));
    
    float density = 0.15 + uVocal * 0.2;
    if (n < density) {
        float headDist = mod(scrollY, 5.0);
        float br = smoothstep(4.0, 0.0, headDist);
        color += mix(BLUE, CYAN, br) * (0.3 + br * 0.7);
    }

    // --- Bass Orb ---
    vec2 orbPos = vec2(44.0, 5.0);
    float dist = length(vec2(fx - orbPos.x, (fy - orbPos.y) * 3.0));
    float rad = 6.0 + uBass * 30.0;
    if (dist < rad) {
        float fall = pow(1.0 - (dist / rad), 2.0);
        color += mix(CYAN, vec3(1.0), fall) * fall * uBass * 2.0;
    }

    // --- Clock ---
    float clockPx = drawClock(cx, cy, 1, 3);
    if (clockPx > 0.0) {
        color = vec3(0.9, 0.95, 1.0) * (mod(uSecond, 2.0) < 1.0 || (cx-1)!=8 ? 1.0 : 0.2);
    }

    fragColor = vec4(clamp(color, 0.0, 1.0), 1.0);
}
"""

try:
    glsl = op('/AudioLinkLight_V01/TEST_SCREEN2/cyber_clock_v2')
    pixel = op('/AudioLinkLight_V01/TEST_SCREEN2/cyber_clock_v2_pixel22')
    core = op('/AudioLinkLight_V01/AudioLinkCore/out1')
    clock = op('/AudioLinkLight_V01/TEST_SCREEN2/clock_updater_v2')

    if not glsl or not pixel:
        print("Required nodes not found!")
    else:
        print("Restoring Phase 2 State...")
        
        # 1. Reset Parameters
        glsl.par.array = 0
        glsl.par.array0name = ''
        glsl.par.array0chop = ''
        
        for i in range(10):
            getattr(glsl.par, f'uniname{i}').val = ''
            getattr(glsl.par, f'value{i}x').expr = ''
            getattr(glsl.par, f'value{i}x').val = 0.0

        # 2. Re-assign Basics
        glsl.par.uniname0, glsl.par.value0x.expr = 'uTime', 'absTime.seconds'
        glsl.par.uniname1, glsl.par.value1x.expr = 'uClap', f"op('{core.path}')['Clap']" if core else '0.0'
        glsl.par.uniname2, glsl.par.value2x.expr = 'uVocal', f"op('{core.path}')['uVocalIntensity']" if core else '0.0'
        glsl.par.uniname3, glsl.par.value3x.expr = 'uBass', f"op('{core.path}')['uBassEnergy']" if core else '0.0'
        glsl.par.uniname4, glsl.par.value4x.expr = 'uHihat', f"op('{core.path}')['Hihat']" if core else '0.0'
        glsl.par.uniname5, glsl.par.value5x.expr = 'uHour', f"op('{clock.path}')['hour']" if clock else '0.0'
        glsl.par.uniname6, glsl.par.value6x.expr = 'uMinute', f"op('{clock.path}')['minute']" if clock else '0.0'
        glsl.par.uniname7, glsl.par.value7x.expr = 'uSecond', f"op('{clock.path}')['second']" if clock else '0.0'

        # 3. Apply Code
        pixel.text = STABLE_GLSL
        with open(project.folder + '/scripts/cyber_clock_v2.glsl', 'w', encoding='utf-8') as f:
            f.write(STABLE_GLSL)
        
        glsl.cook(force=True)
        print("--- PHASE 2 RESTORED SUCCESSFULLY ---")

except Exception as e:
    traceback.print_exc()
