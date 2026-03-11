from dataclasses import dataclass

from astralengine.app.window import AstralWindow
from astralengine.bootstrap.ecs_bootstrap import create_ecs_world
from astralengine.bootstrap.resource_bootstrap import install_core_resources
from astralengine.bootstrap.render_bootstrap import install_render_pipeline
from astralengine.bootstrap.systems_bootstrap import install_core_systems
from astralengine.bootstrap.scene_bootstrap import install_start_scene


@dataclass
class Application:
    window: AstralWindow
    
    def run(self) -> None:
        self.window.run()
        

def create_application() -> Application:
    '''
    Build full application and return an app object.
    '''
    
    world = create_ecs_world()
    
    install_core_resources(world)
    install_render_pipeline(world)
    install_core_systems(world)
    install_start_scene(world)
    
    window = AstralWindow(world)
    
    return Application(window=window)