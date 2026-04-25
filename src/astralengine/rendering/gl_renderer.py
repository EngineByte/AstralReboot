from __future__ import annotations

from pyglet import gl
import numpy as np
import ctypes as ct

from astralengine.assets.builtins.cube import build_cube_mesh
from astralengine.rendering.backend import RenderBackend
from astralengine.rendering.mesh_pool import MeshPool
from astralengine.resources.camera_state import CameraState
from astralengine.resources.render_queue import RenderQueue
from astralengine.rendering.shader import ShaderProgram
from astralengine.math.math_quat import quat_to_mat4, quat_conjugate


VERT_SRC = b'''
#version 330 core
layout (location = 0) in vec3 aPos;

uniform mat4 uModel;
uniform mat4 uView;
uniform mat4 uProj;

void main()
{
    gl_Position = uProj * uView * uModel * vec4(aPos, 1.0);
}
'''

FRAG_SRC = b'''
#version 330 core
out vec4 FragColor;

void main()
{
    FragColor = vec4(0.85, 0.85, 0.92, 1.0);
}
'''


def _perspective_matrix(
    fov_y_degrees: float,
    aspect: float,
    near_clip: float,
    far_clip: float,
) -> np.ndarray:
    fov_rad = np.radians(fov_y_degrees)
    f = 1.0 / np.tan(fov_rad / 2.0)

    mat = np.zeros((4, 4), dtype=np.float32)
    mat[0, 0] = f / aspect
    mat[1, 1] = f
    mat[2, 2] = (far_clip + near_clip) / (near_clip - far_clip)
    mat[2, 3] = (2.0 * far_clip * near_clip) / (near_clip - far_clip)
    mat[3, 2] = -1.0
    return mat


def _view_matrix_from_camera(
    position: np.ndarray,
    orientation: np.ndarray
) -> np.ndarray:
    '''
    Temporary translation-only camera.

    This matches your current demo because camera rotation is zero.
    '''
    matpos = np.identity(4, dtype=np.float32)
    matpos[:3, 3] = -position

    matrot = quat_to_mat4(quat_conjugate(orientation))

    mat = np.array([
        [-1.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [0.0, 0.0, -1.0, 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ], dtype=np.float32) @ matrot @ matpos

    return mat


class GLRenderer(RenderBackend):
    __slots__ = (
        '_window',
        '_initialized',
        '_mesh_pool',
        '_program',
        '_u_model',
        '_u_view',
        '_u_proj',
    )

    def __init__(self, window) -> None:
        self._window = window
        self._initialized = False
        self._mesh_pool = MeshPool()
        self._program = 0
        self._u_model = -1
        self._u_view = -1
        self._u_proj = -1

    def initialize(self) -> None:
        if self._initialized:
            return

        self._window.switch_to()
        self._window.set_viewport()

        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glEnable(gl.GL_CULL_FACE)
        gl.glCullFace(gl.GL_BACK)
        gl.glFrontFace(gl.GL_CCW)

        self._program = ShaderProgram(
            vertex_source=VERT_SRC,
            fragment_source=FRAG_SRC,
        )

        self._u_model = gl.glGetUniformLocation(self._program.handle, b'uModel')
        self._u_view = gl.glGetUniformLocation(self._program.handle, b'uView')
        self._u_proj = gl.glGetUniformLocation(self._program.handle, b'uProj')

        vertices, indices = build_cube_mesh()
        self._mesh_pool.upload_indexed_positions('cube', vertices, indices)

        self._initialized = True

    def begin_frame(self) -> None:
        self._window.switch_to()
        self._window.set_viewport()

        gl.glClearColor(0.08, 0.08, 0.12, 1.0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

    def render_scene(
        self,
        render_queue: RenderQueue,
        camera_state: CameraState,
    ) -> None:
        if not self._initialized:
            self.initialize()

        if not camera_state.is_valid:
            return

        width = max(1, self._window.width)
        height = max(1, self._window.height)
        aspect = width / height

        proj = _perspective_matrix(
            fov_y_degrees=camera_state.fov_y_degrees,
            aspect=aspect,
            near_clip=camera_state.near_clip,
            far_clip=camera_state.far_clip,
        )
        view = _view_matrix_from_camera(camera_state.position, camera_state.orientation)

        self._program.use()

        gl.glUniformMatrix4fv(
            self._u_view,
            1,
            gl.GL_FALSE,
            view.flatten('F').ctypes.data_as(ct.POINTER(gl.GLfloat)),
        )
        gl.glUniformMatrix4fv(
            self._u_proj,
            1,
            gl.GL_FALSE,
            proj.flatten('F').ctypes.data_as(ct.POINTER(gl.GLfloat)),
        )

        for packet in render_queue.packets:
            if packet.mesh_id != 'cube':
                continue

            gl.glUniformMatrix4fv(
                self._u_model,
                1,
                gl.GL_FALSE,
                packet.model_matrix.flatten('F').ctypes.data_as(
                    ct.POINTER(gl.GLfloat)
                ),
            )
            self._mesh_pool.draw('cube')

    def end_frame(self) -> None:
        self._window.swap_buffers()

    def shutdown(self) -> None:
        self._window.switch_to()
        self._mesh_pool.shutdown()
        self._initialized = False