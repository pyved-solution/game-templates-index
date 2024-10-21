import random
import pygame
import glvars
import pyved as pyv


WIDTH_WORLD = 640
HEIGHT_WORLD = 480


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
        "count": BRICK_ROWS * BRICK_COLS
    }
    for col in range(BRICK_COLS):
        for row in range(BRICK_ROWS):
            data['content'].append(
                (WIDTH_WORLD // 2 + col * BRICK_WIDTH + 10, 80 + row * BRICK_HEIGHT, BRICK_WIDTH, BRICK_HEIGHT)
            )

    def destroy_brick(this, ref_brick):
        this.content.remove(ref_brick)
        this.count -= 1
        print(f'remaining bricks: {this.count}')
        pyv.post_ev('x_sync_wall', content=this.content, count=this.count)

    return pyv.new_actor(locals())


PADDLE_WIDTH = 10
PADDLE_HEIGHT = 100


def new_paddle(info_side):
    actor_type, data = 'paddle', {
        "pos": None,
        "side": info_side,  # either left or right
        "offset": 10  # px
    }
    if info_side == 'left':
        data['pos'] = [40, HEIGHT_WORLD // 2 - PADDLE_HEIGHT // 2]
    else:
        data['pos'] = [WIDTH_WORLD - 50, HEIGHT_WORLD // 2 - PADDLE_HEIGHT // 2]

    def on_x_move_paddle(this, ev):
        if ev.player == this.side:
            if ev.dir == "up":
                this.pos[1] = max(this.pos[1] - this.offset, 0)
            elif ev.dir == "down":
                this.pos[1] = min(this.pos[1] + this.offset, HEIGHT_WORLD - PADDLE_HEIGHT)
            pyv.post_ev('x_new_paddle_pos', player=this.side, pos=this.pos)  # broadcast new infos

    return pyv.new_actor(locals())


BALL_RADIUS = 12


def new_component_physics(x, y, vx, vy):
    return {
        "pos": [x, y],
        "velocity": [vx, vy]
    }


def new_ball():
    actor_type, data = 'ball', {
        # a demo of how components can be used
        **new_component_physics(random.randint(-88, 100)+(WIDTH_WORLD // 2), HEIGHT_WORLD // 2, 3, 3)
    }

    def on_update(this, ev):
        if glvars.match_started:
            this.pos[0] += this.velocity[0]
            this.pos[1] += this.velocity[1]

            # Bounce off top and bottom walls
            if this.pos[1] <= 0 or this.pos[1] >= HEIGHT_WORLD - BALL_RADIUS:
                this.velocity[1] = -this.velocity[1]

            # Check for paddle collisions
            left_paddle_data = pyv.actor_state(glvars.left_paddle)
            if left_paddle_data:  # as it can dispappaer during game
                if left_paddle_data.pos[1] <= this.pos[1] <= left_paddle_data.pos[1] + PADDLE_HEIGHT:
                    if this.pos[0] <= 50 + BALL_RADIUS:
                        this.velocity[0] = -this.velocity[0]
            right_paddle_data = pyv.actor_state(glvars.right_paddle)
            if right_paddle_data.pos[1] <= this.pos[1] <= right_paddle_data.pos[1] + PADDLE_HEIGHT:
                if this.pos[0] >= WIDTH_WORLD - 50 - BALL_RADIUS:
                    this.velocity[0] = -this.velocity[0]
            pyv.post_ev('x_new_ball_position', pos=this.pos)

            # Check for brick collisions
            bricks_data = pyv.actor_state(glvars.bricks)
            li_bricks = bricks_data.content
            for brick in li_bricks[:]:
                brect = pygame.Rect(*brick)
                if brect.collidepoint(this.pos):
                    pyv.actor_exec(glvars.bricks, 'destroy_brick', brick)
                    this.velocity[0] = -this.velocity[0]

    return pyv.new_actor(locals())
