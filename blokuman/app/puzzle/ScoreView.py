import katagames_engine as kengi
import glvars
from ev_types import MyEvTypes

kataen = kengi
pygame = kataen.pygame
EventReceiver = kengi.event.EventReceiver
EngineEvTypes = kengi.event.EngineEvTypes


class ScoreView(EventReceiver):
    """
    displays the score, play sounds
    """

    def __init__(self, boardmod, orgpoint, board_px_width):
        super().__init__()
        self.board_px_width = board_px_width

        self._board_model = boardmod
        self.score_img = None
        self.org_point = orgpoint

        self.font_color = glvars.colors['c_lightpurple']
        self.bgcolor = glvars.colors['c_purple']

        self.go_font = glvars.fonts['moderne_big']
        self.sc_font = glvars.fonts['sm_monopx']

        # sons
        self.sfx_explo = pygame.mixer.Sound('assets/explo_basique.wav')
        self.sfx_crumble = pygame.mixer.Sound('assets/crumble.wav')

        # - labels
        self._gameover_img_bg = None
        self._gameover_img_label = None

        self.flag_game_over = False

        self.scr = kataen.get_screen()
        self.view_width, self.view_height = self.scr.get_size()

        self.refresh_score_img(self._board_model.score)

    def refresh_score_img(self, num_val):
        self.score_img = self.sc_font.render("SCORE {:06d}".format(num_val), False, self.font_color)

    def proc_event(self, ev, source):
        if ev.type == EngineEvTypes.PAINT:
            self._paint(ev.screen)

        elif ev.type == MyEvTypes.ScoreChanges:
            self.refresh_score_img(ev.score)

        elif ev.type == MyEvTypes.LineDestroyed:
            glvars.playsfx(self.sfx_crumble)

        elif ev.type == MyEvTypes.BlocksCrumble:
            glvars.playsfx(self.sfx_explo)

    def _paint(self, screen):
        imgw, imgh = self.score_img.get_size()
        tx, ty = self.org_point[0] + (self.board_px_width - imgw) // 2, self.org_point[1] - imgh
        screen.blit(self.score_img, (tx, ty))

        if self.flag_game_over:
            self.draw_game_over_msg(screen)

    def draw_game_over_msg(self, ecran):
        # -- affiche simili -popup
        if not self._gameover_img_bg:
            self._gameover_img_bg = pygame.image.load('assets/img_bt_rouge.png')

        targetp = [self.view_width // 2, self.view_height // 2]
        targetp[0] -= self._gameover_img_bg.get_size()[0] // 2
        targetp[1] -= self._gameover_img_bg.get_size()[1] // 2
        ecran.blit(self._gameover_img_bg, targetp)

        # -- affiche msg
        if not self._gameover_img_label:
            self._gameover_img_label = self.go_font.render("Jeu termine, ENTREE pr sortir", False, self.font_color)

        r = self._gameover_img_label.get_rect()
        targetpos = (
            (self.view_width // 2) - (r.width // 2),
            (self.view_height // 2) - (r.height // 2)
        )
        ecran.blit(self._gameover_img_label, targetpos)
