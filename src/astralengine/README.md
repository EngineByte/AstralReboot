# AstralEngine

AstralEngine is a data-oriented simulation and rendering engine built in Python using OpenGL.

It is designed to support:
- large-scale voxel worlds
- multi-frame coordinate systems (planets, ships)
- extensible simulation systems (gravity, heat, etc.)
- high-performance ECS-based architecture

## Structure

- `ecs/` — core data-oriented entity-component system
- `features/` — modular engine subsystems
- `bootstrap/` — application composition
- `rendering/` — graphics backend
- `game/` — Astral Trail gameplay layer

## Status

Active development. Architecture-first approach.