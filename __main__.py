from __future__ import annotations

import pyglet

from bootstrap.ecs_bootstrap import create_ecs_world
from bootstrap.game_bootstrap import setup_game_world
from renderer.astralwindow import AstralWindow


def main() -> None:
    
    world = create_ecs_world(entity_capacity=1_000_000)

    window = AstralWindow(1280, 720, world=world)
    world.resources.add(AstralWindow, window)

    setup_game_world(world)

    pyglet.clock.schedule(world.update)

    pyglet.app.run()


if __name__ == "__main__":
    main()