#version 300 es
precision mediump float;

in vec3 vertex;
in vec3 normal;
in vec2 texcoord_0;  // <- This matches GLTF's embedded UV channel 0

uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 p3d_ModelMatrix;
uniform mat3 p3d_NormalMatrix;
uniform mat4 shadowViewMatrix;

out vec3 fragNormal;
out vec3 fragPos;
out vec4 fragShadowCoord;
out vec2 fragTexCoord;

void main() {
    vec4 worldPos = p3d_ModelMatrix * vec4(vertex, 1.0);
    fragPos = worldPos.xyz;

    fragNormal = normalize(p3d_NormalMatrix * normal);
    fragShadowCoord = shadowViewMatrix * worldPos;
    fragTexCoord = texcoord_0;

    gl_Position = p3d_ModelViewProjectionMatrix * vec4(vertex, 1.0);
}
