from ..glvars import pyv
from .. import glvars
from .default import new_avatar


# utilitary, helps initializing the scene...
def setup():
    new_bg_painter()
    glvars.av_jungle = new_avatar(50, glvars.scene_dim[1] // 2)
    print('A new avatar actor initiated (->in jungle)', glvars.av_jungle)


# ----------- my actors, specific to that "jungle" scene --------------
def new_bg_painter():
    data = {
        'bg_color': 'black'
    }

    def on_draw(this, ev):
        ev.screen.fill(this.bg_color)
        # after filling the screen with black, imagine i wish to show another image... How to do this?
        # again, it is a simple "blit" to screen operation:
        coordinates = (355, 240)
        ev.screen.blit(
            pyv.vars.images['dummy0'], coordinates
        )

    return pyv.new_actor('bg_scene_jungle', locals())
