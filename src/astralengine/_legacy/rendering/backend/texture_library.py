from __future__ import annotations

from dataclasses import dataclass

from astralengine.old_code.assets.asset_manager import AssetManager
from astralengine.old_code.assets.loaders.cubemap_loader import CubemapLoader
from astralengine.old_code.rendering.backend.cubemap_texture import CubemapTexture


@dataclass(slots=True)
class _CubemapEntry:
    asset_id: str
    texture: CubemapTexture


class TextureLibrary:
    """
    Runtime cache for GPU texture objects.

    For now this focuses on cubemaps.

    Current behavior:
    - If source cubemap faces exist, load them.
    - If cooked cubemap exists but cooked loading is not implemented yet,
      fall back to source if available.
    """

    def __init__(
        self,
        *,
        assets: AssetManager,
        cubemap_loader: CubemapLoader,
    ) -> None:
        self.assets = assets
        self.cubemap_loader = cubemap_loader
        self._cubemaps: dict[str, _CubemapEntry] = {}

    def get_or_load_cubemap(self, asset_id: str) -> CubemapTexture:
        entry = self._cubemaps.get(asset_id)
        if entry is not None:
            return entry.texture

        record = self.assets.require(asset_id)

        if record.kind != "skybox":
            raise ValueError(f"Asset '{asset_id}' is not a skybox/cubemap asset.")

        source_ok = (
            record.source_path is not None
            and record.source_path.exists()
            and record.source_path.is_dir()
        )

        cooked_ok = (
            record.cooked_path is not None
            and record.cooked_path.exists()
            and record.cooked_path.is_file()
        )

        # Prototype behavior:
        # prefer source directory loading until cooked KTX2/DDS loading exists.
        if source_ok:
            tex_id = self.cubemap_loader.load_from_face_directory(record.source_path)
            texture = CubemapTexture(tex_id)

            self._cubemaps[asset_id] = _CubemapEntry(
                asset_id=asset_id,
                texture=texture,
            )
            return texture

        if cooked_ok:
            raise NotImplementedError(
                f"Cooked cubemap exists for '{asset_id}' at {record.cooked_path}, "
                "but cooked cubemap loading is not implemented yet and no source "
                "face directory is available."
            )

        raise FileNotFoundError(
            f"No usable cubemap source found for '{asset_id}'.\n"
            f"source_path={record.source_path}\n"
            f"cooked_path={record.cooked_path}"
        )

    def contains_cubemap(self, asset_id: str) -> bool:
        return asset_id in self._cubemaps

    def clear(self) -> None:
        for entry in self._cubemaps.values():
            entry.texture.delete()
        self._cubemaps.clear()