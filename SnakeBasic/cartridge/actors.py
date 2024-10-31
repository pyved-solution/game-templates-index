from random import randint

from . import glvars
from .glvars import pyv


__all__ = [
    'new_apple', 'new_snake', 'new_background'
]


def new_background():
    data = {
        'color': pyv.pal.punk.nightblue
    }

    def on_draw(this, ev):
        ev.screen.fill(this.color)

    return pyv.new_actor('background', locals())


# >>> apple
apple_id = None


def new_apple():
    candidate_pos = None
    while candidate_pos is None or candidate_pos in pyv.actor_state(snake_id).content:
        candidate_pos = (
            randint(0, glvars.NB_COLUMNS - 1),
            randint(0, glvars.NB_ROWS - 1)
        )
    data = {
        'x': candidate_pos[0], 'y': candidate_pos[1]
    }

    # - behavior
    def on_draw(this, ev):
        if glvars.gameover_msg is None:
            csize = glvars.CELL_SIZE_PX
            apple_infos = pyv.actor_state(apple_id)
            pyv.draw_rect(
                ev.screen, pyv.pal.japan.red,
                pyv.new_rect_obj(apple_infos.x * csize, apple_infos.y * csize, csize, csize)
            )

    return pyv.new_actor('apple', locals())


# >>> snake
snake_id = None


def new_snake():
    data = {
        'content': list(glvars.INIT_SNAKE_MODEL),
        'direction': glvars.INIT_DIRECTION
    }

    # utilitary
    def reset(this):
        this.content = list(glvars.INIT_SNAKE_MODEL)
        this.direction = glvars.INIT_DIRECTION

    def collision_check(this):
        s_body = this.content
        head = s_body[-1]
        for i in range(len(s_body) - 1):
            if head == s_body[i]:
                return 2
        if head[0] >= glvars.NB_COLUMNS or head[0] < 0:
            return 3
        if head[1] >= glvars.NB_ROWS or head[1] < 0:
            return 3
        apple = pyv.actor_state(apple_id)
        if head == (apple.x, apple.y):
            return 1
        return 0

    # - behavior
    def on_draw(this, ev):
        if glvars.gameover_msg is None:
            s_body = this.content
            csize = glvars.CELL_SIZE_PX
            for i in range(len(s_body)):
                pyv.draw_rect(
                    ev.screen, pyv.pal.japan.peach,
                    pyv.new_rect_obj(s_body[i][0] * csize, s_body[i][1] * csize, csize, csize)
                )

    def on_world_tick(this, ev):
        global apple_id
        dx, dy = {
            0: (1, 0),
            1: (0, 1),
            2: (-1, 0),
            3: (0, -1)
        }[this.direction]
        s_body = this.content
        s_body.append((s_body[-1][0] + dx, s_body[-1][1] + dy))
        coll = collision_check(this)
        if coll >= 2:
            glvars.game_running = 2
        elif coll == 1:
            pyv.del_actor(apple_id)
            apple_id = new_apple()
        elif coll == 0:
            s_body.pop(0)

    return pyv.new_actor('snake', locals())
