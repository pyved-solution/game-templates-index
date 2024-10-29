# from . import glvars
# from . import systems
# from .world import blocks_create, player_create, ball_create
from random import random, choice
from . import glvars
from .constants import *
from .classes import GameflowCtrl, GameWorld
from .actors import *

pyv = kengi = glvars.pyv

from .sprites import Explosion, Obstacle, Player, Tower, BonusItem, Runner, Mob, Item

# TODO if you wanna fix bugs, the most important is :
#  - to fix the sound: use a sound controller + use several channels in local ctx
#  - find why icons are blinking and remove this effect
# --- constants


# ----------- global vars
g = None
saved_t = None
# kengi = katasdk.kengi

pg = kengi.pygame
vec = pg.math.Vector2
WARP_BACK_SIG = [2, 'niobepolis']
glclock = None
basefont = None  # will store a (pygame)font object




@pyv.declare_begin
def game_enter(vmst=None):
    global g, glclock, basefont
    kengi.init(1)
    kengi.get_ev_manager().setup()

    basefont = pg.font.Font(None, 29)
    glclock = kengi.pygame.time.Clock()

    g = GameWorld()
    g.screen = kengi.get_surface()

    ctrl = GameflowCtrl(g)

    g.load_data()
    g.load_level()
    ctrl.turn_on()
    print('controls:---')
    print('[g] for debug')
    print('[p] for pause')
    print('[c] change weapon')
    print('[x] land mine')
    print('[space] shoot')

    tmp = new_player((8,9))
    print(tmp)


@pyv.declare_update
def game_update(timeinfo=None):
    global saved_t

    # related to ctrls
    # for weird reasons arrow keys are handled differentrly than other keys in events
    # self.UP_KEY, \
    # self.DOWN_KEY, \
    # self.START_KEY, \
    # self.BACK_KEY, \
    # self.LEFT_KEY, \
    # self.RIGHT_KEY = False, False, False, False, False, False

    for event in pg.event.get():
        if event.type == pg.QUIT:
            pyv.vars.gameover = True
            continue
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                pyv.vars.gameover = True
            elif event.key == pg.K_g:
                print(' -- - -- debug -- - - - -')
                g.draw_debug = not g.draw_debug
                print('debug mode: {}'.format(g.draw_debug))
            elif event.key == pg.K_p:
                g.paused = not g.paused
                print('pause: {}'.format(g.paused))
            # Not the best design, but for convenience putting player action keys here
            elif event.key == pg.K_c:
                g.player.change_weapon()
            elif event.key == pg.K_x:
                g.player.place_mine()

    # - logic
    if saved_t is None:
        g.dt = 0
    else:
        g.dt = (timeinfo - saved_t)
    saved_t = timeinfo
    g.update()

    # - display
    g.draw_scene()
    label = basefont.render(
        '{:.2f}'.format(glclock.get_fps()),
        True,
        (250, 13, 55),
        (0, 0, 0)
    )
    scr = kengi.vars.screen
    scr.blit(label, (scr.get_size()[0] - 96, 16))
    kengi.flip()


@pyv.declare_end
def game_exit(vmstate=None):
    kengi.quit()


# pyv = glvars.pyv
# pygame = pyv.pygame
#
#
# @pyv.declare_begin
# def init_game(vmst=None):
#     pyv.init()
#     screen = pyv.get_surface()
#     # glvars.screen = screen
#     pyv.init(wcaption='Pyv Breaker')
#
#     pyv.define_archetype('player', ('body', 'speed', 'controls'))
#     pyv.define_archetype('block', ('body', ))
#     pyv.define_archetype('ball', ('body', 'speed_Y', 'speed_X'))
#
#     blocks_create()
#     player_create()
#     ball_create()
#     pyv.bulk_add_systems(systems)
#
#
# @pyv.declare_update
# def upd(time_info=None):
#     if glvars.prev_time_info:
#         dt = (time_info - glvars.prev_time_info)
#     else:
#         dt = 0
#     glvars.prev_time_info = time_info
#
#     pyv.systems_proc(dt)
#     pyv.flip()
#
#
# @pyv.declare_end
# def done(vmst=None):
#     pyv.close_game()
#     print('gameover!')
