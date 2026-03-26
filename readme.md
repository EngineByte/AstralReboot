# AstralEngine
AstralEngine is a simulation and game engine prototype.  This engine was 
designed to serve as a research and dev platform for large and very-large
physics simulation, procedural worlds, and advanced/experimental rendering.

This engine accomplishes fast, data-oriented computation with its core 
Entity Component System (ECS) architecture.  ECS also enables fast and
scaleable development with the use of supporting resource and asset registry,
and other UX management tools.  Other supporting features include systems
scheduling, dense memory management, customizeable rendering pipelines, and
built-in introspection tools for debugging and future dev support.

AstralEngine will feature a unique hybrid system for simulation and rendering.
This hybrid system is built upon the concept of having a 'duality' of two
world data structures and seamless/inexpensive methods of mutating both
datasets simultaneously.

The first world-data structure is the 'voxel', which is a very well adapted
game-design architecture (think Minecraft and Timberborn) that is well suited
for hardcore physics modeling and simulation.

The second of the 'duality' of world-data is the Signed Distance Function (SDF).
While this data and computation model is not new, the adaption of SDF in game
development is explored to a lesser extent.  Although there are existing high-
profile examples (A Game About Digging a Hole).  

A guiding principle in the design of this dual-data system is the idea that
different simulation computations are more efficiently done in SDF-realm, and
others might be better suited with a voxel system.  The same goes with
drawing/rendering.  Being able to efficiently keep these two datasets synced
makes this a powerful and stable world-representation.  In reality, one dataset
(likely the voxels) will serve as a master/true, and the other (SDF) will be
generated as needed (and will employ caching to improve memory performance).


## Goals

Primary goals:

- Build a high-performance and highly useable ECS kernal, and upon this kernal:
- Build a flexible and robust GPU-accelerated rendering system using OpenGL
- Build an efficient and stable voxel system
- Develop a fast and cacheable SDF system with full suite of utilities
- Integrate Voxel and SDF systems into a landmark physics and rendering module
- Build a complete suite of core physics systems
- Develop a basic game development environment
- Complete a MVP demonstration/game that is interactive and fun

## Core Architectures

### Entity Component System (ECS) (PROTOTYPE STABLE)
The ECS kernal has the following core components:
- Entity Allocator
- Components, Stores and Component Store Registry
- Systems and System Registry
- ECS Command Buffer
- Data Query
- Resource Registry
- System Scheduler
- ECS Event Bus

Together, these parts come togethers to serve as a data management kernal.
This is the core skeleton of AstralEngine and provides a data-oriented
framework that all additional modules of the program will be build upon.

The core principle in ECS architecture is Structure of Arrays (SoA) data
storage that allows for fast, linear computational runs that maximizes
data caching and minimizes memory management costs in very large simulations.

#### Entity Allocator (PROTOTYPE STABLE)
An 'Entity' is a simple integer label for an empty 'something'.  An Entity
gains traits and behaviors by attaching 'Components'.  For example,
an enemy in the game might have an 'Entity' in the ECS programming that is
simply the integer '302'.  '302' can be literally anything in the programming
or it can be nothing.  It is not until 'enemy' and 'aggressive' and 
'targets player' components are attached to '302' that it becomes meaningful.
And furthermore, the 'meaning' is defined by what 'systems' act on each
'component'.  This is aligned with a pure vision of 'composition over 
inheritance' principles in programming.

#### Store Registry (PROTOTYPE STABLE)
A 'Component' is a set of data that defines something about an entity.
For example, a 'Player-Controlled' component might contain data specifications
on the move-speed, look-sensitivity, and jump-height that an entity with a 
'player-controlled' component will have.

When an entity is given a component, the component data is stored in a dense
set of data along with every other component data of the same type.  If an 
entity is given a 'Position' component, that data will be stored side-by-side
with every single other 'Position' data that has been created or ever will be
created. This SoA architecture is key for very fast computational runs.

A Store Registry is included in the ECS architecture, and this allows for fast
lookups and a highly scaleable architecture.  No matter how many Component
Stores are registered in the application, the coding complexity does not
increase, and the registry allows for simplified UX.

#### System Registry (PROTOTYPE STABLE)
A 'System' is a function that the ECS uses to process an mutate world data. 
For example, a 'Movement' system will process all of the 'Velocity' and
'Position' data within their respective Component Stores, and very quickly apply
velocity to every entity an update its position.  This is done all at one time,
for speed and for reduced bugginess.

#### Command Buffer (PROTOTYPE STABLE)
ECS meta-tasks like adding or removing components, entities or applying simulation
phases are not always needed or desired to be done immediately in a program.  The
Command Buffer allows for such meta-tasks to be queued and completed when able.

#### Query (PROTOTYPE STABLE)
A core function of ECS systems is the ability to easily query a very large
dataset in an inexpensive way. The Query module allows for this to be done in
a quick and intuitive manner.  Query is used in almost all Systems.

Query is used by 'asking' the ECS engine to provide an iterable list of entities
that have a specified set of Components or Tags (no-data components for fast Query)

#### Resource Registry (PROTOTYPE STABLE)
Many parts of an application or game will not work well with ECS data architecture.
Data such as large mesh libraries, Voxel chunks, etc. are more useable as data
pools that the ECS system stores pointers to.  The resource registry allows an
interface to arbitrary resources from within the ECS architecture. For example,
When a complex and large rendering mesh is created, it will be stored in a mesh
data pool, that will grow very large and be unwieldy to try and index with the ECS 
system. The ECS system will keep a 'mesh_id' tag that serves as a pointer to that 
entity's rendering mesh.

Voxel data is also stored in this manner.

#### Scheduler (PROTOTYPE STABLE)
To have many Systems operating on a single sets of Component Store data, this
inherently introduces possibilities of bugs and unwanted physics quirks.  To
help control these complexities, the System Scheduler allows the developer to
define 'phases' and 'orders' that are given to Systems.  These provide a
framework to define WHEN each system works relative to eachother and the
overall application/game loop.
#### Event Bus (TO-DO)

### Assets (PROTOTYPE IN PROGRESS)
### Recipes and Factories (PROTOTYPE IN PROGRESS)
### Rendering (BASIC PIPELINE STABLE)
### Resources (PROTOTYPE STABLE)

### Voxels (PROTOTYPE IN PROGRESS)

### SDF (FUTURE)

### Math and Data

### Input and Windowing

### Bootstrapping

### Application

### Debugging

## Physics Simulation Plan

## Testing Plan

## Users and Logging

## Project Developement

## Requirements
python 3.x
pip

## Run
pip install -r requirements.txt
python __main__.py
