import katagames_engine as kataen
from app.puzzle.model import BoardModel, BagFulloPieces
from app.puzzle.PuzzleCtrl import PuzzleCtrl
from app.puzzle.PuzzleView import PuzzleView
from app.puzzle.ScoreView import ScoreView

pygame = kataen.pygame


class PuzzleState(kataen.BaseGameState):
    """
    classe qui gère le mode de jeu
    ou l'on assemble des pièces en tetromino
    """

    def __init__(self, state_ident):
        super().__init__(state_ident)
        self._ctrl = None
        self.ma_vue = None
        self.score_view = None

    def enter(self):
        the_board = BoardModel(10, 10)  # un arg supplémentaire ne servirait a rien
        avail = BagFulloPieces(the_board)

        # -- - - we used to init seed -  - - -
        # damod.rand.seed(glvars.chall_seed)

        da_cfonts = {}
        if pygame.font.get_init():
            da_cfonts["game_over"] = pygame.font.Font(None, 60)  # Sysfont "ni7seg"
            da_cfonts["score"] = pygame.font.Font(None, 18)

        # - view creation
        pos_origine = (16, 40)
        self.ma_vue = PuzzleView(the_board, avail, pos_origine)
        self.score_view = ScoreView(the_board, pos_origine, self.ma_vue.px_width)

        self.ma_vue.turn_on()
        self.score_view.turn_on()

        # - ctrl
        self._ctrl = PuzzleCtrl(the_board, avail, self.ma_vue, self.score_view)

        # -launch
        self._ctrl.turn_on()

    def release(self):
        self._ctrl.turn_off()
        self.ma_vue.turn_off()
        self.score_view.turn_off()
