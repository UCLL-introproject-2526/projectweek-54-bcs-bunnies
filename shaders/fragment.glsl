#version 330 core
in vec2 TexCoord;
out vec4 FragColor;

void main() {
    float borderThickness = 0.05; // width of border
    float alpha = 0.6;            // transparency

    if (TexCoord.x < borderThickness || TexCoord.x > 1.0 - borderThickness ||
        TexCoord.y < borderThickness || TexCoord.y > 1.0 - borderThickness) {
        FragColor = vec4(1.0, 0.0, 0.0, alpha); // transparent red
    } else {
        FragColor = vec4(0.0, 0.0, 0.0, 0.0);   // fully transparent
    }
}