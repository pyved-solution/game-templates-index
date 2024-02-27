import json
import random

from ... import glvars
from ...ev_types import MyEvTypes
# from katagames_sdk.capsule.gui import Etiquette
from ...labels import Labels
from ...loctexts import tsl
# from katagames_sdk.engine import CogObject, EventReceiver, EngineEvTypes, BaseGameState, CgmEvent
# import katagames_sdk.engine as kataen

# TODO cmt ca se goupille avec l'api historique katagames?
# si on fait pyv-cli play ...

# from katagames_sdk.api import HttpServer


from ... import glvars

from ... import pimodules

pyv = pimodules.pyved_engine


pygame = pyv.pygame

# SCR_W, SCR_H = kataen.get_screen().get_size()
SCR_W, SCR_H = 960, 720


class MenuModel(pyv.Emitter):
    """
    stocke l'info. si le joueur est connecté ou nom
    """
    COUT_PARTIE = 10

    BINF_CHOIX = 134
    CHOIX_LOGIN, CHOIX_START, CHOIX_CRED, CHOIX_QUIT = range(BINF_CHOIX, BINF_CHOIX+4)

    def __init__(self):
        super().__init__()
        self._curr_choice = self.CHOIX_LOGIN

    def reset_choice(self):
        if self.is_logged():
            self._curr_choice = self.CHOIX_START
        else:
            self._curr_choice = self.CHOIX_LOGIN
        self.pev(MyEvTypes.ChoiceChanges, code=self._curr_choice)

    def get_curr_choice(self):
        return self._curr_choice

    def move(self, direction):
        assert direction in (-1, +1)
        self._curr_choice += direction

        if not self.is_logged():
            if self._curr_choice == self.CHOIX_START:
                self._curr_choice += direction
            if self._curr_choice > self.CHOIX_QUIT:
                self._curr_choice = self.CHOIX_LOGIN
            elif self._curr_choice < self.CHOIX_LOGIN:
                self._curr_choice = self.CHOIX_QUIT
            self.pev(MyEvTypes.ChoiceChanges, code=self._curr_choice)
            return

        # on est connecté
        if self._curr_choice == self.CHOIX_LOGIN:
            self._curr_choice += direction
        if self._curr_choice > self.CHOIX_QUIT:
            self._curr_choice = self.CHOIX_START
        elif self._curr_choice < self.CHOIX_START:
            self._curr_choice = self.CHOIX_QUIT
        self.pev(MyEvTypes.ChoiceChanges, code=self._curr_choice)


    def is_logged(self):
        return glvars.username is not None

    def mark_auth_done(self, user, solde_gp):
        self._logged_in = True
        glvars.nom_utilisateur = user
        glvars.solde_gp = solde_gp

    def mark_logout(self):
        self._logged_in = False
        glvars.cli_logout()

    def can_bet(self):
        if not self._logged_in:
            return False
        if self.get_solde() is None:
            return False
        return self.get_solde() >= self.COUT_PARTIE

    def get_username(self):
        if not self.is_logged():
            return tsl(Labels.NomJoueurAnonyme)
        return glvars.nom_utilisateur

    def set_solde(self, val):
        glvars.solde_gp = val
        manager = kataen.get_manager()
        manager.post(
            CgmEvent(MyEvTypes.BalanceChanges, value=val)
        )

    def get_solde(self):
        if not self.is_logged():
            raise Exception('demande solde alors que _logged_in à False')
        return glvars.solde_gp


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

    POS_ETQ_VER = (8, SCR_H - 24)

    REAL_TITLE = '_Tetravalanche_'
    BROKEN_TIT = '-T3trava|a~ch3+'
    FG_COLOR = glvars.colors['c_lightpurple']
    TITLE_COLOR = glvars.colors['c_skin']
    BG_COLOR = glvars.colors['c_purple']
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
            MenuModel.CHOIX_LOGIN: 'Se connecter',
            MenuModel.CHOIX_START: 'Demarrer defi',
            MenuModel.CHOIX_CRED: 'Voir info.',
            MenuModel.CHOIX_QUIT: 'Quitter'
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

            i, j = random.randint(0, SCR_W-1), random.randint(0, SCR_H-1)
            self._allwalker_pos.append([i,j])

        self._label_titre = self._bigfont.render(
            self.REAL_TITLE, False, self.TITLE_COLOR
        )
        self._pos_titre = ( SCR_W//2 - (self._label_titre.get_size()[0]//2), 50)

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

        self._etq_user = self._hugefont.render('{}= {}'.format(label_user, self.mod.get_username()), True, self.FG_COLOR)
        if self.mod.is_logged():
            self._etq_solde = self._hugefont.render('{}= {} mGold'.format(label_solde, self.mod.get_solde()), True, self.FG_COLOR)
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
        base_x = SCR_W // 2
        offset = 0
        if glvars.username:
            omega_choix = (MenuModel.CHOIX_START,MenuModel.CHOIX_CRED, MenuModel.CHOIX_QUIT)
        else:
            omega_choix = (MenuModel.CHOIX_LOGIN,MenuModel.CHOIX_CRED,MenuModel.CHOIX_QUIT)

        for c in omega_choix:
            label = self._options_labels[c]
            pos = (base_x - (label.get_size()[0]//2), base_y + offset)
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

        screen.fill(self.BG_COLOR)

        # - dessin bonhommes
        for k, pos in enumerate(self._allwalker_pos):
            spd = self._walker_speed[k]
            pos[1] += spd
            if spd in (1,2):
                spd_based_color = glvars.colors['c_mud']
            elif spd in (3,4):
                spd_based_color = glvars.colors['c_brown']
            else:
                spd_based_color = glvars.colors['c_gray1']

            pos[1] = pos[1] % SCR_H
            pygame.draw.rect(screen, spd_based_color, (pos[0], pos[1], 4, 6))

        # - dessin titre
        if random.random()<0.1:
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


class MenuCtrl(pyv.EvListener):

    POLLING_FREQ = 4  # sec. de délai entre deux appels serveur

    def __init__(self, mod, view):
        super().__init__()
        self.ref_mod = mod
        self.ref_view = view

        # - prepa de quoi changer de mode de jeu...
        self.nextmode_buffer = None

        # - misc
        self.last_pol = None
        self.logged_in = mod.is_logged()
        self.polling_mode = True

        # TODO fix networking
        #  self.serv = HttpServer.instance()
        self.serv = None

    def pause_polling(self):
        self.polling_mode = False

    def resume_polling(self):
        self.polling_mode = True

    def __handlelogic(self, ev):

        if self.nextmode_buffer is not None:
            if glvars.is_sfx_playin():
                pass
            else:
                # traitement nextmode_buffer...
                if self.nextmode_buffer == MenuModel.CHOIX_START:
                    self.pev(MyEvTypes.DemandeTournoi)

                elif self.nextmode_buffer == MenuModel.CHOIX_QUIT:
                    pyv.vars.gameover = True

                elif self.nextmode_buffer == MenuModel.CHOIX_LOGIN:  # play
                    # je push state tetris
                    print('je push state tetris')
                    self.pev(pyv.EngineEvTypes.StatePush, state_ident=glvars.GameStates.Tetris)
                    # self._assoc_cchoix_event = {
                    # MenuModel.CHOIX_QUIT: pyv.KengiEv(pyv.EngineEvTypes.QUIT),
                    # MenuModel.CHOIX_CRED: pyv.KengiEv(pyv.EngineEvTypes.PUSHSTATE,
                    #                                   state_ident=glvars.GameStates.Credits),
                    # MenuModel.CHOIX_START: None,  # celui-ci est géré via un evenement MyEvTypes.DemandeTournoi !
                    # MenuModel.CHOIX_LOGIN: pyv.KengiEv(pyv.EngineEvTypes.PUSHSTATE,
                    #            state_ident=glvars.GameStates.Login)
                    # }

                    # ---- oldcode ----
                    #ev = self._assoc_cchoix_event[self.nextmode_buffer]
                    #if ev is not None:
                    #    kataen.get_manager().post(ev)

                # reset du champ concerné
                self.nextmode_buffer = None
            return  # ---------------------------------------------------------------

        if self.logged_in:
            if not self.polling_mode:
                return
            if (self.last_pol is None) or (ev.curr_t - self.last_pol > self.POLLING_FREQ):
                self.last_pol = ev.curr_t
                nouv_solde = self._recup_solde_serveur()
                self.ref_mod.set_solde(nouv_solde)

    # --------------------------------------
    #  Gestion des évènements
    # --------------------------------------
    def on_update(self, ev):
        self.__handlelogic(ev)

    def on_keydown(self, ev):
        if ev.key == pygame.K_UP:
            self.ref_mod.move(-1)

        elif ev.key == pygame.K_DOWN:
            self.ref_mod.move(1)

        elif ev.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            self.nextmode_buffer = self.ref_mod.get_curr_choice()
            self.ref_view.validate_effect()

    def proc_event(self, ev, source):
        if ev.type == MyEvTypes.DemandeTournoi:
            if self.ref_mod.can_bet() and self._procedure_debut_challenge():
              self.pev(EngineEvTypes.PUSHSTATE, state_ident=glvars.GameStates.Tetris)
            return  # ---------------------------------------------------------------------------

        # ------------- feature spéciale : faux login ----------
        # if glvars.DEV_MODE:
        #     if ev.type == PygameBridge.KEYDOWN:
        #         if ev.key == K_F10:
        #             self._logged_in = True
        #             self.polling_mode = False
        #             self.ref_mod.force_fakelogin()

    def _procedure_debut_challenge(self):
        """
        :return: bool disant si oui ou non, la procédure s'est déroulé correctement
        """

        if glvars.DEV_MODE:
            print('DEBUG:  _procedure_debut_challenge')

        # - on récupère n° seed et de tournoi
        target = self.serv.get_ludo_app_url() + 'tournois.php'
        params = {
            'fct': 'play_it',
            'game_id': str(glvars.GAME_ID)  # identifie le jeu ds le système du ludo.store
        }
        res = self.serv.proxied_get(target, params)
        tmp = json.loads(res)

        if glvars.DEV_MODE:
            print('DEBUG:  appel sur tournois.php donne...')
            print(str(tmp))
        glvars.num_challenge = int(tmp[0])
        glvars.chall_seed = int(tmp[1])

        # - on paye le droit d'entrée et c'est parti
        params = {
            'fct': 'pay_due',
            'price': str(MenuModel.COUT_PARTIE),
            'cid': str(glvars.num_challenge),
            'id_perso': str(glvars.id_perso)
        }
        res = self.serv.proxied_get(target, params)
        tmp = json.loads(res)
        return tmp

    def _recup_solde_serveur(self):
        if glvars.DEV_MODE:
            print('envoi serveur...')

        target = self.serv.get_gtm_app_url() + 'maj_solde.php'
        params = {
            'id_perso': glvars.id_perso,
            'updating': 0
        }
        res = self.serv.proxied_get(target, params)
        tmp = json.loads(res)
        if tmp is None:
            raise Exception('cannot retrieve players balance!')
        return int(tmp)

    def impacte_retour_login(self):
        if glvars.username:
            self.ref_mod.mark_auth_done(glvars.username, glvars.copie_solde)
            self.logged_in = True
            self.ref_view.refresh_graphic_state()


class MenuState(pyv.BaseGameState):

    def __init__(self, gs_id):

        super().__init__(gs_id)  #, name)
        self.v = self.m = self.c = None
        self.der_lstate = None

    def enter(self):
        if self.m is None:
            self.m = MenuModel()

        self.v = MenuView(self.m)
        self.v.turn_on()

        if self.c is None:
            self.c = MenuCtrl(self.m, self.v)

        self.c.turn_on()

        glvars.init_sound()

        # disabled for now (music)
        # glvars.playmusic()

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

        if glvars.DEV_MODE:
            print('--- Sortie propre OK ---')

    def pause(self):
        self.der_lstate = (glvars.username is None)
        self.c.turn_off()
        self.v.turn_off()
