from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Dict

import ctypes as ct
import numpy as np
import numpy.typing as npt
from pyglet import gl

FloatArray = npt.NDArray[np.float32]
IndexArray = npt.NDArray[np.uint32]
Mat4 = npt.NDArray[np.float32]

if TYPE_CHECKING:
    from ecs.world import ECSWorld


VERT_BYTES = b'''
#version 330 core

layout(location=0) in vec3 aPos;
layout(location=1) in vec3 aNorm;
layout(location=2) in vec2 aUV;

uniform mat4 view;
uniform mat4 proj;

out vec3 fPos;
out vec3 fNorm;
out vec2 fUV;

void main(){
    fPos = aPos;
    fNorm = aNorm;
    fUV = aUV;

    gl_Position = proj * view * vec4(aPos, 1.0);
}
'''

FRAG_BYTES = b'''
#version 330 core

in vec3 fPos;
in vec3 fNorm;
in vec2 fUV;

out vec4 oHue;

const vec3 lightPos = vec3(1000.0, 1300.0, -750.0);
const vec3 ambientC = vec3(1.0, 1.0, 1.0);
const vec3 diffuseC = vec3(1.0, 1.0, 1.0);
const vec3 surfaceC = vec3(1.0, 0.0, 0.3);
const float ambientI = 0.1;
const float diffuseI = 1.0;
const float alpha = 1.0;

void main(){
    vec3 lightDir = normalize(lightPos - fPos);
    float lambert = max(dot(lightDir, fNorm), 0.0);

    vec3 ambientL = ambientI * ambientC * surfaceC;
    vec3 diffuseL = diffuseI * lambert * diffuseC * surfaceC;
    vec3 oColour = diffuseL + ambientL;

    oHue = vec4(oColour, alpha);
}
'''


@dataclass(slots=True)
class _GpuMesh:
    vao: gl.GLuint
    vbo: gl.GLuint
    ebo: gl.GLuint
    index_count: int


class Renderer:
    def __init__(self) -> None:
        self._program = self._create_program(VERT_BYTES, FRAG_BYTES)
        gl.glUseProgram(self._program)
        self._u_view = gl.glGetUniformLocation(self._program, b'view')
        self._u_proj = gl.glGetUniformLocation(self._program, b'proj')

        self._gpu_meshes: Dict[int, _GpuMesh] = {}

        self._create_test_quad()

        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glEnable(gl.GL_CULL_FACE)
        gl.glCullFace(gl.GL_BACK)
        gl.glFrontFace(gl.GL_CCW)

    def draw_mesh(self, mesh_id: int, verts: FloatArray, indices: IndexArray) -> None:
        if verts.dtype != np.float32:
            verts = verts.astype(np.float32, copy=False)
        if indices.dtype != np.uint32:
            indices = indices.astype(np.uint32, copy=False)

        if verts.ndim != 2 or verts.shape[1] != 8:
            raise ValueError(f"verts must be shape (N, 8), got {verts.shape}")
        if indices.ndim != 1:
            raise ValueError(f"indices must be shape (M,), got {indices.shape}")

        if not verts.flags["C_CONTIGUOUS"]:
            verts = np.ascontiguousarray(verts, dtype=np.float32)
        if not indices.flags["C_CONTIGUOUS"]:
            indices = np.ascontiguousarray(indices, dtype=np.uint32)

        gm = self._gpu_meshes.get(mesh_id)
        if gm is None:
            gm = self._create_gpu_mesh(mesh_id)
        self._upload_gpu_mesh(gm, verts, indices)
        self._draw_gpu_mesh(gm)

    def _create_gpu_mesh(self, mesh_id: int) -> _GpuMesh:
        vao = gl.GLuint(0)
        vbo = gl.GLuint(0)
        ebo = gl.GLuint(0)

        gl.glGenVertexArrays(1, ct.byref(vao))
        gl.glGenBuffers(1, ct.byref(vbo))
        gl.glGenBuffers(1, ct.byref(ebo))

        gl.glBindVertexArray(vao)

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)

        stride = 8 * 4  
        gl.glEnableVertexAttribArray(0)
        gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, stride, ct.c_void_p(0))
    
        gl.glEnableVertexAttribArray(1)
        gl.glVertexAttribPointer(1, 3, gl.GL_FLOAT, gl.GL_FALSE, stride, ct.c_void_p(3 * 4))

        gl.glEnableVertexAttribArray(2)
        gl.glVertexAttribPointer(2, 2, gl.GL_FLOAT, gl.GL_FALSE, stride, ct.c_void_p(6 * 4))

        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, ebo)

        gl.glBindVertexArray(0)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)


        gm = _GpuMesh(vao=vao, vbo=vbo, ebo=ebo, index_count=0)
        self._gpu_meshes[mesh_id] = gm
        return gm

    def _upload_gpu_mesh(self, gm: _GpuMesh, verts: FloatArray, indices: IndexArray) -> None:
        gl.glBindVertexArray(gm.vao)

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, gm.vbo)
        gl.glBufferData(
            gl.GL_ARRAY_BUFFER,
            verts.nbytes,
            verts.ctypes.data_as(ct.c_void_p),
            gl.GL_DYNAMIC_DRAW, 
        )

        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, gm.ebo)
        gl.glBufferData(
            gl.GL_ELEMENT_ARRAY_BUFFER,
            indices.nbytes,
            indices.ctypes.data_as(ct.c_void_p),
            gl.GL_DYNAMIC_DRAW,
        )

        gm.index_count = int(indices.shape[0])

        gl.glBindVertexArray(0)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)

    def _draw_gpu_mesh(self, gm: _GpuMesh) -> None:
        if gm.index_count <= 0:
            return

        gl.glUseProgram(self._program)
        gl.glBindVertexArray(gm.vao)
        gl.glDrawElements(gl.GL_TRIANGLES, gm.index_count, gl.GL_UNSIGNED_INT, ct.c_void_p(0))
        gl.glBindVertexArray(0)

    def begin_frame(self) -> None:
        gl.glClearColor(0.0, 0.0, 0.0, 0.0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

    def set_camera(self, view: Mat4, proj: Mat4) -> None:
        gl.glUseProgram(self._program)

        gl.glUniformMatrix4fv(
            self._u_view,
            1,
            gl.GL_FALSE,
            view.flatten('F').ctypes.data_as(ct.POINTER(gl.GLfloat))
        )

        gl.glUniformMatrix4fv(
            self._u_proj,
            1,
            gl.GL_FALSE,
            proj.flatten('F').ctypes.data_as(ct.POINTER(gl.GLfloat))
        )

    def draw_world(self, world: "ECSWorld") -> None:
        gl.glUseProgram(self._program)
        gl.glBindVertexArray(self._vao)
        gl.glDrawElements(
            gl.GL_TRIANGLES,
            6,
            gl.GL_UNSIGNED_INT,
            0
        )

    def end_frame(self) -> None:
        pass

    def _create_test_quad(self) -> None:
        vertices = np.array([
            [1.0, 1.0, 0.0, 0.0, 0.0, -1.0, 0.0, 1.0],
            [1.0, 0.0, 0.0, 0.0, 0.0, -1.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.0, -1.0, 1.0, 0.0],
            [0.0, 1.0, 0.0, 0.0, 0.0, -1.0, 1.0, 1.0],
        ], dtype=np.float32)

        elements = np.array([0, 1, 2, 2, 3, 0], dtype = np.uint32)

        self._vao= gl.GLuint()
        gl.glGenVertexArrays(1, ct.byref(self._vao))
        gl.glBindVertexArray(self._vao)

        vbo = gl.GLuint()
        gl.glGenBuffers(1, ct.byref(vbo))

        ebo = gl.GLuint()
        gl.glGenBuffers(1, ct.byref(ebo))

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)
        gl.glBufferData(
            gl.GL_ARRAY_BUFFER,
            vertices.flatten().nbytes,
            vertices.flatten().ctypes.data_as(ct.POINTER(gl.GLfloat)),
            gl.GL_STATIC_DRAW
        )

        gl.glEnableVertexAttribArray(0)
        gl.glVertexAttribPointer(
            0,
            3,
            gl.GL_FLOAT,
            gl.GL_FALSE,
            8 * 4,
            ct.c_void_p(0)
        )
        
        gl.glEnableVertexAttribArray(1)
        gl.glVertexAttribPointer(
            1,
            3,
            gl.GL_FLOAT,
            gl.GL_FALSE,
            8 * 4,
            ct.c_void_p(3 * 4)
        )
        
        gl.glEnableVertexAttribArray(2)
        gl.glVertexAttribPointer(
            2,
            2,
            gl.GL_FLOAT,
            gl.GL_FALSE,
            8 * 4,
            ct.c_void_p(6 * 4)
        )

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, ebo)

        gl.glBufferData(
            gl.GL_ELEMENT_ARRAY_BUFFER,
            elements.nbytes,
            elements.ctypes.data_as(ct.POINTER(gl.GLuint)),
            gl.GL_STATIC_DRAW
        )

        gl.glBindVertexArray(0)

    def _create_shader(self, src_bytes: bytes, shader_type) -> int:
        shader = gl.glCreateShader(shader_type)

        src_buff = ct.create_string_buffer(src_bytes)
        src_length = gl.GLint(len(src_bytes))
        src = ct.cast(
            ct.pointer(ct.pointer(src_buff)),
            ct.POINTER(ct.POINTER(gl.GLchar))
        )

        gl.glShaderSource(
            shader,
            1,
            src,
            ct.byref(src_length)
        )

        gl.glCompileShader(shader)

        ok = gl.GLint()
        gl.glGetShaderiv(shader, gl.GL_COMPILE_STATUS, ct.byref(ok))
        if not ok:
            log_length = gl.GLint()
            gl.glGetShaderiv(shader, gl.GL_INFO_LOG_LENGTH, ct.byref(log_length))
            log = ct.create_string_buffer(log_length.value)
            gl.glGetShaderInfoLog(shader, log_length, None, log)
            raise RuntimeError(f'Shader compile error: /n{log.value.decode()}')
        
        return shader
    
    def _create_program(self, vert_bytes: bytes, frag_bytes: bytes) -> int:
        vert = self._create_shader(vert_bytes, gl.GL_VERTEX_SHADER)
        frag = self._create_shader(frag_bytes, gl.GL_FRAGMENT_SHADER)

        program = gl.glCreateProgram()
        gl.glAttachShader(program, vert)
        gl.glAttachShader(program, frag)
        gl.glLinkProgram(program)

        ok = gl.GLint()
        gl.glGetProgramiv(program, gl.GL_LINK_STATUS, ct.byref(ok))
        if not ok:
            log_length = gl.GLint()
            gl.glGetProgramiv(program, gl.GL_INFO_LOG_LENGTH, ct.byref(log_length))
            log = ct.create_string_buffer(log_length.value)
            gl.glGetProgramInfoLog(program, log_length, None, log)
            raise RuntimeError(f'Program link error: /n{log.value.decode()}')
        
        gl.glDeleteShader(vert)
        gl.glDeleteShader(frag)

        return program
    
    def destroy_mesh(self, mesh_id: int) -> None:
        gm = self._gpu_meshes.pop(mesh_id, None)
        if gm is None:
            return
        gl.glDeleteVertexArrays(1, ct.byref(gm.vao))
        gl.glDeleteBuffers(1, ct.byref(gm.vbo))
        gl.glDeleteBuffers(1, ct.byref(gm.ebo))

