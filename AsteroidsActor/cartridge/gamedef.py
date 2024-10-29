"""
TECH-DEMO 1
First revision: year 2021, 10-02
Current revision: year 2024, 10-19

My goal is to showcase how the custom py-based engine operates in a straightforward manner
"""
import random
from .glvars import pyv


pyv.bootstrap_e()
last_t = None


def print_mini_tutorial():
    guide = """HOW TO PLAY?
     * use arrows to steer your ship
     * use SPACE to use a wormhole!
    """
    print('-' * 32)
    for line in guide.split('\n'):
        print(line)
    print('-' * 32)


@pyv.declare_begin
def game_init(gms):
    pyv.init(pyv.LOW_RES_MODE)  # 0, forced_size=(960 // 2, 720 // 2), maxfps=60)

    from .actors import new_rockfield, new_ship
    new_rockfield(7)
    scr_w, scr_h = pyv.vars.screen.get_size()
    random_spawn_loc = random.randint(0, scr_w - 1), random.randint(0, scr_h - 1)
    new_ship(random_spawn_loc)

    print_mini_tutorial()


@pyv.declare_update
def game_update(info_t):
    global last_t

    # - ev management
    pyg = pyv.pygame
    for ev in pyg.event.get():
        if ev.type == pyg.QUIT:
            pyv.vars.gameover = True
        elif ev.type == pyg.KEYDOWN:
            if ev.key == pyg.K_SPACE:
                pyv.post_ev("dash")
            elif ev.key == pyg.K_ESCAPE:
                pyv.vars.gameover = True
    keys = pyg.key.get_pressed()
    if keys[pyg.K_LEFT]:
        pyv.post_ev("ship_rotate", dir="counter-clockwise")
    elif keys[pyg.K_RIGHT]:
        pyv.post_ev("ship_rotate", dir="clockwise")
    if keys[pyg.K_UP]:
        pyv.post_ev("thrust")
    elif keys[pyg.K_DOWN]:
        pyv.post_ev("brake")

    # using ev sys 6
    if last_t:
        dt = info_t - last_t
    else:
        dt = 0
    last_t = info_t
    pyv.post_ev("update", dt=dt)
    pyv.process_events()

    # refresh screen then logic
    pyv.vars.screen.fill(pyv.pal.punk.nightblue)
    pyv.post_ev("draw", screen=pyv.vars.screen)
    pyv.process_events()
    pyv.flip()


@pyv.declare_end
def game_exit(gms):
    pyv.close_game()
    print('asteroids demo ->over')
