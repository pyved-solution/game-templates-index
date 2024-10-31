from .glvars import pyv
pyv.bootstrap_e()

from . import dialogue
from . import glvars
from .classes2 import Automaton


# - gl variables
EngineEvTypes = pyv.EngineEvTypes
conv_viewer = None
# - new gl vars
# global variables
evm = None
msg = None


# ----------------------
# Define controllers etc
# --------------------------------------------
class BasicCtrl(pyv.EvListener):

    def on_quit(self, ev):
        pyv.vars.gameover = True

    # def proc_event(self, gdi):
    #     global conversation_ongoing, map_viewer, mypc, current_tilemap, current_path
    #     if gdi.type == pygame.KEYDOWN:
    #         if gdi.key == pygame.K_ESCAPE:
    #             if conversation_ongoing:
    #                 # abort
    #                 self.pev(MyEvTypes.ConvEnds)
    #             else:
    #                 self.pev(EngineEvTypes.GAMEENDS)
    #         elif gdi.key == pygame.K_d and mypc.x < tilemap_width - 1.5:
    #             mypc.x += 0.1
    #         elif gdi.key == pygame.K_a and mypc.x > -1:
    #             mypc.x -= 0.1
    #         elif gdi.key == pygame.K_w and mypc.y > -1:
    #             mypc.y -= 0.1
    #         elif gdi.key == pygame.K_s and mypc.y < tilemap_height - 1.5:
    #             mypc.y += 0.1
    #         elif gdi.key == pygame.K_TAB:
    #             current_tilemap = 1 - current_tilemap
    #             map_viewer.switch_map(maps[current_tilemap])


class PathCtrl(pyv.EvListener):
    def __init__(self):
        super().__init__()

    def start_conv(self):
        global conv_viewer
        glvars.conversation_ongoing = True

        # TODO faire en sorte que l'automate prenne l'interface de dialogue.Offer
        # ou inversement, que la ConversationView puisse s'adapter à une interface type AUtomaton

        # myconvo = dialogue.Offer.from_json(pyv.vars.data['legacy_conv'])  # using data pre-loaded thu pyv
        automaton = Automaton(pyv.vars.data)
        automaton.load_from_json(pyv.vars.data['encounter_1'])
        print(automaton)

        conv_viewer = dialogue.ConversationView(
            automaton
        )
        conv_viewer.turn_on()

    def on_conv_finish(self, ev):
        glvars.conversation_ongoing = False  # unlock player movements
        if conv_viewer.active:
            conv_viewer.turn_off()


def init(vmst=None):
    global evm, msg
    pyv.init(1) #pyv.LOW_RES_MODE, wcaption='IsometricRPG Tech Demo')
    evm = pyv.get_ev_manager()
    evm.setup()

    pctrl = PathCtrl()
    pctrl.turn_on()
    bctrl = BasicCtrl()
    bctrl.turn_on()
    
    # start conv
    pctrl.start_conv()
    msg = pyv.new_font_obj(None, 33).render('encounter ended', False, 'orange')

    #gctrl = pyv.get_game_ctrl()
    #gctrl.turn_on()


def update(time_info=None):
    # for ev in pygame.event.get():
    #     if ev.type == pygame.QUIT:
    #         pyv.vars.gameover = True
    #     elif ev.type == pygame.KEYDOWN:
    #         kpressed.add(ev.key)
    #     elif ev.type == pygame.KEYUP:
    #         kpressed.remove(ev.key)

    # - logic
    evm.post(EngineEvTypes.Update, info_t=time_info)

    # do not draw directly, use events!
    # scr = pyv.vars.screen

    # scr.fill('paleturquoise3')
    # if len(kpressed):
    #     pyv.draw_rect(scr, 'orange', (15, 64, 100, 100))
    pyv.vars.screen.fill(pyv.pal.punk.nightblue)
    evm.post(EngineEvTypes.Paint, screen=pyv.vars.screen)
    evm.update()  # auto convert pygame events to high-level events

    if not glvars.conversation_ongoing:
        pyv.vars.screen.blit(msg, (256, 320))
    pyv.flip()


def close(vmst=None):
    pyv.close_game()
    print('gameover!')
