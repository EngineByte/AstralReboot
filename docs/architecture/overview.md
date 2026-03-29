# Architecture Overview

## Purpose

AstralEngine is a data-oriented simulation engine designed to support large-scale, emergent worlds through modular systems and efficient data processing.

The architecture is built around three primary layers:

1. **ECS (Entity Component System)** — core data substrate
2. **Features** — modular simulation and engine systems
3. **Application / Game Layer** — composition and usage

---

## Layered Structure

### ECS (Substrate)

The ECS provides:

* entity identity and lifecycle
* component storage (Structure-of-Arrays)
* query-based iteration
* system scheduling
* deferred mutation (command buffer)
* resource management

It is intentionally **engine-agnostic** and contains no domain-specific logic.

---

### Features (Engine Systems)

Features define all engine capabilities.

Examples include:

* transform (spatial data)
* gravity (n-body simulation)
* frames (hierarchical coordinate systems)
* voxels (terrain and volumetric data)
* rendering (visual output)
* heat (future simulation system)

Each feature is:

* self-contained
* responsible for its own components, stores, and systems
* installed into the ECS world via a standard interface

---

### Application / Game Layer

This layer composes the engine into a runnable experience.

It is responsible for:

* creating the ECS world
* installing features
* configuring resources
* building scenes
* running the simulation loop

Game-specific logic (Astral Trail) lives here and does not modify engine internals.

---

## Data Flow (Per Frame)

A typical frame follows this flow:

1. Input and external state updates
2. System execution (by scheduler phase)

   * simulation systems (e.g., gravity, movement)
   * structural systems (e.g., chunk streaming)
3. Rendering submission
4. GPU execution (render pipeline)

All simulation operates on ECS data through queries and systems.

---

## Design Principles

* **Data-oriented design** — prioritize memory layout and cache efficiency
* **Modularity** — features are independent and composable
* **Scalability** — systems must support large numbers of entities and large spatial domains
* **Separation of concerns** — ECS, features, and game logic are clearly isolated

---

## Notes

The architecture is evolving. Design decisions favor long-term scalability and clarity over short-term convenience.
