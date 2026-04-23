from __future__ import annotations

import ctypes as ct
from dataclasses import dataclass

from pyglet import gl

import numpy as np
import numpy.typing as npt


FloatArray = npt.NDArray[np.float32]
UIntArray = npt.NDArray[np.uint32]


@dataclass(slots=True)
class GPUMesh:
    vao: int
    vbo: int
    ebo: int
    index_count: int


class MeshPool:
    '''
    Minimal GPU mesh registry.
    '''

    __slots__ = ('_meshes',)

    def __init__(self) -> None:
        self._meshes: dict[str, GPUMesh] = {}

    def has_mesh(self, mesh_id: str) -> bool:
        return mesh_id in self._meshes

    def upload_indexed_positions(
        self,
        mesh_id: str,
        vertices: FloatArray,
        indices: UIntArray,
    ) -> None:
        vao = gl.GLuint()
        vbo = gl.GLuint()
        ebo = gl.GLuint()

        gl.glGenVertexArrays(1, ct.byref(vao))
        gl.glGenBuffers(1, ct.byref(vbo))
        gl.glGenBuffers(1, ct.byref(ebo))

        gl.glBindVertexArray(vao)

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)
        gl.glBufferData(
            gl.GL_ARRAY_BUFFER,
            vertices.nbytes,
            vertices.ctypes.data_as(ct.POINTER(gl.GLfloat)),
            gl.GL_STATIC_DRAW,
        )

        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, ebo)
        gl.glBufferData(
            gl.GL_ELEMENT_ARRAY_BUFFER,
            indices.nbytes,
            indices.ctypes.data_as(ct.POINTER(gl.GLuint)),
            gl.GL_STATIC_DRAW,
        )

        # location = 0 -> vec3 position
        gl.glEnableVertexAttribArray(0)
        gl.glVertexAttribPointer(
            0,
            3,
            gl.GL_FLOAT,
            gl.GL_FALSE,
            3 * vertices.itemsize,
            ct.c_void_p(0),
        )

        gl.glBindVertexArray(0)

        self._meshes[mesh_id] = GPUMesh(
            vao=vao.value,
            vbo=vbo.value,
            ebo=ebo.value,
            index_count=int(indices.size),
        )

    def draw(self, mesh_id: str) -> None:
        mesh = self._meshes[mesh_id]
        gl.glBindVertexArray(mesh.vao)
        gl.glDrawElements(
            gl.GL_TRIANGLES, 
            mesh.index_count, 
            gl.GL_UNSIGNED_INT, 
            ct.c_void_p(0)
        )
        gl.glBindVertexArray(0)

    def shutdown(self) -> None:
        for mesh in self._meshes.values():
            vao = gl.GLuint(mesh.vao)
            vbo = gl.GLuint(mesh.vbo)
            ebo = gl.GLuint(mesh.ebo)
            gl.glDeleteVertexArrays(1, vao)
            gl.glDeleteBuffers(1, vbo)
            gl.glDeleteBuffers(1, ebo)
        self._meshes.clear()