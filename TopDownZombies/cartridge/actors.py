"""
zombies game: actors
"""
from .glvars import pyv


__all__ = [
    'new_player'
]

Vector2d = pyv.Vector2d

LINE_COLOR = 'antiquewhite2'
LINE_THICKNESS = 2
SHIP_DASH_RANGE = 55
SHIP_DELTA_ANGLE = 0.04
SHIP_SPEED_CAP = 192
SHIP_RAD = 5
SHIP_COLOR = (119, 255, 0)


def new_player(pos_xy):
    data = {
        "pos": Vector2d(*pos_xy),
        "angle": 0,
        "speed": Vector2d(),
        "scr_size": pyv.vars.screen.get_size()
    }

    # -------------------
    # utilitary functions
    def ensure_ok_pos(this):
        maxw, maxh = this.scr_size
        if this.pos.x < 0:
            this.pos.x += maxw
        elif this.pos.x >= maxw:
            this.pos.x -= maxw

        if this.pos.y < 0:
            this.pos.y += maxh
        elif this.pos.y >= maxh:
            this.pos.y -= maxh

    def update_speed_vect(this):
        pass

    # --------
    # behavior
    # def on_thrust(this, ev):
    #     pass
    #
    # def on_brake(this, ev):
    #     pass

    return pyv.new_actor('playen', locals())
