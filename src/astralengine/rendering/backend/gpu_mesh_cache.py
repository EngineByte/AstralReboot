from __future__ import annotations

import ctypes as ct
from dataclasses import dataclass

from pyglet import gl

from astralengine.voxels.mesh_pool import MeshData


@dataclass(slots=True)
class GpuMesh:
    vao: int
    vbo: int
    ebo: int
    index_count: int
    stride_bytes: int


class GpuMeshCache:
    """
    GPU-resident mesh cache keyed by mesh_id.
    Assumes vertex layout P3_N3_U2 -> 8 floats / vertex.
    """

    def __init__(self) -> None:
        self._meshes: dict[int, GpuMesh] = {}

    def upload_or_replace(self, mesh_id: int, mesh: MeshData) -> None:
        if mesh_id in self._meshes:
            self._replace(mesh_id, mesh)
        else:
            self._upload_new(mesh_id, mesh)

    def contains(self, mesh_id: int) -> bool:
        return mesh_id in self._meshes

    def get(self, mesh_id: int) -> GpuMesh:
        return self._meshes[mesh_id]

    def draw(self, mesh_id: int) -> None:
        gpu = self._meshes[mesh_id]
        gl.glBindVertexArray(gpu.vao)
        gl.glDrawElements(
            gl.GL_TRIANGLES,
            gpu.index_count,
            gl.GL_UNSIGNED_INT,
            ct.c_void_p(0),
        )
        gl.glBindVertexArray(0)

    def delete(self, mesh_id: int) -> None:
        gpu = self._meshes.pop(mesh_id)

        vao = gl.GLuint(gpu.vao)
        vbo = gl.GLuint(gpu.vbo)
        ebo = gl.GLuint(gpu.ebo)

        gl.glDeleteVertexArrays(1, ct.byref(vao))
        gl.glDeleteBuffers(1, ct.byref(vbo))
        gl.glDeleteBuffers(1, ct.byref(ebo))

    def clear(self) -> None:
        for mesh_id in list(self._meshes.keys()):
            self.delete(mesh_id)

    def _upload_new(self, mesh_id: int, mesh: MeshData) -> None:
        vao = gl.GLuint()
        vbo = gl.GLuint()
        ebo = gl.GLuint()

        gl.glGenVertexArrays(1, ct.byref(vao))
        gl.glGenBuffers(1, ct.byref(vbo))
        gl.glGenBuffers(1, ct.byref(ebo))

        gl.glBindVertexArray(vao.value)

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo.value)
        gl.glBufferData(
            gl.GL_ARRAY_BUFFER,
            mesh.verts.nbytes,
            mesh.verts.ctypes.data_as(ct.POINTER(gl.GLfloat)),
            gl.GL_STATIC_DRAW,
        )

        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, ebo.value)
        gl.glBufferData(
            gl.GL_ELEMENT_ARRAY_BUFFER,
            mesh.indices.nbytes,
            mesh.indices.ctypes.data_as(ct.POINTER(gl.GLuint)),
            gl.GL_STATIC_DRAW,
        )

        stride_bytes = mesh.stride_floats * 4
        self._setup_vertex_layout(stride_bytes)

        gl.glBindVertexArray(0)

        self._meshes[mesh_id] = GpuMesh(
            vao=vao.value,
            vbo=vbo.value,
            ebo=ebo.value,
            index_count=mesh.index_count,
            stride_bytes=stride_bytes,
        )

    def _replace(self, mesh_id: int, mesh: MeshData) -> None:
        gpu = self._meshes[mesh_id]

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, gpu.vbo)
        gl.glBufferData(
            gl.GL_ARRAY_BUFFER,
            mesh.verts.nbytes,
            mesh.verts.ctypes.data_as(ct.POINTER(gl.GLfloat)),
            gl.GL_STATIC_DRAW,
        )

        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, gpu.ebo)
        gl.glBufferData(
            gl.GL_ELEMENT_ARRAY_BUFFER,
            mesh.indices.nbytes,
            mesh.indices.ctypes.data_as(ct.POINTER(gl.GLuint)),
            gl.GL_STATIC_DRAW,
        )

        gpu.index_count = mesh.index_count

    def _setup_vertex_layout(self, stride_bytes: int) -> None:
        gl.glEnableVertexAttribArray(0)
        gl.glVertexAttribPointer(
            0, 3, gl.GL_FLOAT, gl.GL_FALSE, stride_bytes, ct.c_void_p(0)
        )

        gl.glEnableVertexAttribArray(1)
        gl.glVertexAttribPointer(
            1, 3, gl.GL_FLOAT, gl.GL_FALSE, stride_bytes, ct.c_void_p(12)
        )

        gl.glEnableVertexAttribArray(2)
        gl.glVertexAttribPointer(
            2, 2, gl.GL_FLOAT, gl.GL_FALSE, stride_bytes, ct.c_void_p(24)
        )