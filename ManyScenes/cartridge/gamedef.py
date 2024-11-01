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

    pyv.init(wcaption="Test with avatar and rooms")
    glvars.world_dim[0], glvars.world_dim[1] = pyv.vars.screen.get_size()
    mapW, mapH = glvars.world_dim

    # prepare world #2
    pyv.switch_world(glvars.JUNG_WORLD_ID)
    avatar_jungle = actors.new_avatar(50, mapH//2)
    pyv.actor_exec(avatar_jungle, 'reset_pos')  # move the avatar to a cool location
    print('a new av has been initiated (in jungle):', avatar_jungle)

    # go back to the default world
    pyv.switch_world('default')
    actors.new_avatar(mapW//2, mapH//2)
    actors.ref_npc = actors.new_npc()
    hint_msg = pyv.new_font_obj(None, FT_SIZE).render(HINT_TEXT, False, 'yellow')


def update(tnow=None):  # will be called BEFORE event dispatching...
    # Event handling, and check keyboard inputs
    for ev in pyv.evsys0.get():
        if ev.type == pyv.evsys0.QUIT:
            pyv.vars.gameover = True
        elif ev.type == pyv.evsys0.KEYDOWN:
            if ev.key == pyv.evsys0.K_ESCAPE:
                pyv.vars.gameover = True
            elif ev.key == pyv.evsys0.K_SPACE:
                if pyv.get_curr_world() != glvars.JUNG_WORLD_ID:
                    pyv.actor_exec(actors.ref_npc, 'say_something', 'Hello world!')
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
    scr=pyv.vars.screen
    if pyv.get_curr_world() == 'default':
        scr.fill('darkred')
        scr.blit(hint_msg, (256, 32))
    else:
        scr.fill('gray6')
    pyv.post_ev('draw', screen=scr)
    pyv.process_events()

    pyv.flip()


def close(gms):
    pyv.close_game()
    print('bye!')


# launch the game
if __name__ == '__main__':
    pyv.game_loop(locals())
