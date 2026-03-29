from astralengine.ecs.core.world import ECSWorld
from astralengine.game.recipes.gravity_sandbox import build_gravity_sandbox_scene
from astralengine.game.recipes.frame_sandbox import build_frame_sandbox

def install_start_scene(world: ECSWorld) -> None:
    '''
    Install the initial scene.
    '''
    build_gravity_sandbox_scene(world)