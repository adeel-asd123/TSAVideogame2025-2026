#version 300 es
precision mediump float;
out vec4 fragColor;

float linearizeDepth(float z) {
    float near = 1.0;
    float far = 100.0;
    return (2.0 * near) / (far + near - z * (far - near));
}

vec4 packDepth(const float depth) {
    const vec4 bitSh = vec4(256.0*256.0*256.0, 256.0*256.0, 256.0, 1.0);
    const vec4 bitMsk = vec4(0.0, 1.0/256.0, 1.0/256.0, 1.0/256.0);
    vec4 comp = fract(depth * bitSh);
    comp -= comp.xxyz * bitMsk;
    return comp;
}

void main() {
    float linearDepth = linearizeDepth(gl_FragCoord.z);
    fragColor = packDepth(linearDepth);
}
