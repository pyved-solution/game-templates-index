import os

from . import glvars
from .glvars import pyv
from . import systems
from .World import World
from .classes import Camera


pyv.bootstrap_e()
pygame = pyv.pygame
ts_prev_frame = None


def init(vms=None):
    pyv.init()
    screen = pyv.get_surface()
    glvars.screen = screen
    pyv.define_archetype('player', (
        'speed', 'accel_y', 'gravity', 'lower_block', 'body', 'camera', 'controls'
    ))
    pyv.define_archetype('block', ['body', ])
    pyv.define_archetype('mob_block', ['body', 'speed', 'bounds', 'horz_flag', ])

    world = World(2128.0, 1255.0)
    world.load_map('my_map')
    glvars.world = world
    world.add_game_obj(
        {'key': 'origin'}
    )
    camera = Camera([-280, -280], world)

    world.create_avatar(camera)
    pyv.bulk_add_systems(systems)


def update(timeinfo):
    glvars.t_now=timeinfo
    pyv.systems_proc(pyv.all_entities(), None)
    pyv.flip()


def close(vms=None):
    pyv.quit()
