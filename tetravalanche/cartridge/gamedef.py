from . import glvars
from . import loctexts
from . import pimodules
from .ev_types import MyEvTypes


pyv = pimodules.pyved_engine
pyv.bootstrap_e()


@pyv.declare_begin
def init_game(vmst=None):
    loctexts.init_repo(glvars.CHOSEN_LANG)
    pyv.init(wcaption='Tetravalanche')
    glvars.screen = pyv.get_surface()

    glvars.ev_manager = pyv.get_ev_manager()
    glvars.ev_manager.setup(MyEvTypes)
    glvars.init_fonts_n_colors()

    # - init game states & boot up the game, now!
    from .app.menu.state import MenuState
    from .app.tetris.state import TetrisState
    pyv.declare_game_states(
        glvars.GameStates, {
            glvars.GameStates.Menu: MenuState,
            glvars.GameStates.Tetris: TetrisState,
        }
    )
    glvars.ev_manager.post(pyv.EngineEvTypes.Gamestart)


@pyv.declare_update
def upd(time_info=None):
    glvars.ev_manager.post(pyv.EngineEvTypes.Update, curr_t=time_info)
    glvars.ev_manager.post(pyv.EngineEvTypes.Paint, screen=glvars.screen)
    glvars.ev_manager.update()
    pyv.flip()


@pyv.declare_end
def done(vmst=None):
    pyv.close_game()
