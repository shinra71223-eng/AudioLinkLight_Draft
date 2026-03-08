// =========================================================================
// Light Rain / Data Stream v2 (88x50 Canvas)
// =========================================================================
uniform float uTime;

out vec4 fragColor;

float rand(vec2 co){
    return fract(sin(dot(co, vec2(12.9898, 78.233))) * 43758.5453);
}

void main()
{
    vec2 uv = vUV.st;
    float fx = floor(uv.x * 88.0);
    float fy = uv.y * 50.0; 

    vec3 CYAN = vec3(0.0,  0.95, 0.85);
    vec3 BLUE = vec3(0.05, 0.15, 0.90);

    // --- Randomness per Column ---
    float colSeed = rand(vec2(fx, 123.45));
    float colSpeed = 1.0 + colSeed * 5.0; 
    float colOffset = colSeed * 100.0;    
    
    // VARIATION: Randomize the vertical pitch (tiling height) per column
    // This makes some columns have "denser" packets than others
    float rainVirtualH = 6.0 + colSeed * 12.0; 
    
    float scroll   = uTime * colSpeed + colOffset;
    float scrollY  = mod(fy + scroll, rainVirtualH);
    
    float blockID = floor(scrollY);
    float n = rand(vec2(fx, blockID));

    // VARIATION: Randomize the horizontal density per column
    // Some columns are mostly empty, others are busy
    float baseDensity = 0.05 + colSeed * 0.25; 

    vec3 color = vec3(0.0);
    if (n < baseDensity) {
        // Particles vary in length based on the column's pitch
        float particleLen = rainVirtualH * 0.6;
        float headDist  = mod(scrollY, particleLen);
        
        float brightness = smoothstep(particleLen, 0.5, headDist); 
        
        vec3 streamColor = mix(BLUE, CYAN, brightness);
        color = streamColor * (0.15 + brightness * 0.85);
    }

    fragColor = vec4(clamp(color, 0.0, 1.0), 1.0);
}
