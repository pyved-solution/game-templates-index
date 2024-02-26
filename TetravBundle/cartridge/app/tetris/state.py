from ... import glvars
import pyved_engine as pyv

# import katagames_sdk.engine as kataen
# from katagames_sdk.engine import BaseGameState
from ...modele_tetris import Board
from .TetrisView import TetrisView
from .TetrisCtrl import TetrisCtrl

pygame = pyv.pygame


class TetrisState(pyv.BaseGameState):

    def __init__(self, state_ident):

        super().__init__(state_ident)  #, state_name)
        self._ctrl = None
        self.ma_vue = None

    def enter(self):
        damod = Board(10, 20)
        damod.rand.seed(glvars.chall_seed)
        da_cfonts = {}
        if pygame.font.get_init():
            # before :
            # da_cfonts["game_over"] = pygame.font.SysFont("ni7seg", 60)
            # da_cfonts["score"] = pygame.font.SysFont("ni7seg", 18)
            # TODO fix this temp patch for web ctx
            da_cfonts["game_over"] = pygame.font.Font(None, 66)
            da_cfonts["score"] = pygame.font.Font(None, 18)
        
        # - view creation
        self.ma_vue = TetrisView(
            glvars.screen.get_size(), glvars.colors['c_purple'], glvars.colors['c_lightpurple']
        )
        self.ma_vue.turn_on()

        # - ctrl
        self._ctrl = TetrisCtrl(damod, self.ma_vue)

        # -launch
        self._ctrl.setup_ctrl()
        self._ctrl.turn_on()

    def release(self):
        self._ctrl.turn_off()
        self.ma_vue.turn_off()
