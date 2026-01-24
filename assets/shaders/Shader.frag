#version 300 es
precision mediump float;
precision mediump sampler2D;

in vec3 fragNormal;
in vec3 fragPos;
in vec4 fragShadowCoord;
in vec2 fragTexCoord;

uniform vec3 light0_direction;
uniform vec3 light0_color;
uniform vec3 ambient_color;
uniform vec3 cameraPos;


uniform vec4 material_specular;
uniform float material_shininess;

uniform sampler2D diffuseTex;
uniform sampler2D shadowMap;

out vec4 fragColor;

float unpackDepth(vec4 rgba) {
    const vec4 bitShift = vec4(
        1.0 / (256.0 * 256.0 * 256.0),
        1.0 / (256.0 * 256.0),
        1.0 / 256.0,
        1.0
    );
    return dot(rgba, bitShift);
}

float calculateShadow(vec4 shadowCoord) {
    vec3 projCoords = shadowCoord.xyz / shadowCoord.w;
    projCoords = projCoords * 0.5 + 0.5;

    if (projCoords.z > 1.0 || projCoords.x < 0.0 || projCoords.x > 1.0 || projCoords.y < 0.0 || projCoords.y > 1.0)
        return 1.0;

    float fragDepth = projCoords.z;

    float storedDepth = unpackDepth(texture(shadowMap, projCoords.xy));
    float bias = max(0.0005, 0.0025 * tan(acos(dot(normalize(fragNormal), normalize(light0_direction)))));
    bias = clamp(bias, 0.0001, 0.01);

    return (fragDepth - bias) <= storedDepth ? 1.0 : 0.0;
}

void main() {
    vec4 texColor = texture(diffuseTex, fragTexCoord);

    vec3 norm = normalize(fragNormal);
    vec3 lightDir = normalize(-light0_direction);
    vec3 viewDir = normalize(cameraPos - fragPos);
    vec3 reflectDir = reflect(-lightDir, norm);

    float diff = max(dot(norm, lightDir), 0.0);
    diff = mix(0.1, 1.0, diff);
    vec3 halfDir = normalize(lightDir + viewDir);
    float spec = pow(max(dot(norm, halfDir), 0.0), material_shininess);


    vec3 ambient = ambient_color * texColor.rgb;
    vec3 diffuse = diff * light0_color * texColor.rgb;
    vec3 specular = spec * light0_color * material_specular.rgb;

    float shadow = calculateShadow(fragShadowCoord);
    vec3 color = ambient + shadow * (diffuse + specular);

    fragColor = vec4(color, texColor.a);
}
