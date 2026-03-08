// baseball_scene_v2.glsl
// ================================================================
// Scene 6: Baseball Narrative Sequence (88x50 Expansion)
// TEXTURE-BASED RENDERING + CELEBRATION EFFECTS
// ================================================================

uniform float uTime;
uniform float uPitchIndex;   // State 0..8 (0:Intro, 1-5:Pitch, 6:HR, 7:Stats, 8:Outro)
uniform float uStateFrame;    // Frames within the state (0..899)

uniform vec4 uLenA; // States 0-3
uniform vec4 uLenB; // States 4-7
uniform vec4 uLenC; // States 8-11
uniform vec4 uLenD; // States 12-15

out vec4 fragColor;

// --- Helpers ---
float hash(float n) { return fract(sin(n) * 43758.5453123); }

float getAtlasPx(int state_row, int lx, int ly) {
    if (state_row < 0 || state_row >= 16 || lx < 0 || lx >= 2048 || ly < 0 || ly >= 8) return 0.0;
    float u = (float(lx) + 0.5) / 2048.0;
    float v = (float(state_row * 8 + ly) + 0.5) / 128.0;
    return texture(sTD2DInputs[0], vec2(u, v)).r;
}

float getPitchLen(int state) {
    if (state < 4) return uLenA[state];
    if (state < 8) return uLenB[state-4];
    if (state < 12) return uLenC[state-8];
    return uLenD[state-12];
}

void main() {
    vec2 res = uTDOutputInfo.res.zw;
    vec2 pixelCoord = floor(vUV.st * res);
    int cx = int(pixelCoord.x);
    int cy = int(pixelCoord.y);

    int state = int(uPitchIndex);
    float f = uStateFrame;
    vec3 color = vec3(0.0);
    
    // NEW: Vertical center of 20-29 LED window for 8px text
    int baseY = 21; 
    int ty = cy - baseY; 

    // --- CELEBRATION: Confetti (States 6) in dead zones ---
    // Only starts at frame 270 when "HOME RUN!" text appears
    if (state == 6 && f >= 270.0 && (cy < 20 || cy >= 30)) {
        float fcy = float(cy);
        float fcx = float(cx);
        float col = floor(fcx / 4.4); 
        float speed = 0.2 + hash(col) * 0.3;
        float phase = hash(col + 123.4) * 50.0;
        float yPos = 50.0 - fract((f * speed + phase) / 50.0) * 50.0;
        
        if (abs(fcy - yPos) < 1.0 && hash(col + f * 0.01) > 0.7) {
            color = 0.5 + 0.5 * cos(6.28318 * (vec3(0.0, 1.0, 2.0)/3.0 + col * 0.1 + f * 0.02));
        }
    }

    // --- CELEBRATION: Orbiting Border (State 6) ---
    // Only starts at frame 270 when "HOME RUN!" text appears
    if (state == 6 && f >= 270.0 && cy >= 20 && cy < 30) {
        float fcy = float(cy);
        float fcx = float(cx);
        float perimeter = (88.0 + 10.0) * 2.0;
        float headPos = mod((f - 270.0) * 5.0, perimeter); // Starts fresh from frame 270
        
        // Calculate current pixel's position along the perimeter (clockwise from 0,20)
        float pixPos = 0.0;
        if (cy == 20) pixPos = fcx;
        else if (cx == 87) pixPos = 88.0 + (fcy - 20.0);
        else if (cy == 29) pixPos = 98.0 + (87.0 - fcx);
        else if (cx == 0) pixPos = 186.0 + (29.0 - fcy);
        
        // Distance from head (circular)
        float dist = mod(headPos - pixPos + perimeter, perimeter);
        
        // Trail length: 15 pixels
        if (dist < 15.0) {
            float intensity = 1.0 - (dist / 15.0);
            intensity = pow(intensity, 2.0); // Sharper fade
            color += (0.5 + 0.5 * cos(6.28318 * (vec3(0.0, 1.0, 2.0)/3.0 + headPos * 0.05 + f * 0.1))) * intensity;
        }
    }

    // --- Main Rendering (State-based) ---
    if (state == 0) { // Intro
        int sx = 88 - int(f / 2.0);
        int dx = cx - sx;
        if (getAtlasPx(0, dx, ty) > 0.5) color = vec3(0.4, 0.8, 1.0);
    }
    else if (state >= 1 && state <= 5) { // Pitches
        if (f < 60.0) { // Ball L->R
            float t = f / 60.0;
            float bx = t * 88.0; float by = 24.0 + sin(t * 3.1415) * 0.5;
            if (length(vec2(float(cx), float(cy)) - vec2(bx, by)) < 1.2) color = vec3(1.0);
        }
        else if (f < 240.0) { // Result (60 to 240 = 180 frames = 3s)
            float t = (f - 60.0) / 180.0;
            if (cy >= 20 && cy < 30) color = vec3(sin(t * 3.1415) * 0.3);
            int rLen = int(getPitchLen(state));
            int dx = cx - (88 - rLen) / 2;
            if (getAtlasPx(state, dx, ty) > 0.5) {
                color = (state%2 == 1) ? vec3(1.0, 0.2, 0.2) : vec3(0.2, 1.0, 0.2); 
            }
        }
        else if (f < 270.0) { // Wait (240 to 270 = 30 frames = 0.5s)
            color = vec3(0.0);
        }
        else { // Detail Scroll (Starts at 270)
            int sx = 88 - (int(f) - 270);
            int dx = cx - sx;
            if (getAtlasPx(state + 8, dx, ty) > 0.5) color = vec3(0.6, 0.6, 0.8);
        }
    }
    else if (state == 6) { // Home Run
        if (f < 60.0) { // Catching hit
            float t = f / 60.0;
            float bx = t * 88.0; float by = 24.0;
            if (length(vec2(float(cx), float(cy)) - vec2(bx, by)) < 1.2) color = vec3(1.0);
        }
        else if (f < 240.0) { // BOOM (Extended to 3s for consistency)
            float flash = sin((f - 60.0) / 180.0 * 3.1415);
            // Flash only applies to center area
            if (cy >= 20 && cy < 30) color += vec3(flash * 0.4);
            int rLen = int(getPitchLen(6));
            if (getAtlasPx(6, cx - (88 - rLen) / 2, ty) > 0.5) color = vec3(1.0); // White
        }
        else if (f < 270.0) { // Wait (0.5s)
            color = vec3(0.0);
        }
        else { // Flight + Rainbow (Starts at 270)
            float flyT = (f - 270.0) / 630.0; 
            float bx = 88.0 - flyT * 140.0; float by = 23.0 + flyT * 25.0;
            if (length(vec2(float(cx), float(cy)) - vec2(bx, by)) < 1.5) color = vec3(1.0);
            int rLen = int(getPitchLen(15));
            if (getAtlasPx(15, cx - (88 - rLen) / 2, ty) > 0.5) {
                 color = vec3(1.0); // Changed to White (from rainbow)
            }
        }
    }
    else if (state == 7) { // HR Stats
        int sx = 88 - int(f);
        int dx = cx - sx;
        if (getAtlasPx(7, dx, ty) > 0.5) color = vec3(1.0, 0.7, 0.3);
    }
    else if (state == 8) { // Outro
        int sx = 88 - int(f / 2.0);
        int dx = cx - sx;
        if (getAtlasPx(8, dx, ty) > 0.5) color = vec3(0.5, 1.0, 0.5);
    }

    fragColor = vec4(clamp(color, 0.0, 1.0), 1.0);
}
