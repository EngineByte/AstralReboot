from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from pyglet import gl

from astralengine.old_code.assets.asset_manager import AssetManager
from astralengine.old_code.rendering.backend.shader_program import (
    ShaderProgram,
    compile_shader,
    link_program,
)


@dataclass(slots=True)
class _ShaderProgramEntry:
    name: str
    program: ShaderProgram
    vertex_asset_id: str
    fragment_asset_id: str


class ShaderLibrary:
    """
    Manages compiled OpenGL shader programs.
    """

    def __init__(self, *, assets: AssetManager) -> None:
        self.assets = assets
        self._programs: Dict[str, _ShaderProgramEntry] = {}

    def register_from_asset_ids(
        self,
        *,
        name: str,
        vertex_asset_id: str,
        fragment_asset_id: str,
    ) -> None:
        if name in self._programs:
            raise ValueError(f"Shader program '{name}' already registered.")

        vert_src = self.assets.shader_source(vertex_asset_id)
        frag_src = self.assets.shader_source(fragment_asset_id)

        vert_shader = compile_shader(
            vert_src,
            shader_type=gl.GL_VERTEX_SHADER,
            label=vertex_asset_id,
        )

        frag_shader = compile_shader(
            frag_src,
            shader_type=gl.GL_FRAGMENT_SHADER,
            label=fragment_asset_id,
        )

        program_id = link_program(
            vert_shader,
            frag_shader,
            label=name,
        )

        program = ShaderProgram(
            program_id=program_id,
            name=name,
        )

        self._programs[name] = _ShaderProgramEntry(
            name=name,
            program=program,
            vertex_asset_id=vertex_asset_id,
            fragment_asset_id=fragment_asset_id,
        )

    def get(self, name: str) -> ShaderProgram:
        entry = self._programs.get(name)
        if entry is None:
            raise KeyError(f"Shader program '{name}' not registered.")
        return entry.program

    def has(self, name: str) -> bool:
        return name in self._programs

    def reload(self, name: str) -> None:
        entry = self._programs.get(name)
        if entry is None:
            raise KeyError(f"Shader program '{name}' not registered.")

        vert_src = self.assets.shader_source(entry.vertex_asset_id)
        frag_src = self.assets.shader_source(entry.fragment_asset_id)

        vert_shader = compile_shader(
            vert_src,
            shader_type=gl.GL_VERTEX_SHADER,
            label=entry.vertex_asset_id,
        )

        frag_shader = compile_shader(
            frag_src,
            shader_type=gl.GL_FRAGMENT_SHADER,
            label=entry.fragment_asset_id,
        )

        program_id = link_program(
            vert_shader,
            frag_shader,
            label=name,
        )

        entry.program = ShaderProgram(
            program_id=program_id,
            name=name,
        )

    def stats(self) -> dict:
        return {
            "program_count": len(self._programs),
            "programs": list(self._programs.keys()),
        }