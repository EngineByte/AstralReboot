#version 330 core

in vec3 fPos;
in vec3 fNorm;
in vec2 fUV;

out vec4 FragColor;

void main() {
    vec3 n = normalize(fNorm);
    vec3 light_dir = normalize(vec3(0.4, 0.8, 0.2));

    float diffuse = max(dot(n, light_dir), 0.0);
    float ambient = 0.2;

    vec3 base = vec3(0.7, 0.75, 0.8);
    vec3 color = base * (ambient + 0.8 * diffuse);

    FragColor = vec4(color, 1.0);
}