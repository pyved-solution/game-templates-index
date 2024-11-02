from .glvars import pyv


pyv.bootstrap_e()
pyg = pyv.pygame
r4 = pyg.Rect(128, 256, 200, 200)
kpressed = set()


def init(vmst=None):
    pyv.init(wcaption='Untitled, empty, and pyved-based demo')
    print('-'*32)
    print('press one or two key (any key) to see something cool')


def update(time_info=None):
    for ev in pyg.event.get():
        if ev.type == pyg.QUIT:
            pyv.vars.gameover = True
        elif ev.type == pyg.KEYDOWN:
            kpressed.add(ev.key)
        elif ev.type == pyg.KEYUP:
            kpressed.remove(ev.key)

    # logic?
    pass
    
    # refresh screen
    scr = pyv.get_surface()
    scr.fill('paleturquoise3')
    if len(kpressed)==1:
        scr.blit(
            pyv.vars.images['lion'], (r4[0]-100, r4[1]-200)
        )
    elif len(kpressed)==2:
        pyv.draw_rect(scr, 'orange', r4)
    pyv.flip()


def close(vmst=None):
    pyv.close_game()
    print('gameover!')
