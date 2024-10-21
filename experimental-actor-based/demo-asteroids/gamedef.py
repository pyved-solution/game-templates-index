"""
TECH-DEMO 1
First revision: year 2021, 10-02
Current revision: year 2024, 10-19

My goal is to showcase how the custom py-based engine operates in a straightforward manner
"""
from shared import pyv, pygame, random
from actors import *


def print_mini_tutorial():
    guide = """HOW TO PLAY?
     * use arrows to steer your ship
     * use SPACE to use a wormhole!
    """
    print('-' * 32)
    for line in guide.split('\n'):
        print(line)
    print('-' * 32)


def game_init():
    print_mini_tutorial()
    pyv.init((960 // 2, 720 // 2))
    scr_w, scr_h = pyv.screen.get_size()
    random_spawn_loc = random.randint(0, scr_w - 1), random.randint(0, scr_h - 1)
    new_ship(random_spawn_loc)
    new_rockfield(7)


def game_update(dt):  # will be called BEFORE event dispatching...
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            pyv.playing = False
        elif ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_SPACE:
                pyv.post_ev("dash")
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        pyv.post_ev("ship_rotate", dir="counter-clockwise")
    if keys[pygame.K_RIGHT]:
        pyv.post_ev("ship_rotate", dir="clockwise")
    if keys[pygame.K_UP]:
        pyv.post_ev("thrust")
    if keys[pygame.K_DOWN]:
        pyv.post_ev("brake")
    # clear screen
    pyv.screen.fill('gray5')


def game_exit():
    print('asteroids demo, over')


if __name__ == '__main__':
    pyv.game_loop(locals())
