from . import shared
from . import systems
# from .world import blocks_create, player_create, ball_create
from .glvars import pyv, ecs
from .classes import *
from . import glvars
import random


pygame = pyv.pygame


def player_create():
    player = ecs.create_entity(
        Speed(0.0), Controls(), Body(glvars.scr_size[0]//2, 635, glvars.PL_WIDTH, glvars.PL_HEIGHT)
    )
    glvars.player_entity = player


def ball_create():
    if random.choice((True, False)):  # we select a random direction
        initial_vx = random.uniform(0.33 * glvars.MAX_XSPEED_BALL, glvars.MAX_XSPEED_BALL)
    else:
        initial_vx = random.uniform(-glvars.MAX_XSPEED_BALL, -0.33 * glvars.MAX_XSPEED_BALL)
    glvars.ball_entity = ecs.create_entity(
        Speed(initial_vx, glvars.YSPEED_BALL),
        Body(
            glvars.BALL_INIT_POS[0], glvars.BALL_INIT_POS[1], glvars.BALL_SIZE, glvars.BALL_SIZE
        )
    )


def blocks_create():
    bcy = 0
    for column in range(5):
        bcy = bcy + shared.BLOCK_H + shared.BLOCK_SPACING
        bcx = -shared.BLOCK_W
        for row in range(round(shared.LIMIT)):
            bcx = bcx + shared.BLOCK_W + shared.BLOCK_SPACING
            precursor_rect = (0 + bcx, 0 + bcy, shared.BLOCK_W, shared.BLOCK_H)
            ecs.create_entity(
                Body(*precursor_rect)
            )


@pyv.declare_begin
def init_game(vmst=None):
    pyv.init()
    glvars.screen = screen = pyv.get_surface()
    glvars.scr_size = screen.get_size()

    pyv.init(wcaption='Pyv Breaker')
    print('ecs?', ecs)
    print(' +-------------------------+ ')
    # pyv.define_archetype('player', ('body', 'speed', 'controls'))
    # pyv.define_archetype('block', ('body', ))
    # pyv.define_archetype('ball', ('body', 'speed_Y', 'speed_X'))

    # blocks_create()
    player_create()
    ball_create()
    blocks_create()

    # pyv.bulk_add_systems(systems)
    # -----------------
    # do all the ecs stuff
    # ecs.switch_world('intro')
    # print(ecs.list_worlds())

    # position??
    for proc in (
        EventProcessor(), PhysicsProcessor(), GfxProcessor()
    ):
        ecs.add_processor(proc)

    # ------------------
    #  mini docs
    # ------------------
    # World.create_entity()
    # World.delete_entity(entity)
    # World.add_processor(processor_instance)
    # World.remove_processor(ProcessorType)
    # World.add_component(entity, component_instance)
    # World.remove_component(entity, ComponentType)
    # World.get_component(ComponentType)
    # World.get_components(ComponentTypeA, ComponentTypeB, Etc)
    # World.component_for_entity(entity, ComponentType)
    # World.components_for_entity(entity)
    # World.has_component(entity, ComponentType)
    # World.process()


@pyv.declare_update
def upd(time_info=None):
    if glvars.prev_time_info:
        dt = (time_info - glvars.prev_time_info)
    else:
        dt = 0
    glvars.prev_time_info = time_info

    ev_li = pygame.event.get()
    for ev in ev_li:
        if ev.type == pygame.QUIT:
            pyv.vars.gameover = True
    ecs.process(dt)

    # already done??
    pyv.flip()


@pyv.declare_end
def done(vmst=None):
    pyv.close_game()
    print('gameover!')
