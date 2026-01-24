#version 300 es
precision mediump float;

in vec3 vertex;
uniform mat4 p3d_ModelViewProjectionMatrix;

void main() {
    gl_Position = p3d_ModelViewProjectionMatrix * vec4(vertex, 1.0);
}
