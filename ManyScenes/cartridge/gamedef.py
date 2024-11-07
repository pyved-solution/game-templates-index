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
    glvars.scene_dim[0], glvars.scene_dim[1] = pyv.vars.screen.get_size()
    mapW, mapH = glvars.scene_dim

    # prepare scene #1
    # the first scene is always named 'default',
    # this is a standard in pyved-engine, but for several reasons
    # (future API changes?) it is recommended to use the scene
    # identifier, not its "str" code directly.
    # "str" Code : 'default'
    # scene identifier : pyv.DEFAULT_SCENE
    # so, 'default' == pyv.DEFAULT_SCENE is true in the current version
    actors.new_avatar(mapW // 2, mapH // 2)
    actors.ref_npc = actors.new_npc()
    hint_msg = pyv.new_font_obj(None, FT_SIZE).render(HINT_TEXT, False, 'yellow')

    # go to scene #2 and prepare the scene #2
    pyv.set_scene(glvars.JUNG_SCENE_ID)  # you can name extra scenes, with the name you want
    glvars.av_jungle = actors.new_avatar(50, mapH // 2)
    print('A new avatar actor initiated (->in jungle)', glvars.av_jungle)

    # we have to go back to the default scene #1,
    # because this is where the game starts
    pyv.set_scene(pyv.DEFAULT_SCENE)

    print('-'*32)
    print('CONTROLS are:\n Arrow keys | SPACE in the 1st scene | ENTER in the 2nd scene')

def update(tnow=None):  # will be called BEFORE event dispatching...
    # Event handling, and check keyboard inputs
    for ev in pyv.evsys0.get():
        if ev.type == pyv.evsys0.QUIT:
            pyv.vars.gameover = True
        elif ev.type == pyv.evsys0.KEYDOWN:
            if ev.key == pyv.evsys0.K_ESCAPE:
                pyv.vars.gameover = True
            elif ev.key == pyv.evsys0.K_RETURN:
                if pyv.get_scene() == glvars.JUNG_SCENE_ID:
                    pyv.trigger('reset_pos', glvars.av_jungle)  # move the avatar to a cool location
            elif ev.key == pyv.evsys0.K_SPACE:
                if pyv.get_scene() != glvars.JUNG_SCENE_ID:
                    pyv.trigger('say_something', actors.ref_npc, 'Hello, scenes are:'+str(pyv.ls_scenes()) )
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
    if pyv.get_scene() == pyv.DEFAULT_SCENE:
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
