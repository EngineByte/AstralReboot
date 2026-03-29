# Features Overview

## Purpose

Features define all engine capabilities in AstralEngine.

They are modular subsystems that extend the ECS with domain-specific behavior.

---

## What is a Feature?

A feature is a self-contained unit that typically includes:

* components
* stores (if required)
* systems
* resources
* an installation function (`install(world)`)

---

## Examples

* **transform** — spatial data (position, rotation, scale)
* **gravity** — n-body physics simulation
* **frames** — hierarchical coordinate systems
* **voxels** — chunked volumetric data
* **rendering** — visual representation
* **heat** — temperature and energy transfer (planned)

---

## Installation

Features are installed into an ECS world during application bootstrap.

Example:

```python
install_transform(world)
install_gravity(world)
install_frames(world)
```

Each feature registers:

* its component stores
* its systems (via scheduler)
* any required resources

---

## Dependencies

Features may depend on other features.

Examples:

* gravity depends on transform
* heat may depend on voxels
* rendering depends on transform

Dependencies should be explicit and respected during installation.

---

## Design Principles

* **Modularity** — features should not depend on unrelated systems
* **Encapsulation** — features own their data and behavior
* **Composability** — features can be combined without modification
* **Clarity** — feature boundaries should be obvious

---

## Adding a Feature

Typical workflow:

1. Create a new feature module
2. Define components
3. Define systems
4. Implement `install(world)`
5. Register stores, systems, and resources

---

## Notes

Features are the primary mechanism for scaling the engine. New capabilities should be added as features rather than modifying existing systems.
