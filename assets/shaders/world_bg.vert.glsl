#version 300 es
precision mediump float;

// Input from the vertex buffer
in vec4 p3d_Vertex;
uniform mat4 p3d_ModelViewProjectionMatrix;

// Output to the fragment shader
out vec3 skybox_pos;

void main() {
  skybox_pos = p3d_Vertex.xyz;
  gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
}