# import sharedvars
from . import pimodules
from . import glvars as vars

vars.katasdk = pimodules
pyv = pimodules.pyved_engine

pyv.bootstrap_e()

pyg = pyv.pygame
# sharedvars.katasdk
from . import util

util.init_fonts_n_colors()  # need to init colors before loading TitleView, otherwise --> crash!

# from katagames_sdk.capsule.networking.httpserver import HttpServer
from .defs import GameStates
from . import loctexts
from .puzzle_state import PuzzleState
from .menu_state import TitleScreenState
from .ev_types import BlokuEvents
from . import glvars

# TODO: fix
HttpServer = None

# -------------------------
# version ultra ancienne :

# HttpServer = old_v_kengi.network.HttpServer  # katasdk.network.HttpServer in future versions
# class BlokuGame(kengi.GameTpl):
#
#
#         # xxx DOUBLEMENT deprecated xxx
#         ## - juste un test réseau, ce reset game ne sert a rien pour BLOKU-MAN,
#         ## il est utile pour mConquest...
#         ## serv = HttpServer.instance()
#         ## url = 'https://sc.gaudia-tech.com/tom/'
#         ## params = {}
#         ## full_script = url+'resetgame.php'
#         ## print(full_script)
#         ## res = serv.proxied_get(full_script, params)
#         ## game_ctrl = kengi.get_game_ctrl()
#         ## game_ctrl.turn_on()
#
#         important! Its needed to proc the 1st gstate 'do_init' method
#         self._manager.post(kengi.EngineEvTypes.Gamestart)
# blokuwrapper.glvars.gameref = game = BlokuGame()
# katasdk.gkart_activation(game)

# ------------------------
# version qui date de juin 2024, manque une refonte ici
# class BlokumanGame(pyv.GameTpl):
    # def get_video_mode(self):
        # return 1
    # def list_game_events(self):
        # return BlokuEvents
    # def enter(self, vms=None):
        # safer this way:
        # self.nxt_game = 'game_selector'
        # loctexts.init_repo(glvars.CHOSEN_LANG)
        # super().enter(vms)
        # pyv.declare_game_states(  # doit etre appelé après le setup_ev_manager !!!
            # GameStates,
            # {
                # GameStates.TitleScreen: TitleScreenState,
                # GameStates.Puzzle: PuzzleState
            # }
        # )
# game = BlokumanGame()


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
