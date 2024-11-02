from .actors import new_game_controller
from .glvars import pyv


pyv.bootstrap_e()
EngineEvTypes = pyv.EngineEvTypes
amt_viewer_id = None


def init(vmst=None):
    global amt_viewer_id
    pyv.init(pyv.LOW_RES_MODE)
    new_game_controller()
    amt_viewer_id = pyv.story.new_automaton_viewer(
        'encounter_1', 'encounter_Y'
    )
    # insta-begin the conversation!
    pyv.post_ev('conv_begins')


def update(time_info=None):
    # bind old ev system to evsys6
    for ev in pyv.evsys0.get():
        if ev.type == pyv.evsys0.QUIT:
            pyv.vars.gameover = True
        elif ev.type == pyv.evsys0.KEYDOWN:
            if ev.key == pyv.evsys0.K_ESCAPE:
                pyv.vars.gameover = True
            # elif ev.key == pyv.evsys0.K_RETURN:
            #    pyv.post_ev('conv_begins')
        elif ev.type == pyv.evsys0.MOUSEMOTION:
            pyv.post_ev('mousemotion', pos=ev.pos, rel=ev.rel)
        elif ev.type == pyv.evsys0.MOUSEBUTTONDOWN:
            pyv.post_ev('mousedown', pos=ev.pos, button=ev.button)
        elif ev.type == pyv.evsys0.MOUSEBUTTONUP:
            pyv.post_ev('mouseup', pos=ev.pos, button=ev.button)

    # -evsys6
    pyv.post_ev('update', info_t=time_info)
    pyv.post_ev('draw', screen=pyv.vars.screen)
    pyv.process_evq()
    pyv.flip()


def close(vmst=None):
    pyv.del_actor(amt_viewer_id)
    pyv.close_game()
    print('visual novel:over')
