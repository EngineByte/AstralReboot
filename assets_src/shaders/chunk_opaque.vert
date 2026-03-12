#version 330 core

layout(location=0) in vec3 aPos;
layout(location=1) in vec3 aNorm;
layout(location=2) in vec2 aUV;

uniform mat4 model;
uniform mat4 view;
uniform mat4 proj;

out vec3 fPos;
out vec3 fNorm;
out vec2 fUV;

void main(){
    vec4 world_pos = model * vec4(aPos, 1.0);
    fPos = world_pos.xyz;
    fNorm = mat3(model) * aNorm;
    fUV = aUV;

    gl_Position = proj * view * world_pos;
}