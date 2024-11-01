from . import glvars
from .glvars import pyv


pyv.bootstrap_e()
EngineEvTypes = pyv.EngineEvTypes
conv_viewer = None
msg = None


class BasicCtrl(pyv.EvListener):
    def on_quit(self, ev):
        pyv.vars.gameover = True

    def on_keydown(self, ev):
        if ev.key == pyv.evsys0.K_ESCAPE:
            pyv.vars.gameover = True


class PathCtrl(pyv.EvListener):
    def __init__(self): super().__init__()

    def start_conv(self):
        global conv_viewer
        from .story import Automaton
        from .story import ConversationView
        glvars.conversation_ongoing = True
        conv_viewer = ConversationView(
            Automaton(('encounter_1', pyv.vars.data['encounter_1']),
                      ('encounter_Y', pyv.vars.data['encounter_Y'])))
        conv_viewer.turn_on()

    def on_conv_finish(self, ev):
        glvars.conversation_ongoing = False
        if conv_viewer.active:
            conv_viewer.turn_off()


def init(vmst=None):
    global msg
    pyv.init(pyv.LOW_RES_MODE)
    pyv.get_ev_manager().setup()
    pctrl = PathCtrl()
    pctrl.turn_on()
    bctrl = BasicCtrl()
    bctrl.turn_on()
    pctrl.start_conv()
    msg = pyv.new_font_obj(None, 33).render('encounter ended', False, 'orange')


def update(time_info=None):
    evm = pyv.get_ev_manager()
    evm.post(EngineEvTypes.Update, info_t=time_info)
    pyv.vars.screen.fill(pyv.pal.punk.nightblue)
    evm.post(EngineEvTypes.Paint, screen=pyv.vars.screen)
    evm.update()  # note that this auto-converts pygame events to higher-level events
    if not glvars.conversation_ongoing:
        pyv.vars.screen.blit(msg, (256, 320))
    pyv.flip()


def close(vmst=None):
    pyv.close_game()
    print('visual novel:over')
