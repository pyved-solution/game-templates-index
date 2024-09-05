import random

from ... import glvars
from ...glvars import pyv
from ...ev_types import MyEvTypes
from ...glvars import ChoixMenu
from ...labels import Labels
from ...loctexts import tsl


BG_COLOR_NO_AUTH = glvars.colors['c_purple']
BG_COLOR_IS_AUTH = pyv.pal.japan['peach']


class MenuView(pyv.EvListener):
    """
    se basera sur un modèle pouvant alterner entre DEUX etats:
    (1) guest, et (2) player_known
    le choix "start" ne sera dévérouillé que dans le cas 2
    """

    TXT_COLOR_HL = (217, 25, 84)
    TXT_COLOR = (110, 80, 90)

    BASE_X_MENU = 175
    TAQUET_VERT = 505

    # constantes etiquette txt
    LABEL_USER_POS = (TAQUET_VERT, 165)
    LABEL_SOLDE_POS = (TAQUET_VERT, 215)

    # constantes pr placement des boutons
    BT_LOGIN_POS = (TAQUET_VERT, BASE_X_MENU + 100)
    BT_TRAINING_POS = (TAQUET_VERT, BASE_X_MENU + 170)
    BT_CHALL_POS = (TAQUET_VERT, BASE_X_MENU + 285)
    BT_EXIT_POS = (TAQUET_VERT, BASE_X_MENU + 350)

    ICON_POS = (TAQUET_VERT - 52, BT_CHALL_POS[1] - 4)

    POS_ETQ_VER = (8, glvars.SCR_SIZE[1] - 24)

    REAL_TITLE = '_Tetravalanche_'
    BROKEN_TIT = '-T3trava|a~ch3+'
    FG_COLOR = glvars.colors['c_lightpurple']
    TITLE_COLOR = glvars.colors['c_skin']
    SELEC_COLOR = glvars.colors['c_oceanblue']

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
        txt = MenuView.prettify(tmp)
        adhoc_label = self._medfont.render(txt, False, self.SELEC_COLOR)
        self._options_labels[code] = adhoc_label

        self._mem_option_active = code

    def validate_effect(self):
        glvars.playsfx(self.sfx_high)

    def __init__(self, ref_mod):
        super().__init__()

        # - son
        self.sfx_low = pyv.vars.sounds['coinlow']
        self.sfx_high = pyv.vars.sounds['coinhigh']

        # - polices de car.
        self._bigfont = glvars.fonts['moderne_big']
        self._medfont = glvars.fonts['moderne']

        # ****************** creation etiquettes pr le menu ******************
        self._options_menu = {
            ChoixMenu.DemoMode: 'Se connecter',
            ChoixMenu.StartChallenge: 'Demarrer defi',
            ChoixMenu.SeeInfos: 'Voir info.',
            ChoixMenu.QuitGame: 'Quitter'
        }
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

            i, j = random.randint(0, glvars.SCR_SIZE[0] - 1), random.randint(0, glvars.SCR_SIZE[1] - 1)
            self._allwalker_pos.append([i, j])

        self._label_titre = self._bigfont.render(
            self.REAL_TITLE, False, self.TITLE_COLOR
        )
        self._pos_titre = (glvars.SCR_SIZE[0] // 2 - (self._label_titre.get_size()[0] // 2), 50)

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
        # Etiquette.set_font(glvars.fonts['moderne'])
        self._etq_user = None
        self._etq_solde = None
        self.refresh_graphic_state()

    def refresh_graphic_state(self):
        label_user = tsl(Labels.Utilisateur)
        label_solde = tsl(Labels.Solde)

        self._etq_user = self._hugefont.render('{}= {}'.format(label_user, self.mod.get_username()), True,
                                               self.FG_COLOR)
        if self.mod.is_logged():
            self._etq_solde = self._hugefont.render('{}= {} mGold'.format(label_solde, self.mod.get_solde()), True,
                                                    self.FG_COLOR)
        else:
            self._etq_solde = None

    def on_paint(self, ev):
        self.draw_content(ev.screen)

    def on_choice_changes(self, ev):
        self.activation_option(ev.code)

    def proc_event(self, ev, source):
        if ev.type == MyEvTypes.BalanceChanges:
            self.refresh_graphic_state()

        # -- cétait pour tester
        # elif ev.type == MyEvTypes.FakeLogin:
        #     self.mod.mark_auth_done('Roger', 997)
        #     self.bt_login.turn_off()
        #     self.refresh_graphic_state()

    def dessin_boutons(self, screen):

        base_y = 128
        base_x = glvars.SCR_SIZE[0] // 2
        offset = 0
        omega_choix = [
            ChoixMenu.DemoMode,
            ChoixMenu.SeeInfos,
            ChoixMenu.QuitGame
        ]
        if glvars.ready_to_compete:
            omega_choix[0] = ChoixMenu.StartChallenge

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

    def draw_content(self, screen):

        screen.fill(BG_COLOR_NO_AUTH if not glvars.ready_to_compete else BG_COLOR_IS_AUTH)

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

            pos[1] = pos[1] % glvars.SCR_SIZE[1]
            pyv.pygame.draw.rect(screen, spd_based_color, (pos[0], pos[1], 4, 6))

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

        # pygame.transform.scale(self._vscreen, glvars.SCREEN_SIZE, screen)

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
