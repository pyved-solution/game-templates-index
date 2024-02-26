from . import pimodules

pyv = pimodules.pyved_engine
pyv.bootstrap_e()

pyg = pyv.pygame

from . import glvars
from . import loctexts
from .ev_types import MyEvTypes


@pyv.declare_begin
def init_game(vmst=None):
    loctexts.init_repo(glvars.CHOSEN_LANG)
    pyv.init(wcaption='Tetravalanche')
    glvars.ev_manager = pyv.get_ev_manager()
    glvars.screen = pyv.get_surface()

    glvars.ev_manager.setup(MyEvTypes)

    glvars.init_fonts_n_colors()

    from .app.menu.state import MenuState
    from .app.tetris.state import TetrisState

    pyv.declare_game_states(
        glvars.GameStates, {
            # do this to bind state_id to the ad-hoc class!
            glvars.GameStates.Menu: MenuState,
            # glvars.GameStates.Login: ChessmatchState,
            glvars.GameStates.Tetris: TetrisState,
            # glvars.GameStates.Credits: ChessmatchState
            # glvars.GameStates.TaxPayment: ChessmatchState
        }
    )
    # - old way:
    # pyv.tag_multistate(glvars.GameStates, glvars.GameStates.Menu, True)
    # game_ctrl = pyv.get_game_ctrl()
    # game_ctrl.turn_on()

    glvars.ev_manager.post(pyv.EngineEvTypes.Gamestart)


@pyv.declare_update
def upd(time_info=None):
    # pyv.vars.gameover = True
    glvars.ev_manager.post(pyv.EngineEvTypes.Update, curr_t=time_info)
    glvars.ev_manager.post(pyv.EngineEvTypes.Paint, screen=glvars.screen)

    glvars.ev_manager.update()
    pyv.flip()


@pyv.declare_end
def done(vmst=None):
    pyv.close_game()
    print('gameover!')
