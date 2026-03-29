# ECS Overview

## Purpose

The ECS module provides the core data-oriented substrate for AstralEngine.

It is responsible for storing and processing all simulation data in a performant and predictable way.

---

## Core Concepts

### Entities

Entities are lightweight identifiers representing objects in the world.

They contain no data directly and are composed entirely of components.

---

### Components

Components define data.

Examples:

* position
* velocity
* mass
* voxel data
* temperature

Components are stored in **Structure-of-Arrays (SoA)** format for performance.

---

### Stores

Each component type is managed by a dedicated store.

Stores provide:

* dense data arrays
* sparse-to-dense mapping
* efficient add/remove operations
* compact memory layout

---

### Queries

Queries allow systems to iterate over entities with specific component combinations.

They:

* resolve component stores
* provide dense indices for fast access
* support tag inclusion/exclusion

---

### Systems

Systems operate on components.

They:

* run each frame (or phase)
* read and write component data
* contain all simulation logic

---

### Scheduler

The scheduler organizes system execution into phases.

Example phases:

* pre_update
* update
* physics
* post_update
* render

---

### Command Buffer

The command buffer enables safe deferred mutation.

It allows:

* entity creation/destruction
* component addition/removal
* tag updates

without invalidating active queries.

---

### Resources

Resources are singleton-like objects shared across systems.

Examples:

* renderer
* input state
* simulation settings

---

## Design Goals

* **Performance** — cache-friendly memory layout and batched processing
* **Determinism** — predictable update order and behavior
* **Safety** — controlled mutation through deferred operations
* **Simplicity** — minimal abstraction over core operations

---

## Non-Goals

* no domain-specific logic (e.g., voxels, physics, rendering)
* no hidden behavior or implicit side effects

---

## Notes

The ECS is designed to be extractable as a standalone library in the future.
