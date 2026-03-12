#version 330 core

in vec3 vDir;
out vec4 FragColor;

uniform samplerCube uSkybox;
uniform float uExposure;

void main() {
    vec3 color = texture(uSkybox, normalize(vDir)).rgb;
    color *= uExposure;
    FragColor = vec4(color, 1.0);
}