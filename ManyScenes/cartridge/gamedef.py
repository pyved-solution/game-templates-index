from .glvars import pyv
from . import glvars
from . import actors

pyv.bootstrap_e()

# const
# BLUE = (0, 0, 255)
# RED = (255, 0, 0)
# GREEN = (0, 255, 0)
# BLACK = (0, 0, 0)

HINT_TEXT = 'Use arrow keys | Go right...'
FT_SIZE = 60

# gl variables
hint_msg = None


def init(gms):
    global hint_msg

    pyv.init(wcaption="Test:One avatar, two rooms")
    pyv.declare_evs(
        'move_avatar'
    )
    glvars.world_dim[0], glvars.world_dim[1] = pyv.vars.screen.get_size()
    mapW, mapH = glvars.world_dim

    # prepare world #2
    pyv.set_world(glvars.JUNG_WORLD_ID)
    glvars.av_jungle = actors.new_avatar(50, mapH // 2)
    print('A new avatar actor initiated (->in jungle)', glvars.av_jungle)

    # go back to the default world
    pyv.set_world('default')
    actors.new_avatar(mapW // 2, mapH // 2)
    actors.ref_npc = actors.new_npc()
    hint_msg = pyv.new_font_obj(None, FT_SIZE).render(HINT_TEXT, False, 'yellow')

    print('-'*32)
    print('CONTROLS are:\n Arrow keys | SPACE in the 1st world | ENTER in the 2nd world')

def update(tnow=None):  # will be called BEFORE event dispatching...
    # Event handling, and check keyboard inputs
    for ev in pyv.evsys0.get():
        if ev.type == pyv.evsys0.QUIT:
            pyv.vars.gameover = True
        elif ev.type == pyv.evsys0.KEYDOWN:
            if ev.key == pyv.evsys0.K_ESCAPE:
                pyv.vars.gameover = True
            elif ev.key == pyv.evsys0.K_RETURN:
                if pyv.get_world() == glvars.JUNG_WORLD_ID:
                    pyv.trigger('reset_pos', glvars.av_jungle)  # move the avatar to a cool location
            elif ev.key == pyv.evsys0.K_SPACE:
                if pyv.get_world() != glvars.JUNG_WORLD_ID:
                    pyv.trigger('say_something', actors.ref_npc, 'Hello world!')
    keys = pyv.evsys0.pressed_keys()
    if keys[pyv.evsys0.K_LEFT]:
        pyv.post_ev("move_avatar", dir="left")
    if keys[pyv.evsys0.K_RIGHT]:
        pyv.post_ev("move_avatar", dir="right")
    if keys[pyv.evsys0.K_UP]:
        pyv.post_ev("move_avatar", dir="up")
    if keys[pyv.evsys0.K_DOWN]:
        pyv.post_ev("move_avatar", dir="down")

    # - logic
    pyv.post_ev('update', info_t=tnow)

    # - refrsh gfx
    scr = pyv.vars.screen
    if pyv.get_world() == 'default':
        scr.fill(glvars.BG_COL)
        scr.blit(hint_msg, (256, 32))
    else:
        scr.fill('gray6')
    pyv.post_ev('draw', screen=scr)
    pyv.process_evq()

    pyv.flip()


def close(gms):
    pyv.close_game()
    print('bye!')
