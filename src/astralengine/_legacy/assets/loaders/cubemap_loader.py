from __future__ import annotations

import ctypes as ct
from pathlib import Path

from pyglet import gl
from PIL import Image


_CUBEMAP_FACE_ORDER: tuple[str, ...] = ("px", "nx", "py", "ny", "pz", "nz")


class CubemapLoader:
    """
    Load cubemap textures from source face directories.

    Current supported source layout:
        <skybox_dir>/
            px.png
            nx.png
            py.png
            ny.png
            pz.png
            nz.png

    Notes:
    - This is an early prototype loader.
    - Later you should prefer cooked runtime formats such as KTX2/DDS.
    """

    def load_from_face_directory(self, skybox_dir: Path) -> int:
        if not skybox_dir.exists() or not skybox_dir.is_dir():
            raise FileNotFoundError(f"Skybox directory not found: {skybox_dir}")

        tex_id = gl.GLuint()
        gl.glGenTextures(1, ct.byref(tex_id))
        gl.glBindTexture(gl.GL_TEXTURE_CUBE_MAP, tex_id.value)

        for i, face_name in enumerate(_CUBEMAP_FACE_ORDER):
            img_path = self._find_face_file(skybox_dir, face_name)
            img = Image.open(img_path).convert("RGBA")
            img = img.transpose(Image.FLIP_TOP_BOTTOM)

            width, height = img.size
            raw = img.tobytes()

            gl.glTexImage2D(
                gl.GL_TEXTURE_CUBE_MAP_POSITIVE_X + i,
                0,
                gl.GL_RGBA,
                width,
                height,
                0,
                gl.GL_RGBA,
                gl.GL_UNSIGNED_BYTE,
                raw,
            )

        gl.glTexParameteri(
            gl.GL_TEXTURE_CUBE_MAP,
            gl.GL_TEXTURE_MIN_FILTER,
            gl.GL_LINEAR,
        )
        gl.glTexParameteri(
            gl.GL_TEXTURE_CUBE_MAP,
            gl.GL_TEXTURE_MAG_FILTER,
            gl.GL_LINEAR,
        )
        gl.glTexParameteri(
            gl.GL_TEXTURE_CUBE_MAP,
            gl.GL_TEXTURE_WRAP_S,
            gl.GL_CLAMP_TO_EDGE,
        )
        gl.glTexParameteri(
            gl.GL_TEXTURE_CUBE_MAP,
            gl.GL_TEXTURE_WRAP_T,
            gl.GL_CLAMP_TO_EDGE,
        )
        gl.glTexParameteri(
            gl.GL_TEXTURE_CUBE_MAP,
            gl.GL_TEXTURE_WRAP_R,
            gl.GL_CLAMP_TO_EDGE,
        )

        gl.glBindTexture(gl.GL_TEXTURE_CUBE_MAP, 0)
        return int(tex_id.value)

    def _find_face_file(self, skybox_dir: Path, face_name: str) -> Path:
        candidates = (
            skybox_dir / f"{face_name}.png",
            skybox_dir / f"{face_name}.jpg",
            skybox_dir / f"{face_name}.jpeg",
            skybox_dir / f"{face_name}.webp",
        )

        for path in candidates:
            if path.exists():
                return path

        raise FileNotFoundError(
            f"Missing cubemap face '{face_name}' in directory: {skybox_dir}"
        )