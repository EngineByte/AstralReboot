from __future__ import annotations

import os
from pathlib import Path


def configure_paths() -> None:
    '''
    Configure runtime paths and ensure core directories exist.

    Environment variables set:
    - ASTRAL_ROOT
    - ASTRAL_SRC
    - ASTRAL_LOG_DIR
    - ASTRAL_ASSET_DIR
    '''
    package_dir = Path(__file__).resolve().parent
    src_dir = package_dir.parent
    root_dir = src_dir.parent.parent

    log_dir = root_dir / 'logs'
    asset_dir = src_dir / 'astralengine' / 'assets'

    log_dir.mkdir(parents=True, exist_ok=True)
    asset_dir.mkdir(parents=True, exist_ok=True)

    os.environ.setdefault('ASTRAL_ROOT', str(root_dir))
    os.environ.setdefault('ASTRAL_SRC', str(src_dir))
    os.environ.setdefault('ASTRAL_LOG_DIR', str(log_dir))
    os.environ.setdefault('ASTRAL_ASSET_DIR', str(asset_dir))