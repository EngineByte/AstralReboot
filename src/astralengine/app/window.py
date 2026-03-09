from pyglet.window import Window

from ecs.world import ECSWorld

class AstralWindow(Window):
    def __init__(self, *args, world: 'ECSWorld', **kwargs):
        super().__init__(*args, 'AstralWindow', **kwargs)
        self.world = world

    def on_draw(self):
        self.world.render()
        #print('AstralWindow on_draw')
        