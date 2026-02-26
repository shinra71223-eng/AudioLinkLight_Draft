// =========================================================================
// Light Rain / Data Stream  (extracted from cyber_clock_v2)
// 88x10 pixel LED output
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
    float fy = floor(uv.y * 10.0);

    vec3 CYAN = vec3(0.0,  0.95, 0.85);
    vec3 BLUE = vec3(0.05, 0.15, 0.90);

    // 列ごとに落下速度をランダム化
    float colSpeed = rand(vec2(fx * 0.37, 1.0)) * 3.0 + 1.0;
    float scroll   = uTime * colSpeed;
    float scrollY  = mod(fy + scroll, 10.0);
    float n        = rand(vec2(fx, floor(scrollY)));

    // 密度(0〜1): 大きいほど粒が多い
    float density = 0.18;

    vec3 color = vec3(0.0);
    if (n < density) {
        float headDist  = mod(scrollY, 5.0);
        float brightness = smoothstep(4.0, 0.0, headDist);  // 頭が明るく尾が暗い
        vec3 streamColor = mix(BLUE, CYAN, brightness);
        color = streamColor * (0.3 + brightness * 0.7);
    }

    fragColor = vec4(clamp(color, 0.0, 1.0), 1.0);
}