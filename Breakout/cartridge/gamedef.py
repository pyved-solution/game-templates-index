from . import glvars
from . import systems
from .world import blocks_create, player_create, ball_create

pyv = glvars.pyv
pygame = pyv.pygame


@pyv.declare_begin
def init_game(vmst=None):
    pyv.init()
    screen = pyv.get_surface() 
    # glvars.screen = screen
    pyv.init(wcaption='Pyv Breaker')

    pyv.define_archetype('player', ('body', 'speed', 'controls'))
    pyv.define_archetype('block', ('body', ))
    pyv.define_archetype('ball', ('body', 'speed_Y', 'speed_X'))

    blocks_create()
    player_create()
    ball_create()
    pyv.bulk_add_systems(systems)


@pyv.declare_update
def upd(time_info=None):
    if glvars.prev_time_info:
        dt = (time_info - glvars.prev_time_info)
    else:
        dt = 0
    glvars.prev_time_info = time_info

    pyv.systems_proc(dt)
    pyv.flip()


@pyv.declare_end
def done(vmst=None):
    pyv.close_game()
    print('gameover!')
