import glvars
from ev_types import MyEvTypes
import katagames_engine as kataen
# from katagames_sdk import api as katapi

kevent = kataen.event

pygame = kataen.pygame


class PuzzleCtrl(kevent.EventReceiver):

    def __init__(self, board_mod, avail, ref_view, view_score):
        super().__init__()
        self.view2 = view_score
        self.boardmodel = board_mod
        self._avail = avail
        self.view = ref_view
        self.game_over = False

        self.show_action = None
        self._score_sent = False
        self._rdy_to_exit = False

    def flag_games_over(self):
        self.game_over = True
        self._score_sent = False
        self._rdy_to_exit = False
    # ---------------------------------------
    #  GESTION EV. COREMON ENG.
    # ---------------------------------------
    def proc_event(self, ev, source):

        if ev.type == MyEvTypes.GameLost:
            self.flag_games_over()
            self.view2.flag_game_over = True

        elif ev.type == kevent.EngineEvTypes.LOGICUPDATE:
            if self.game_over:
                if not self._score_sent:
                    pass
                    # TODO fix later
                    # katapi.push_score(
                    #     glvars.acc_id, glvars.username, glvars.num_challenge, self.boardmodel.score
                    # )
                    self._score_sent = True

        elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_RETURN:
            if self.game_over and self._score_sent and (not self._rdy_to_exit):
                self._rdy_to_exit = True

        elif ev.type == pygame.KEYUP:
            if self._rdy_to_exit:
                self.pev(kevent.EngineEvTypes.POPSTATE)
