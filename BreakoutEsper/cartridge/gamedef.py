import random

from . import glvars
from .classes import *
from .glvars import pyv, ecs


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
    bcy = glvars.BLOCKS_STARTING_Y
    for column in range(5):
        bcx = glvars.BLOCKS_STARTING_X
        for row in range(round(glvars.blocks_limit)):
            precursor_rect = (bcx, bcy, glvars.BLOCK_W, glvars.BLOCK_H)
            ecs.create_entity(
                Body(*precursor_rect),
                BlockSig()  # to tag entity as being a block
            )
            bcx += glvars.BLOCK_W + glvars.BLOCK_SPACING
        bcy += glvars.BLOCK_H + glvars.BLOCK_SPACING


@pyv.declare_begin
def init_game(vmst=None):
    pyv.init(wcaption='Pyv Breaker')
    glvars.screen = s_obj = pyv.get_surface()
    glvars.set_scr_size(s_obj.get_size())
    ft = pyv.new_font_obj(None, glvars.classic_ftsize)
    glvars.start_game_label = ft.render('Press space to start the game', True, 'white')

    # add my entities
    player_create()
    ball_create()
    blocks_create()

    # add my processors
    all_proc = (
        EventProcessor(),
        PhysicsProcessor(),
        EndgameProcessor(),
        GfxProcessor()
    )
    list(map(ecs.add_processor, all_proc))

    #  mini docs for ecs.*
    # ------------------
    # .create_entity()
    # .delete_entity(entity)
    # .add_component(entity, component_instance)
    # .remove_component(entity, ComponentType)

    # .try_component(entity, ComponentType)
    # .get_component(ComponentType)
    # .get_components(ComponentTypeA, ComponentTypeB, Etc)
    # .component_for_entity(entity, ComponentType)
    # .components_for_entity(entity)
    # .has_component(entity, ComponentType)

    # .add_processor(processor_instance)
    # .remove_processor(ProcessorType)
    # .process()


@pyv.declare_update
def upd(time_info=None):
    if glvars.prev_time_info is None:
        glvars.prev_time_info = time_info
    else:
        dt = (time_info - glvars.prev_time_info)
        glvars.prev_time_info = time_info
        ecs.process(dt)
        pyv.flip()


@pyv.declare_end
def done(vmst=None):
    pyv.close_game()
    print('gameover!')
