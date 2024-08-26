from . import pimodules

pyv = pimodules.pyved_engine
pyv.bootstrap_e()

from .shared import MyEvTypes
from . import glvars


THECOLORS = pyv.pygame.color.THECOLORS
netw = pimodules.network

# pyv = pimodules.pyved_engine
pygame = pyv.pygame
my_mod = None
gscreen = None
replayed = False


@pyv.declare_begin
def initfunc(vmst=None):
    global my_mod, gscreen
    pyv.init()
    glvars.screen = pyv.get_surface()
    glvars.ev_manager = pyv.get_ev_manager()
    glvars.ev_manager.setup(MyEvTypes)

    from .casino_state import CasinoState
    from .intro_state import ChessintroState

    pyv.declare_game_states(
        glvars.MyGameStates, {
            # do this to bind state_id to the ad-hoc class!
            glvars.MyGameStates.IntroState: ChessintroState,
            glvars.MyGameStates.CasinoState: CasinoState
        }
    )
    glvars.ev_manager.post(pyv.EngineEvTypes.Gamestart)
    print()
    print('-max fps is now:-')
    pyv.vars.maxfps = 0  # hack: replace the default value, to maximize speed execution
    print(pyv.vars.maxfps)


@pyv.declare_update
def updatefunc(info_t):
    glvars.ev_manager.post(pyv.EngineEvTypes.Update, curr_t=info_t)
    glvars.ev_manager.post(pyv.EngineEvTypes.Paint, screen=glvars.screen)
    glvars.ev_manager.update()
    pyv.flip()


@pyv.declare_end
def done(vmst=None):
    pyv.close_game()
    print('gameover!')
