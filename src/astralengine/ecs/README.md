# ECS Module

Core data-oriented Entity Component System.

## Responsibilities

- entity lifecycle and identity
- component storage (SoA)
- query and iteration
- system scheduling
- deferred mutation (command buffer)
- resource management

## Design Goals

- high performance (cache-friendly)
- minimal abstraction overhead
- deterministic behavior
- engine-agnostic (no domain knowledge)

## Notes

ECS is intended to be extractable as a standalone library.