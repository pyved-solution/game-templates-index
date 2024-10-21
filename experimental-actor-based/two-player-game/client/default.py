from shared import BLUE, GREEN
from shared import pyv, pygame


__all__ = [
    'new_bricks',
    'new_paddle',
    'new_ball'
]


BRICK_ROWS = 5
BRICK_COLS = 4
BRICK_WIDTH = 20
BRICK_HEIGHT = 48


def new_bricks():
    # declare data
    actor_type, data = 'bricks', {
        "content": [],
        "count": 0
    }

    def on_draw(this, ev):
        for brick in this.content:
            pygame.draw.rect(pyv.screen, BLUE, brick)

    # callback functions
    def on_x_sync_wall(this, ev):
        this.content = ev.content
        this.count = ev.count

    return pyv.new_actor(locals())


PADDLE_WIDTH = 10
PADDLE_HEIGHT = 100


def new_paddle(info_side):
    actor_type, data = 'paddle', {
        "pos": [0, 0],
        "side": info_side  # left or right
    }

    def on_draw(this, ev):
        pygame.draw.rect(pyv.screen, BLUE if this.side == 'left' else GREEN, (*this.pos, PADDLE_WIDTH, PADDLE_HEIGHT))

    def on_x_new_paddle_pos(this, ev):
        if ev.player == this.side:
            this.pos[0], this.pos[1] = ev.pos

    return pyv.new_actor(locals())


BALL_RADIUS = 12


def new_physics_component(x, y, vx, vy):
    return {
        "pos": [x, y],
        "velocity": [vx, vy]
    }


def new_ball():
    actor_type, data = 'ball', {
        # a demo of how components can be used (2/2)
        **new_physics_component(0, 0, 3, 3),
        "color": "orange"
    }

    def on_draw(this, ev):
        pygame.draw.circle(pyv.screen, this.color, this.pos, BALL_RADIUS)

    def on_x_new_ball_position(this, ev):
        this.pos[0], this.pos[1] = ev.pos

    return pyv.new_actor(locals())
