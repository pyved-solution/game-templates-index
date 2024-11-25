from .glvars import pyv
from . import glvars
from . import scenes

pyv.bootstrap_e()


def init(gms):
    global hint_msg

    pyv.init(wcaption=glvars.WINDOW_LABEL)
    pyv.declare_evs(
        'move_avatar', 'player_action'
    )
    glvars.scene_dim[0], glvars.scene_dim[1] = pyv.vars.screen.get_size()

    # prepare scene #1
    # the first scene is always named 'default',
    # this is a standard in pyved-engine, but for several reasons
    # (future API changes?)
    # it is recommended to use the scene identifier, not its "str" code directly.
    # "str" Code : 'default'
    # scene identifier : pyv.DEFAULT_SCENE
    # so, 'default' == pyv.DEFAULT_SCENE is true in the current version
    scenes.default.setup(*glvars.scene_dim)

    # init all scenes...
    pyv.set_scene(glvars.JUNG_SCENE_ID)  # you can name extra scenes, with the name you want
    scenes.jungle.setup()
    pyv.set_scene(glvars.SPACE_SCENE_ID)
    scenes.space.setup()

    # and now,
    # we have to go back to the default scene #1, because this is where the game begins
    pyv.set_scene(pyv.DEFAULT_SCENE)
    print('-' * 32)
    print(glvars.TUTO_TEXT)


def update(tnow=None):  # will be called BEFORE event dispatching...
    # ------------
    # Event handling + check keyboard inputs
    # ------------
    for ev in pyv.evsys0.get():
        if ev.type == pyv.evsys0.QUIT:
            pyv.vars.gameover = True
        elif ev.type == pyv.evsys0.KEYDOWN:
            if ev.key == pyv.evsys0.K_ESCAPE:
                pyv.vars.gameover = True
            elif ev.key == pyv.evsys0.K_RETURN:
                if pyv.get_scene() == pyv.DEFAULT_SCENE:
                    my_msg = 'In the next scene press Enter twice to enter a special world'
                    pyv.trigger('say_something', scenes.default.ref_npc, my_msg)
                else:
                    pyv.post_ev('player_action')
            elif ev.key == pyv.evsys0.K_SPACE:
                if pyv.get_scene() == pyv.DEFAULT_SCENE:
                    my_msg = 'Hello, scenes are:' + str(pyv.ls_scenes())
                    pyv.trigger('say_something', scenes.default.ref_npc, my_msg)

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

    # - refresh gfx and process all events...
    pyv.post_ev('draw', screen=pyv.vars.screen)
    pyv.process_evq()

    pyv.flip()


def close(gms):
    pyv.close_game()
    print('bye!')
