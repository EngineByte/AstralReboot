from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class SceneBootstrapState:
    did_spawn_initial_scene: bool = False


@dataclass(slots=True)
class TestSceneConfig:
    entity_count: int = 100
    initial_x_spacing: float = 1.0
    velocity_x: float = 1.0
    velocity_y: float = 0.25
    lifetime_sec: float = 5.0