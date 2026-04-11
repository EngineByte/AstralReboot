from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Final
import json

from astralengine.app.paths import AppPaths


@dataclass(frozen=True, slots=True)
class AssetRecord:
    """
    Resolved asset metadata.

    Attributes:
        asset_id: Stable logical ID used by the codebase.
        kind: Asset category such as 'shader', 'skybox', 'texture', 'model'.
        source_path: Optional development/source asset path.
        cooked_path: Optional runtime/cooked asset path.
    """
    asset_id: str
    kind: str
    source_path: Path | None
    cooked_path: Path | None


class AssetManager:
    """
    Central asset lookup service.

    This class resolves stable asset IDs into source/cooked filesystem paths.
    Runtime systems should prefer cooked assets whenever possible.

    Current behavior:
    - Uses deterministic conventions for common asset IDs
    - Optionally overlays metadata from cooked_assets/manifest.json if present

    Future growth:
    - hash/version validation
    - cook status checks
    - packfile support
    - asset dependency graphs
    """

    _DEFAULT_SHADER_EXTENSIONS: Final[tuple[str, ...]] = (
        ".vert",
        ".frag",
        ".geom",
        ".comp",
        ".tesc",
        ".tese",
    )

    def __init__(self, paths: AppPaths) -> None:
        self.paths = paths
        self._manifest = self._load_manifest()

    def _load_manifest(self) -> dict[str, dict]:
        """
        Load cooked asset manifest if present.

        Returns an empty dict if:
        - no manifest exists
        - manifest file is empty
        - manifest file contains only whitespace
        """
        manifest_path = self.paths.cooked_assets / "manifest.json"
        if not manifest_path.exists():
            return {}

        try:
            text = manifest_path.read_text(encoding="utf-8")
        except Exception as exc:
            raise RuntimeError(
                f"Failed to read asset manifest: {manifest_path}"
            ) from exc

        if not text.strip():
            return {}

        try:
            data = json.loads(text)
        except Exception as exc:
            raise RuntimeError(
                f"Failed to parse asset manifest JSON: {manifest_path}"
            ) from exc

        if not isinstance(data, dict):
            raise RuntimeError(
                f"Asset manifest must be a JSON object at top level: {manifest_path}"
            )

        return data

    def get(self, asset_id: str) -> AssetRecord:
        """
        Resolve an asset ID into an AssetRecord.

        Resolution order:
        1. explicit manifest entry
        2. convention-based fallback
        """
        entry = self._manifest.get(asset_id)
        if entry is not None:
            return self._record_from_manifest(asset_id, entry)

        return self._record_from_convention(asset_id)

    def require(self, asset_id: str) -> AssetRecord:
        """
        Resolve an asset and require that at least one backing file exists.
        """
        record = self.get(asset_id)
        if record.source_path is None and record.cooked_path is None:
            raise FileNotFoundError(f"Asset '{asset_id}' could not be resolved.")

        if record.cooked_path is not None and record.cooked_path.exists():
            return record

        if record.source_path is not None and record.source_path.exists():
            return record

        raise FileNotFoundError(
            f"Asset '{asset_id}' resolved, but no existing file was found.\n"
            f"source_path={record.source_path}\n"
            f"cooked_path={record.cooked_path}"
        )

    def best_path(self, asset_id: str, prefer_cooked: bool = True) -> Path:
        """
        Return the best existing path for an asset.

        Preference order:
        - cooked then source if prefer_cooked=True
        - source then cooked if prefer_cooked=False
        """
        record = self.require(asset_id)

        primary = record.cooked_path if prefer_cooked else record.source_path
        secondary = record.source_path if prefer_cooked else record.cooked_path

        if primary is not None and primary.exists():
            return primary

        if secondary is not None and secondary.exists():
            return secondary

        raise FileNotFoundError(
            f"No readable path exists for asset '{asset_id}'."
        )

    def cooked_path(self, asset_id: str) -> Path:
        """
        Return cooked path and require that it exists.
        """
        record = self.require(asset_id)
        if record.cooked_path is None or not record.cooked_path.exists():
            raise FileNotFoundError(
                f"Cooked asset not found for '{asset_id}': {record.cooked_path}"
            )
        return record.cooked_path

    def source_path(self, asset_id: str) -> Path:
        """
        Return source path and require that it exists.
        """
        record = self.require(asset_id)
        if record.source_path is None or not record.source_path.exists():
            raise FileNotFoundError(
                f"Source asset not found for '{asset_id}': {record.source_path}"
            )
        return record.source_path
    
    def read_text(
        self,
        asset_id: str,
        *,
        prefer_cooked: bool = True,
        encoding: str = "utf-8",
    ) -> str:
        """
        Read a text asset from the best available path.
        """
        path = self.best_path(asset_id, prefer_cooked=prefer_cooked)
        return path.read_text(encoding=encoding)

    def read_bytes(self, asset_id: str, *, prefer_cooked: bool = True) -> bytes:
        """
        Read a binary asset from the best available path.
        """
        path = self.best_path(asset_id, prefer_cooked=prefer_cooked)
        return path.read_bytes()

    def shader_source(self, asset_id: str) -> str:
        """
        Read shader source text.

        Shader assets usually fall back cleanly to source assets until you
        introduce a shader cooking step.
        """
        return self.read_text(asset_id, prefer_cooked=True, encoding="utf-8")

    def skybox_path(self, name: str, ext: str = ".ktx2") -> Path:
        """
        Convenience helper for cooked skyboxes.
        """
        if not ext.startswith("."):
            ext = "." + ext
        path = self.paths.cooked_assets / "skybox" / f"{name}{ext}"
        if not path.exists():
            raise FileNotFoundError(f"Skybox not found: {path}")
        return path

    def shader_path(self, name: str) -> Path:
        """
        Convenience helper for shader assets by filename.

        Example:
            shader_path("skybox.vert")
        """
        source = self.paths.assets_src / "shaders" / name
        cooked = self.paths.cooked_assets / "shaders" / name

        if cooked.exists():
            return cooked
        if source.exists():
            return source

        raise FileNotFoundError(
            f"Shader '{name}' not found in cooked or source shader directories."
        )

    def _record_from_manifest(self, asset_id: str, entry: dict) -> AssetRecord:
        kind = str(entry.get("kind", "unknown"))

        source_raw = entry.get("source")
        cooked_raw = entry.get("cooked")

        source_path = self._resolve_manifest_path(source_raw)
        cooked_path = self._resolve_manifest_path(cooked_raw)

        return AssetRecord(
            asset_id=asset_id,
            kind=kind,
            source_path=source_path,
            cooked_path=cooked_path,
        )

    def _resolve_manifest_path(self, raw: str | None) -> Path | None:
        if raw is None:
            return None

        path = Path(raw)
        if path.is_absolute():
            return path

        return self.paths.project_root / path

    def _record_from_convention(self, asset_id: str) -> AssetRecord:
        """
        Convention-based fallback for common asset IDs.

        Supported examples:
            shader.chunk_opaque.vert
            shader.chunk_opaque.frag
            shader.skybox.vert
            shader.skybox.frag
            skybox.milkyway
            texture.rock_albedo
            model.test_cube
        """
        if asset_id.startswith("shader."):
            return self._shader_record_from_id(asset_id)

        if asset_id.startswith("skybox."):
            return self._skybox_record_from_id(asset_id)

        if asset_id.startswith("texture."):
            return self._texture_record_from_id(asset_id)

        if asset_id.startswith("model."):
            return self._model_record_from_id(asset_id)

        return AssetRecord(
            asset_id=asset_id,
            kind="unknown",
            source_path=None,
            cooked_path=None,
        )

    def _shader_record_from_id(self, asset_id: str) -> AssetRecord:
        """
        Example:
            shader.chunk_opaque.vert -> assets_src/shaders/chunk_opaque.vert
        """
        _, remainder = asset_id.split(".", 1)

        source_path = self.paths.assets_src / "shaders" / remainder
        cooked_path = self.paths.cooked_assets / "shaders" / remainder

        return AssetRecord(
            asset_id=asset_id,
            kind="shader",
            source_path=source_path,
            cooked_path=cooked_path,
        )

    def _skybox_record_from_id(self, asset_id: str) -> AssetRecord:
        """
        Example:
            skybox.milkyway

        Convention:
            source  -> assets_src/skybox/milkyway/
            cooked  -> cooked_assets/skybox/milkyway.ktx2
        """
        _, name = asset_id.split(".", 1)

        source_dir = self.paths.assets_src / "skybox" / name
        cooked_file = self.paths.cooked_assets / "skybox" / f"{name}.ktx2"

        source_path = source_dir if source_dir.exists() else source_dir
        cooked_path = cooked_file

        return AssetRecord(
            asset_id=asset_id,
            kind="skybox",
            source_path=source_path,
            cooked_path=cooked_path,
        )

    def _texture_record_from_id(self, asset_id: str) -> AssetRecord:
        """
        Example:
            texture.rock_albedo

        Convention:
            source  -> assets_src/textures/rock_albedo.png
            cooked  -> cooked_assets/textures/rock_albedo.ktx2
        """
        _, name = asset_id.split(".", 1)

        source_path = self.paths.assets_src / "textures" / f"{name}.png"
        cooked_path = self.paths.cooked_assets / "textures" / f"{name}.ktx2"

        return AssetRecord(
            asset_id=asset_id,
            kind="texture",
            source_path=source_path,
            cooked_path=cooked_path,
        )

    def _model_record_from_id(self, asset_id: str) -> AssetRecord:
        """
        Example:
            model.test_cube

        Convention:
            source  -> assets_src/models/test_cube.obj
            cooked  -> cooked_assets/models/test_cube.bin
        """
        _, name = asset_id.split(".", 1)

        source_path = self.paths.assets_src / "models" / f"{name}.obj"
        cooked_path = self.paths.cooked_assets / "models" / f"{name}.bin"

        return AssetRecord(
            asset_id=asset_id,
            kind="model",
            source_path=source_path,
            cooked_path=cooked_path,
        )