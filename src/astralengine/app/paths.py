from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os
import sys


@dataclass(frozen=True, slots=True)
class AppPaths:
    """
    Canonical filesystem locations used by the engine.

    These are resolved once during startup and stored as a
    resource in the ECS world.
    """

    project_root: Path
    src_root: Path

    assets_src: Path
    cooked_assets: Path

    cache: Path
    config: Path
    user_data: Path

    dist: Path

def _detect_project_root() -> Path:
    """
    Locate the repository root.

    Works both in development and installed environments.
    """

    here = Path(__file__).resolve()

    for parent in here.parents:
        if (parent / "pyproject.toml").exists():
            return parent

    return here.parents[4]

def build_paths() -> AppPaths:
    """
    Construct the canonical path structure.
    """

    root = _detect_project_root()

    paths = AppPaths(
        project_root=root,
        src_root=root / "src",

        assets_src=root / "assets_src",
        cooked_assets=root / "cooked_assets",

        cache=root / "cache",
        config=root / "config",
        user_data=root / "user_data",

        dist=root / "dist",
    )

    _ensure_directories(paths)

    return paths

def _ensure_directories(paths: AppPaths) -> None:
    """
    Create runtime directories if they don't exist.
    """

    paths.cache.mkdir(parents=True, exist_ok=True)
    paths.user_data.mkdir(parents=True, exist_ok=True)
    paths.cooked_assets.mkdir(parents=True, exist_ok=True)

def describe_paths(paths: AppPaths) -> str:
    """
    Return a formatted string describing current paths.
    Useful for debugging startup.
    """

    return (
        "\n"
        "AstralEngine Path Configuration\n"
        "--------------------------------\n"
        f"project_root : {paths.project_root}\n"
        f"src_root     : {paths.src_root}\n"
        f"assets_src   : {paths.assets_src}\n"
        f"cooked_assets: {paths.cooked_assets}\n"
        f"cache        : {paths.cache}\n"
        f"config       : {paths.config}\n"
        f"user_data    : {paths.user_data}\n"
        f"dist         : {paths.dist}\n"
    )