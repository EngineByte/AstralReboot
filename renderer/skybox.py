from __future__ import annotations

import ctypes as ct
import numpy as np
import numpy.typing as npt
from pyglet import gl

Mat4 = npt.NDArray[np.float32]
Vec3 = npt.NDArray[np.float32]


skybox_vert = b'''
#version 330 core

layout(location=0) in vec3 aPos;

out vec3 vDir;

uniform mat4 uProj;
uniform mat4 uViewRot;

void main(){
    vDir = aPos;
    vec4 clip = uProj * uViewRot * vec4(aPos, 1.0);
    gl_Position = clip.xyww;
}
'''

skybox_frag = b'''
#version 330 core

in vec3 vDir;
out vec4 FragColor;

uniform samplerCube uSkybox;
uniform vec3 uSunDir;
uniform vec3 uSunColor;
uniform float uSunAngularRadius;
uniform float uSunGlowPower;
uniform float uExposure;

void main(){
    vec3 dir = normalize(vDir);

    vec3 sky = texture(uSkybox, dir).rgb;

    float cosAngle = dot(dir, normalize(uSunDir));

    float outerCos = cos(uSunAngularRadius);
    float innerCos = cos(uSunAngularRadius * 0.5);

    float sunDisc = smoothstep(outerCos, innerCos, cosAngle);
    float sunGlow = pow(max(cosAngle, 0.0), uSunGlowPower);

    vec3 color = sky
        + uSunColor * (5.0 * sunDisc + 1.2 * sunGlow);

    color = vec3(1.0) - exp(-color * uExposure);

    FragColor = vec4(color, 1.0);
}
'''

class SkyboxRenderer:
    def __init__(self, program, cubemap_tex_id: int):
        self.program = program
        self.cubemap_tex_id = cubemap_tex_id

        self.vao = gl.GLuint()
        self.vbo = gl.GLuint()

        self._build_cube()

    def _build_cube(self) -> None:
        verts = np.array([
            -1,  1, -1,   -1, -1, -1,    1, -1, -1,
             1, -1, -1,    1,  1, -1,   -1,  1, -1,

            -1, -1,  1,   -1, -1, -1,   -1,  1, -1,
            -1,  1, -1,   -1,  1,  1,   -1, -1,  1,

             1, -1, -1,    1, -1,  1,    1,  1,  1,
             1,  1,  1,    1,  1, -1,    1, -1, -1,

            -1, -1,  1,   -1,  1,  1,    1,  1,  1,
             1,  1,  1,    1, -1,  1,   -1, -1,  1,

            -1,  1, -1,    1,  1, -1,    1,  1,  1,
             1,  1,  1,   -1,  1,  1,   -1,  1, -1,

            -1, -1, -1,   -1, -1,  1,    1, -1, -1,
             1, -1, -1,   -1, -1,  1,    1, -1,  1,
        ], dtype=np.float32)

        gl.glGenVertexArrays(1, ct.byref(self.vao))
        gl.glGenBuffers(1, ct.byref(self.vbo))

        gl.glBindVertexArray(self.vao)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo)
        gl.glBufferData(
            gl.GL_ARRAY_BUFFER,
            verts.nbytes,
            verts.ctypes.data_as(ct.POINTER(gl.GLfloat)),
            gl.GL_STATIC_DRAW
        )

        gl.glEnableVertexAttribArray(0)
        gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 3 * 4, ct.c_void_p(0))

        gl.glBindVertexArray(0)

    @staticmethod
    def _view_rotation_only(view: Mat4) -> Mat4:
        out = np.array(view, dtype=np.float32, copy=True)
        out[0, 3] = 0.0
        out[1, 3] = 0.0
        out[2, 3] = 0.0
        return out

    def draw(self, sun_dir: np.ndarray,
             sun_radius: float = 0.01, sun_glow_power: float = 512.0,
             exposure: float = 1.0) -> None:

        gl.glDepthMask(gl.GL_FALSE)
        gl.glDepthFunc(gl.GL_LEQUAL)

        gl.glUseProgram(self.program)

        u_sundir_loc = gl.glGetUniformLocation(self.program, b'uSunDir')
        u_sun_angular = gl.glGetUniformLocation(self.program, b'uSunAngularRadius')
        u_sun_glow = gl.glGetUniformLocation(self.program, b'uSunGlowPower')
        u_exposure = gl.glGetUniformLocation(self.program, b'uExposure')
        u_skybox = gl.glGetUniformLocation(self.program, b'uSkybox')

        gl.glUniform3fv(u_sundir_loc, 1, sun_dir.ctypes.data_as(ct.POINTER(gl.GLfloat)))
        gl.glUniform1f(u_sun_angular, np.float32(sun_radius))
        gl.glUniform1f(u_sun_glow, np.float32(sun_glow_power))
        gl.glUniform1f(u_exposure, np.float32(exposure))


        gl.glActiveTexture(gl.GL_TEXTURE0)
        gl.glBindTexture(gl.GL_TEXTURE_CUBE_MAP, self.cubemap_tex_id)
        gl.glUniform1i(u_skybox, 0)

        gl.glBindVertexArray(self.vao)
        gl.glDrawArrays(gl.GL_TRIANGLES, 0, 36)
        gl.glBindVertexArray(0)

        gl.glDepthFunc(gl.GL_LESS)
        gl.glDepthMask(gl.GL_TRUE)

    @classmethod
    def _build_skybox_program(self):
        vert_shader = self._compile_shader(skybox_vert, gl.GL_VERTEX_SHADER)
        frag_shader = self._compile_shader(skybox_frag, gl.GL_FRAGMENT_SHADER)
        
        return self._link_program(vert_shader, frag_shader)
    
    @classmethod
    def _compile_shader(self, src_bytes: bytes, shader_type: int) -> None:
        src_length = gl.GLint(len(src_bytes))
        src_pointer = ct.cast(
            ct.pointer(ct.pointer(ct.create_string_buffer(src_bytes))),
            ct.POINTER(ct.POINTER(gl.GLchar))
        )
        shader = gl.glCreateShader(shader_type)
        gl.glShaderSource(
            shader,
            1,
            src_pointer,
            src_length
        )
        gl.glCompileShader(shader)

        return shader
    
    @classmethod
    def _link_program(self, vert_shader: int, frag_shader: int) -> int:
        program = gl.glCreateProgram()

        gl.glAttachShader(program, vert_shader)
        gl.glAttachShader(program, frag_shader)

        gl.glLinkProgram(program)

        return program
    
    def set_camera(self, view: Mat4, proj: Mat4) -> None:
        view[:3, 3] = (0.0, 0.0, 0.0)
        gl.glUseProgram(self.program)
        _u_view = gl.glGetUniformLocation(self.program, b'uViewRot')
        _u_proj = gl.glGetUniformLocation(self.program, b'uProj')
        gl.glUniformMatrix4fv(
            _u_view,
            1,
            gl.GL_FALSE,
            view.flatten('F').ctypes.data_as(ct.POINTER(gl.GLfloat))
        )

        gl.glUniformMatrix4fv(
            _u_proj,
            1,
            gl.GL_FALSE,
            proj.flatten('F').ctypes.data_as(ct.POINTER(gl.GLfloat))
        )
