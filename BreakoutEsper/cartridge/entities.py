"""
Contains all components that can be used to build your entities (follows the ECS pattern)
"""
from . import glvars
from .glvars import pyv, ecs
import random


# components
# -------------------------------------
class Speed:
    def __init__(self, vx=0.0, vy=0.0):
        self.vx = vx
        self.vy = vy


class Controls:
    def __init__(self):
        self.right = self.left = False


class BlockSig:
    free_b_id = 0

    def __init__(self):
        self.bid = self.__class__.free_b_id
        self.__class__.free_b_id += 1


class Body:
    def __init__(self, x, y, w, h):
        self._x, self._y, self.w, self.h = x, y, w, h
        self._cached_rect = pyv.new_rect_obj(self.x, self.y, self.w, self.h)

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, val):
        self._y = val
        self._cached_rect = pyv.new_rect_obj(self._x, self._y, self.w, self.h)

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, val):
        self._x = val
        self._cached_rect = pyv.new_rect_obj(self._x, self._y, self.w, self.h)

    def to_rect(self):
        return self._cached_rect

    def commit(self):
        # use the cached rect (has been modified) to update other values
        self._x, self.y = self._cached_rect.topleft


# tooling to create entities
# -------------------------------------
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
            glvars.blocks.add(ecs.create_entity(
                Body(*precursor_rect),
                BlockSig()  # to tag entity as being a block
            ))
            bcx += glvars.BLOCK_W + glvars.BLOCK_SPACING
        bcy += glvars.BLOCK_H + glvars.BLOCK_SPACING


def wipe_ingame_state():
    # mark all entities for deletion
    ecs.delete_entity(glvars.ball_entity)
    ecs.delete_entity(glvars.player_entity)
    glvars.ball_entity = glvars.player_entity = None
    for e in glvars.blocks:
        ecs.delete_entity(e)
    glvars.blocks.clear()
    glvars.end_game_label = None


def build_ingame_entities():
    # marks the fact the game hasnt started yet
    glvars.start_game_label = glvars.font.render('Press space to start the game', True, 'white')
    # entities creation per se
    player_create()
    ball_create()
    blocks_create()
