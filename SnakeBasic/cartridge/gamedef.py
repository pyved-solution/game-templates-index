""" ~220 lignes de code pour coder le snake
Les 11 appels à connaitre: pyv.*
- init
- post_ev
- process_events
- new_font_obj
- new_rect_obj
- flip
- close

- new_actor
- del_actor
- actor_state
- actor_exec
"""
from . import actors
from . import glvars
from .actors import *

pyv = glvars.pyv
pyv.bootstrap_e()
DIRECTIONS = {  # helps for event management
    pyv.evsys0.K_RIGHT: 'right',  # 0,  # evsys0? -> one event system that comes with pyved-engine
    pyv.evsys0.K_DOWN: 'down',  # 1,
    pyv.evsys0.K_LEFT: 'left',  # 2,
    pyv.evsys0.K_UP: 'up'  # 3
}
# helps for adjusting game speed (world_tick events)
last_t = None
hourglass_like_var = 0.0


def do_reset_game():
    glvars.game_running = 0
    glvars.gameover_msg = None
    pyv.trigger('reset', actors.snake_id)
    pyv.del_actor(actors.apple_id)
    actors.apple_id = new_apple()


def init(vmst=None):
    alpha = glvars.CELL_SIZE_PX
    pyv.init(
        0, forced_size=(alpha * glvars.NB_COLUMNS, alpha * glvars.NB_ROWS),
        wcaption='Snake basic', maxfps=35)
    pyv.declare_evs(
        'world_tick',
        'player_moves'
    )
    glvars.font_obj = pyv.new_font_obj(None, 48)
    new_background()
    actors.snake_id = new_snake()
    actors.apple_id = new_apple()


def update(time_info=None):
    global last_t, hourglass_like_var
    # <> EVENTS
    for ev in pyv.evsys0.get():
        if ev.type == pyv.evsys0.QUIT:
            pyv.vars.gameover = True
        elif ev.type == pyv.evsys0.KEYDOWN:
            if ev.key == pyv.evsys0.K_ESCAPE:
                pyv.vars.gameover = True
            elif ev.key == pyv.evsys0.K_SPACE:
                do_reset_game()
            else:
                glvars.game_running = 1
    kpressed = pyv.evsys0.pressed_keys()
    for arrow in DIRECTIONS:
        if kpressed[arrow]:
            pyv.post_ev('player_moves', dir=DIRECTIONS[arrow])

    # <> LOGIC
    if glvars.game_running == 2:
        if glvars.gameover_msg is None:
            glvars.gameover_msg = glvars.font_obj.render(glvars.END_MSG, False, 'blue')
    elif glvars.game_running == 1:
        if last_t is None:
            last_t = time_info
            return
        hourglass_like_var += (time_info - last_t)
        last_t = time_info
        if hourglass_like_var > glvars.DELAY_INTER_MV:
            hourglass_like_var = 0.0
            pyv.post_ev("world_tick")
    pyv.process_evq()

    # <> GFX
    pyv.post_ev('draw', screen=pyv.vars.screen)
    pyv.process_evq()
    if glvars.gameover_msg is not None:
        pyv.vars.screen.blit(glvars.gameover_msg, (3 * glvars.CELL_SIZE_PX, 3 * glvars.CELL_SIZE_PX))
    pyv.flip()


def close(vmst=None):
    pyv.close_game()
    print('snake basic:over')
