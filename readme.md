# AstralReboot

A data-oriented simulation engine and game prototype exploring large-scale voxel worlds, multi-frame physics, and emergent systems.

---

## Overview

AstralReboot is a ground-up engine and game project built to explore a different approach to simulation:

* **Voxel worlds at multiple scales** — from small structures to planetary bodies
* **Hierarchical coordinate frames** — enabling planets, ships, and local systems to coexist
* **Data-oriented ECS architecture** — optimized for performance and scalability
* **Real-time physics simulation** — including n-body gravity and future systems
* **Modular feature design** — systems like gravity, voxels, and heat are independent and composable

The project serves both as:

* a long-term game development effort (**Astral Trail**)
* a technical platform for experimenting with simulation systems and engine architecture

---

## Design Philosophy

This project prioritizes:

* **Data-oriented design**
  Cache-efficient ECS, batched updates, and minimal abstraction overhead

* **Scalable simulation**
  Systems designed to handle everything from local interactions to planetary-scale environments

* **Modular features**
  Engine capabilities are built as independent, installable subsystems

* **Engine-first development**
  Building a strong simulation substrate before layering gameplay

The goal is to enable **emergent, physically grounded worlds**, not just scripted environments.

---

## Current Features

* ECS-based simulation core (SoA storage, query system, scheduler)
* Instanced rendering of large numbers of objects
* N-body gravitational simulation
* Modular feature architecture (in progress)

---

## In Progress

* Frame system for independent coordinate spaces (planets, ships)
* Chunked voxel world with streaming
* Level-of-detail (LoD) representations
* GPU-driven culling and rendering optimizations
* Additional simulation systems (heat, materials, fluids)

---

## Project Structure

```
src/astralengine/
    ecs/        # Core data-oriented ECS
    features/   # Modular engine subsystems
    rendering/  # OpenGL rendering backend
    bootstrap/  # Application composition
    game/       # Game-specific logic (Astral Trail)

docs/           # Architecture and design documentation

tests/          # Validation and integration testing

```

---

## Getting Started

```bash
pip install -e .
python -m astralengine
```

**Requirements:**

* Python 3.12+
* OpenGL-capable GPU

---

## Status

Active development.

This is an experimental engine with evolving architecture. Systems are being built iteratively with a focus on long-term scalability, performance, and clarity of design.

---

## Roadmap

* [ ] Frame-based spatial system
* [ ] Chunked voxel terrain
* [ ] GPU-based culling and streaming
* [ ] Advanced simulation systems (heat, materials, fluids)
* [ ] Playable gameplay prototype (Astral Trail)

---

## About

AstralReboot is a solo development project focused on exploring advanced simulation systems, engine architecture, and data-oriented design.

It serves as both a **technical portfolio** and a **long-term game development effort**.

---

## License

(TBD)
