import random

import glvars
import katagames_sdk.capsule.event as kevent
import katagames_sdk.engine as kataen
from app.title_screen.TitleModel import TitleModel
from ev_types import MyEvTypes
from katagames_sdk.engine import EventReceiver
from katagames_sdk.engine import gui
from labels import Labels
from loctexts import tsl


pygame = kataen.import_pygame()


class TitleView(EventReceiver):
    """
    se basera sur un modèle pouvant alterner entre DEUX etats:
    (1) guest, et (2) player_known
    le choix "start" ne sera dévérouillé que dans le cas 2
    """

    TXT_COLOR_HL = (217, 25, 84)
    TXT_COLOR = (110, 80, 90)

    POS_ETQ_VER = None

    REAL_TITLE = '- BLoKu Man -'
    BROKEN_TIT = '+ bL0Ku m4N ~'

    FG_COLOR = glvars.colors['c_lightpurple']
    TITLE_COLOR = glvars.colors['c_mud']
    BG_COLOR = glvars.colors['bgspe_color']
    SELEC_COLOR = glvars.colors['c_oceanblue']

    def __init__(self, ref_mod):
        super().__init__()

        self.scr_size = kataen.get_screen().get_size()
        self.midx = self.scr_size[0]//2

        # - retro effect, part 1
        # self._vscr_size = (SCR_W, SCR_H)
        # self._vscreen = pygame.Surface(self._vscr_size)

        # - son
        self.sfx_low = pygame.mixer.Sound('assets/coinlow.wav')
        self.sfx_high = pygame.mixer.Sound('assets/coinhigh.wav')

        # - polices de car.
        self._bigfont = glvars.fonts['moderne_big']
        self._medfont = glvars.fonts['moderne']

        # ****************** creation etiquettes pr le menu ******************
        self._options_menu = {
            TitleModel.CHOIX_LOGIN: 'Se connecter',
            TitleModel.CHOIX_START: 'Demarrer defi',
            TitleModel.CHOIX_CRED: 'Voir info.',
            TitleModel.CHOIX_QUIT: 'Quitter'
        }
        # TODO clean up
        if kataen.runs_in_web():
            self._options_menu[TitleModel.CHOIX_QUIT] = 'Log out'

        self._options_labels = dict()
        for code in self._options_menu.keys():
            self._reset_label_option(code)

        self._mem_option_active = None
        self.activation_option(ref_mod.get_curr_choice())

        # ****************** prepa pour effets particules ******************
        self._allwalker_pos = list()
        self._walker_speed = dict()

        for k in range(20):
            self._walker_speed[k] = random.randint(1, 6)

            i, j = random.randint(0, self.scr_size[0] - 1), random.randint(0, self.scr_size[1] - 1)
            self._allwalker_pos.append([i, j])

        self._label_titre = self._bigfont.render(
            self.REAL_TITLE, False, self.TITLE_COLOR
        )
        self._pos_titre = (
            (self.scr_size[0] - self._label_titre.get_size()[0]) // 2,
            50
        )

        self.mod = ref_mod
        self._hugefont = glvars.fonts['moderne']
        spefont = glvars.fonts['tiny_monopx']
        self._font = glvars.fonts['tiny_monopx']
        self._smallfont = glvars.fonts['tiny_monopx']
        self._boutons = list()
        self.bt_chall = None
        self.bt_login = None
        self.bt_exit = None

        # - crea etiquettes qui habillent bouton challenge
        gui.Etiquette.set_font(glvars.fonts['moderne'])
        self._etq_user = None
        self._etq_solde = None
        self.refresh_graphic_state()

    @staticmethod
    def prettify(txt):
        return '/\\----[__' + txt + '__]----\\/'

    def _reset_label_option(self, code):
        txt = self._options_menu[code]
        adhoc_label = self._medfont.render(txt, False, self.FG_COLOR)
        self._options_labels[code] = adhoc_label

    def activation_option(self, code):
        if self._mem_option_active is not None:
            glvars.playsfx(self.sfx_low)
            self._reset_label_option(self._mem_option_active)

        tmp = self._options_menu[code]
        txt = TitleView.prettify(tmp)
        adhoc_label = self._medfont.render(txt, False, self.SELEC_COLOR)
        self._options_labels[code] = adhoc_label

        self._mem_option_active = code

    def validate_effect(self):
        glvars.playsfx(self.sfx_high)

    def refresh_graphic_state(self):
        label_user = tsl(Labels.Utilisateur)
        label_solde = tsl(Labels.Solde)
        spe_color = (210, 33, 35)
        self._etq_user = self._medfont.render(
            '{}= {}'.format(label_user, self.mod.get_username()), False, spe_color
        )
        if self.mod.is_logged():
            self._etq_solde = self._medfont.render(
                '{}= {} MOBI'.format(label_solde, self.mod.get_solde()), False, spe_color
            )
        else:
            self._etq_solde = None

    def proc_event(self, ev, source):
        if ev.type == kevent.EngineEvTypes.PAINT:
            self._paint(ev.screen)

        elif ev.type == MyEvTypes.ChoiceChanges:
            self.activation_option(ev.code)

        elif ev.type == MyEvTypes.BalanceChanges:
            self.refresh_graphic_state()

        # -- cétait pour tester
        # elif ev.type == MyEvTypes.FakeLogin:
        #     self.mod.mark_auth_done('Roger', 997)
        #     self.bt_login.turn_off()
        #     self.refresh_graphic_state()

    def dessin_boutons(self, screen):

        base_y = 128
        base_x = self.midx
        offset = 0
        if glvars.username:
            omega_choix = (TitleModel.CHOIX_START, TitleModel.CHOIX_CRED, TitleModel.CHOIX_QUIT)
        else:
            omega_choix = (TitleModel.CHOIX_LOGIN, TitleModel.CHOIX_CRED, TitleModel.CHOIX_QUIT)

        for c in omega_choix:
            label = self._options_labels[c]
            pos = (base_x - (label.get_size()[0] // 2), base_y + offset)
            offset += 40
            screen.blit(label, pos)

        # for bt in self._boutons:
        #     # les boutons login & chall font l'objet d'un traitement a part
        #     if bt in (self.bt_login, self.bt_chall):
        #         continue
        #
        #     if bt == self.bt_exit:
        #         screen.blit(self.img_bt_rouge, (bt.position[0] - 4, bt.position[1] + decal_y))
        #
        #     elif bt == self.bt_training:  # signe désactivation bt training
        #         screen.blit(self.img_bt_gris, (bt.position[0] - 4, bt.position[1] + decal_y))
        #     else:
        #         screen.blit(self.img_bt_bleu, (bt.position[0] - 4, bt.position[1] + decal_y))
        #
        #     screen.blit(bt.image, bt.position)
        #
        # # - dessin (traitement particulier) bt login !
        # if not self.mod.is_logged():  # on cache le bouton login
        #     screen.blit(self.img_bt_vert, (self.bt_login.position[0] - 4, self.bt_login.position[1] + decal_y))
        #     screen.blit(self.bt_login.image, self.bt_login.position)
        #
        # # - dessin (traitement particulier) bt chall !
        # if self.mod.can_bet():
        #     img_adhoc = self.img_bt_bleu
        # else:
        #     img_adhoc = self.img_bt_gris
        #
        # screen.blit(img_adhoc, (self.bt_chall.position[0] - 4, self.bt_chall.position[1] + decal_y))
        # screen.blit(self.bt_chall.image, self.bt_chall.position)

    def _paint(self, screen):
        screen.fill(self.BG_COLOR)

        # - dessin bonhommes
        for k, pos in enumerate(self._allwalker_pos):
            spd = self._walker_speed[k]
            pos[1] += spd
            if spd in (1, 2):
                spd_based_color = glvars.colors['c_mud']
            elif spd in (3, 4):
                spd_based_color = glvars.colors['c_brown']
            else:
                spd_based_color = glvars.colors['c_gray1']

            pos[1] = pos[1] % self.scr_size[1]
            pygame.draw.rect(screen, spd_based_color, (pos[0], pos[1], 4, 6))

        # - dessin titre
        if random.random() < 0.1:
            if random.random() > 0.5:
                txt = self.REAL_TITLE
            else:
                txt = self.BROKEN_TIT
            self._label_titre = self._bigfont.render(txt, False, self.TITLE_COLOR)

        screen.blit(self._label_titre, self._pos_titre)

        # -- menu --
        self.dessin_boutons(screen)

        if self._etq_solde:
            screen.blit(self._etq_user, (int(0.05*self.scr_size[0]), 6))
            screen.blit(self._etq_solde, (int(0.05*self.scr_size[0]), 26))
        # - retro effect part 2
        # pygame.transform.scale(screen, glvars.SCREEN_SIZE, screen)

    # association état avec ceux des boutons
    def turn_on(self, prio=None):
        super().turn_on()
        for bt in self._boutons:
            bt.turn_on()
        self.refresh_graphic_state()

    def turn_off(self):
        super().turn_off()
        for bt in self._boutons:
            bt.turn_off()
