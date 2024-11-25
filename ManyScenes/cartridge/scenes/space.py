from ..glvars import pyv
from .. import glvars
from .default import new_avatar


# utilitary, helps initializing the scene...
av_space = None


def setup():
    global av_space
    new_scene_painter()
    av_space = new_avatar(50, glvars.scene_dim[1] // 2)
    print('A new avatar actor initiated (->in space)', av_space)


# ----------- my actors, specific to that "jungle" scene --------------
def new_scene_painter():
    data = {
        'bg_color': 'gray',
        'tp_zone_rect': pyv.new_rect_obj(128, 50, 100, 80)
    }

    # detect collision with the rect
    def on_move_avatar(this, ev):
        avatar_data = pyv.peek(av_space)
        pt = avatar_data.x, avatar_data.y
        if this.tp_zone_rect.collidepoint(pt):
            # avatar goes back to the "eden" state position
            avatar_data.x = 50
            avatar_data.y = glvars.scene_dim[1] // 2

            pyv.set_scene(pyv.DEFAULT_SCENE)

    def on_draw(this, ev):
        ev.screen.fill(this.bg_color)
        # draw the rect where the player can teleport
        pyv.draw_rect(ev.screen, 'purple', this.tp_zone_rect, 3)

    return pyv.new_actor('bg_scene_space', locals())
