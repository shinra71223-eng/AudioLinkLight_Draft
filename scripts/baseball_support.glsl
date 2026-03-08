// baseball_support.glsl
// ================================================================
// Support Message Shader
// IDENTICAL formula to main shader: u/2048.0, v/128.0
// Each support GLSL has its own 2048x128 text source (same dims as main)
// ================================================================

uniform float uStateFrame;
uniform float uPitchIndex;
uniform vec4 uColor;
uniform float uDirection; // 1.0: Pitcher (L->R), -1.0: Batter (R->L)

out vec4 fragColor;

void main() {
    vec2 res = uTDOutputInfo.res.zw;
    vec2 pixelCoord = floor(vUV.st * res);
    int cx = int(pixelCoord.x);
    int cy = int(pixelCoord.y);

    fragColor = vec4(0.0);
    
    // Pitcher: 30-39, Batter: 10-19
    bool inPitcherZone = (uDirection > 0.5 && cy >= 30 && cy < 40);
    bool inBatterZone = (uDirection < -0.5 && cy >= 10 && cy < 20);
    
    if (!inPitcherZone && !inBatterZone) return;
    
    // Team Color Indicator Blocks (Always ON)
    if (inPitcherZone && cx < 4) {
        fragColor = vec4(uColor.rgb, 1.0);
        return;
    }
    if (inBatterZone && cx >= 84) {
        fragColor = vec4(uColor.rgb, 1.0);
        return;
    }
    
    if (uStateFrame < 270.0) return;
    
    float t = clamp((uStateFrame - 270.0) / 45.0, 0.0, 1.0);
    float slideOffset = (1.0 - t) * 88.0 * uDirection;

    int dx = cx + int(slideOffset);
    
    // Offset Pitcher text by 1 character (8 pixels) to the right to avoid overlapping the team color block
    if (inPitcherZone) {
        dx -= 8;
    }

    if (dx < 0 || dx >= 2048) return;

    int ty = (uDirection > 0.5) ? (cy - 31) : (cy - 11);
    if (ty < 0 || ty >= 8) return;
    
    int state = int(uPitchIndex);
    if (state < 0 || state >= 16) return;
    
    // *** 100% IDENTICAL to main shader's getAtlasPx ***
    // Same texture size (2048x128), same formula, same divisors
    float u_coord = (float(dx) + 0.5) / 2048.0;
    float v_coord = (float(state * 8 + ty) + 0.5) / 128.0;
    
    float mask = texture(sTD2DInputs[0], vec2(u_coord, v_coord)).r;
    if (mask > 0.5) {
        fragColor = vec4(uColor.rgb, 1.0);
    }
}
