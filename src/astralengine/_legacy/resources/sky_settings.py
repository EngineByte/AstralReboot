from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class SkySettings:
    enabled: bool = True
    asset_id: str = "skybox.milkyway"
    sun_dir: tuple[float, float, float] = (0.4, 0.8, 0.2)
    exposure: float = 1.0