import glvars
import katagames_engine as kataen
from app.title_screen.MenuCtrl import MenuCtrl
from app.title_screen.TitleModel import TitleModel
from app.title_screen.TitleView import TitleView


pygame = kataen.import_pygame()


class TitleScreenState(kataen.BaseGameState):
    """
    represents the game state that shows the game title + a menu!
    """

    def __init__(self, gs_id):
        super().__init__(gs_id)
        self.v = self.m = self.c = None
        self.der_lstate = None

    def enter(self):
        if self.m is None:
            self.m = TitleModel()
        self.v = TitleView(self.m)
        if self.c is None:
            self.c = MenuCtrl(self.m, self.v)
            self.c.impacte_retour_login()

        self.v.turn_on()
        self.c.turn_on()
        glvars.init_sound()
        glvars.playmusic()

    def resume(self):
        self.c.impacte_retour_login()
        self.v.turn_on()
        if self.der_lstate != (glvars.username is None):
            self.m.reset_choice()

        self.c.turn_on()

    def release(self):
        self.c.turn_off()
        self.v.turn_off()

        pygame.mixer.music.fadeout(750)
        while pygame.mixer.music.get_busy():
            pass
        print('release( TitleScreenState) ')

    def pause(self):
        self.der_lstate = (glvars.username is None)
        self.c.turn_off()
        self.v.turn_off()
