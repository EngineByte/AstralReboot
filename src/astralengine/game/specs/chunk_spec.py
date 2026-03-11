from dataclasses import dataclass

@dataclass(slots=True)
class ChunkSpec:
    coord: tuple[int, int, int]
    size: int = 16
    position: tuple[float, float, float] = (0.0, 0.0, 0.0)
    rotation: tuple[float, float, float] = (0.0, 0.0, 0.0)
    linvel: tuple[float, float, float] = (0.0, 0.0, 0.0)
    angvel: tuple[float, float, float] = (0.0, 0.0, 0.0)
    mass: float = 1.0
    gravity_strength: float = 0.0
    fill_value: int = 1
    mesh_id: int = -1
    mark_dirty_remesh: bool = True
    mark_dirty_remodel: bool = True