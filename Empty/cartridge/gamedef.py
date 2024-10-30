from .glvars import pyv


pyv.bootstrap_e()
pyg = pyv.pygame
screen = None
r4 = pyg.Rect(32, 32, 128, 128)
kpressed = set()


def init(vmst=None):
    global screen
    pyv.init(wcaption='Untitled pyved-based Game')
    screen = pyv.get_surface()


def update(time_info=None):
    for ev in pyg.event.get():
        if ev.type == pyg.QUIT:
            pyv.vars.gameover = True
        elif ev.type == pyg.KEYDOWN:
            kpressed.add(ev.key)
        elif ev.type == pyg.KEYUP:
            kpressed.remove(ev.key)

    screen.fill('paleturquoise3')
    if len(kpressed):
        # pyv.draw_rect(screen, 'orange', r4)
        screen.blit(pyv.vars.images['lion'], (r4[0],r4[1]))
    pyv.flip()


def close(vmst=None):
    pyv.close_game()
    print('gameover!')
