"""
this game isnt fun.

It exists solely for the purpose of testing the
 Challenge System/Challenge service...

provided by the Kata.Games distribution platform and related tools
"""
from . import pimodules

# if you dont boostrap FIRST, then class Button will crash
pyv = pimodules.pyved_engine
pyv.bootstrap_e()

from . import chdefs
from . import glvars
from .state_intro import ChessintroState
from .state_compete import CompeteState


pyg = pyv.pygame


@pyv.Singleton
class SharedStorage:
    def __init__(self):
        self.ev_manager = pyv.get_ev_manager()
        self.ev_manager.setup(chdefs.ChessEvents)
        self.screen = pyv.get_surface()


@pyv.declare_begin
def beginchess(vmst=None):
    pyv.init()
    glvars.ev_manager = pyv.get_ev_manager()

    estoragevars = SharedStorage.instance()

    # sq_size_pixels = (100, 100)
    # for iname, sv in pyv.vars.images.items():
    #     if iname[-6:] == 'square':
    #         pass
    #     else:
    #         pyv.vars.images[iname] = pyg.transform.scale(sv, sq_size_pixels)

    pyv.declare_game_states(
        glvars.MyGameStates, {
            # do this to bind state_id to the ad-hoc class!
            glvars.MyGameStates.TitleScreen: ChessintroState,
            glvars.MyGameStates.CompeteNow: CompeteState
        }
    )
    glvars.ev_manager.post(pyv.EngineEvTypes.Gamestart)


@pyv.declare_update
def updatechess(info_t):
    glvars = SharedStorage.instance()

    glvars.ev_manager.post(pyv.EngineEvTypes.Update, curr_t=info_t)
    glvars.ev_manager.post(pyv.EngineEvTypes.Paint, screen=glvars.screen)

    glvars.ev_manager.update()
    pyv.flip()


@pyv.declare_end
def endchess(vmst=None):
    pyv.close_game()
