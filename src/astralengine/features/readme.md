# Features

Feature modules define all engine capabilities.

Each feature is self-contained and typically includes:
- components
- stores
- systems
- resources
- an `install(world)` entrypoint

## Examples

- `transform` — spatial data
- `gravity` — n-body simulation
- `frames` — hierarchical coordinate systems
- `voxels` — voxel data and meshing

## Philosophy

Features are additive and modular. The engine is composed by installing features into an ECS world.