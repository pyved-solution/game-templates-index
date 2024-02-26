import json
import time
import gui
from katagames_sdk.capsule.gui import Etiquette
from katagames_sdk.engine import EventReceiver, EngineEvTypes, CogObject, CgmEvent, BaseGameState
from ev_types import MyEvTypes
import glvars
from labels import Labels
from katagames_sdk.api import HttpServer
from loctexts import tsl
import katagames_sdk.engine as kataen


COORD_X_CHAMPS_TXT = 100
TEXT_INPUT_SIZE = 340
INTER_FIELD_OFFSET = 55  # offset en px pour décaler second champ texte...
POS_BT_CONFIRM = (COORD_X_CHAMPS_TXT, 500)
POS_BT_CANCEL = (COORD_X_CHAMPS_TXT, POS_BT_CONFIRM[1]+ INTER_FIELD_OFFSET)
POS_LBL_LOGIN = (215, 380)
POS_LBL_PASSWORD = (215, POS_LBL_LOGIN[1] + INTER_FIELD_OFFSET)


pygame = kataen.import_pygame()


class LoginModel(CogObject):
    """
    classe utilisée pr stocker temporairement login / pwd
    durant le processus de login. Le pwd est gardé secret (pas d'affichage) mais on compte et
    on affiche correctement le nb de car
    """

    def __init__(self):
        super().__init__()
        #data_cote_cli = LocalStorage.instance()
        #self.curr_login = data_cote_cli.get_val('stored_username')
        #self.curr_pwd = data_cote_cli.get_val('stored_pwd')
        self.save_pwd = False  #len(self.curr_pwd) > 0
        self.curr_login = ''
        self.curr_pwd = ''
        self.focus_sur_login = True  # valeur initiale pr : ou se trouve la boite de focus

    def ajoute_lettre(self, c):
        if self.focus_sur_login:
            self.curr_login += c
        else:
            self.curr_pwd += c

    def set_focus_pwd(self):
        self.focus_sur_login = False

    def set_focus_login(self):
        self.focus_sur_login = True

    def toggle_focus(self):
        # TODO faire partir m-a-j graphique depuis le modèle ?
        if self.focus_sur_login:
            self.set_focus_pwd()
            return
        self.set_focus_login()

    def suppr_lettre(self):
        if self.focus_sur_login:
            if len(self.curr_login) > 0:
                self.curr_login = self.curr_login[:-1]
                #self._manager.post(
                #    CredentialsChangedEvent(self.curr_login, None)
                #)
        else:
            if len(self.curr_pwd) > 0:
                self.curr_pwd = self.curr_pwd[:-1]
                #self._manager.post(
                #    CredentialsChangedEvent(None, self.getPwdStr())
                #)

    # méthodes pr la remise à zéro
    # def resetPwdOnly(self):
    #     if len(self.curr_pwd) > 0:
    #         self.curr_pwd = ''
    #         tag_pwd = self.getPwdStr()
    #         self._manager.post(
    #             CredentialsChangedEvent(None, tag_pwd)
    #         )

    def reset_fields(self):
        self.curr_login = ''
        self.curr_pwd = ''
        self.pev(MyEvTypes.LoginModUpdate, login='', pwd='')

    # méthodes utiles pour initialiser la vue, mais aussi pr masquer le mot de passe dans laffichage graphique
    def isFocusingLogin(self):
        return self.focus_sur_login

    def getLoginStr(self):
        return self.curr_login

    def getPwdStr(self):
        k = len(self.curr_pwd)
        li_etoiles = '*' * k
        return ''.join(li_etoiles)

    def change_pwd_save(self):
        self.save_pwd = not self.save_pwd
        return self.save_pwd

    def get_save_pwd(self):
        return self.save_pwd


class LoginView(EventReceiver):
    """
    affiche écran intermédiaire permettant la SAISIE des IDENT.
    """

    ERR_MSG_DELAY = 2.5  # sec
    POS_BT_BROWSER = (385, 215)

    # ------------------
    #  positions des labels
    # TODO ramener depuis extérieur classe

    def __init__(self, ref_mod, fgcolor, bgcolor):
        super().__init__()

        self.bgcolor = bgcolor
        self.fgcolor = fgcolor

        self._ref_mod = ref_mod
        self.scr = kataen.get_screen()

        self._font = glvars.fonts['moderne']
        self._buttons = list()
        self._crea_boutons()
        self.focus = 0
        self.red_color = glvars.colors['c_cherokee']
        self._fin_aff_flottant = None

        self.saisie_txt1 = gui.TextInput('>', self._font, LoginView.nop, (100, 305), TEXT_INPUT_SIZE)

        self.saisie_txt2 = gui.TextInput('>', self._font, LoginView.nop, (100, 375), TEXT_INPUT_SIZE)
        self.saisie_txt2.pwd_field = True

        # *** plein d'étiquettes...
        # Please identify yourself
        # No account yet? Sign up via http://ludo.store."

        # ACCOUNT-
        # LOGIN-
        self._etiquettes = [
            Etiquette(tsl(Labels.SensLogin), (100, 200), self.fgcolor),
            Etiquette(tsl(Labels.CanCreateAcc), (100, 230), self.fgcolor),
            # Etiquette(tsl(Labels.InciteLudoStore), (100, 260), self.TXT_COLOR)  # It's easy, fast and 100% free!

            Etiquette(tsl(Labels.WordLogin), (80, 280), self.fgcolor),
            Etiquette(tsl(Labels.WordPassword), (80, 340), self.fgcolor)
        ]

        self._err_etiquette = Etiquette(
            tsl(Labels.CannotLogin), (100, 420), self.red_color
        )

    @staticmethod
    def confirm_routine():
        # TODO déclencher interrogation serveur
        # TODO exporter trucs vers le contrôleur, c'est lui qui va popstate
        ev = CgmEvent(MyEvTypes.TrigValidCredentials)
        kataen.get_manager().post(ev)

    @staticmethod
    def cancel_routine():
        ev = CgmEvent(EngineEvTypes.POPSTATE)  # state_ident=GameStates.IntroJeu)
        kataen.get_manager().post(ev)

    @staticmethod
    def nop(txt):
        pass

    # @staticmethod
    # def go_browser():
    #     webbrowser.open('http://ludo.store', new=1, autoraise=True)

    def _crea_boutons(self):
        txt = tsl(Labels.Connexion)
        bt = gui.Button(self._font, txt, POS_BT_CONFIRM, LoginView.confirm_routine)
        self._buttons.append(bt)

        txt = tsl(Labels.RetourArr)
        bt = gui.Button(self._font, txt, POS_BT_CANCEL, LoginView.cancel_routine)
        self._buttons.append(bt)

        # self.bt_browser = gui.Button(
        #     self._font, tsl(Labels.OpenBrowser), self.POS_BT_BROWSER, LoginView.go_browser, draw_background=False)
        # self._buttons.append(self.bt_browser)

    # - activation / désactivation impacte boutons également
    def turn_on(self, prio=None):
        super().turn_on()
        for bt in self._buttons:
            bt.turn_on()

        self.focus = 0
        self.saisie_txt1.turn_on()
        self.saisie_txt1.focus()

    def turn_off(self):
        super().turn_off()
        for bt in self._buttons:
            bt.turn_off()
        if self.focus == 0:
            self.saisie_txt1.turn_off()
        else:
            self.saisie_txt2.turn_off()

    def do_focus1(self):
        if self.focus == 1:
            return
        self.focus = 1
        self.saisie_txt1.no_focus()
        self.saisie_txt1.turn_off()
        self.saisie_txt2.focus()
        self.saisie_txt2.turn_on()
        self._ref_mod.set_focus_pwd()

    def do_focus0(self):
        if self.focus == 0:
            return
        self.focus = 0
        self.saisie_txt1.focus()
        self.saisie_txt1.turn_on()
        self.saisie_txt2.no_focus()
        self.saisie_txt2.turn_off()
        self._ref_mod.set_focus_login()

    def draw_content(self, screen):
        screen.fill(self.bgcolor)
        for e in self._etiquettes:
            screen.blit(e.img, e.pos)

        # - dessin boutons & widgets
        for b in self._buttons:
            screen.blit(b.image, b.position)
        screen.blit(self.saisie_txt1.image, self.saisie_txt1.position)
        screen.blit(self.saisie_txt2.image, self.saisie_txt2.position)

        if self._fin_aff_flottant is not None:
            t = time.time()
            if t > self._fin_aff_flottant:
                self._fin_aff_flottant = None
            else:
                screen.blit(self._err_etiquette.img, self._err_etiquette.pos)

    # ---
    #  GESTION EV.
    # --- ---
    def on_paint(self, ev):
        self.draw_content(ev.screen)

    def proc_event(self, ev, source):
        if ev.type == MyEvTypes.LoginModUpdate:

            if (ev.login == '') and (ev.pwd == ''):  # in case of reset
                self.saisie_txt1.move_caret('home')
                while self.saisie_txt1.get_disp_text() != '':
                    self.saisie_txt1.delete_char()
                self.saisie_txt2.move_caret('home')
                while self.saisie_txt2.get_disp_text() != '':
                    self.saisie_txt2.delete_char()
                self.do_focus0()
                self.saisie_txt1.render_field()
                self.saisie_txt2.render_field()

            else:
                pass  # TODO better model>view communication?

        elif ev.type == pygame.MOUSEBUTTONDOWN:
            if self.saisie_txt2.contains(ev.pos):
                    self.do_focus1()
            elif self.saisie_txt1.contains(ev.pos):
                    self.do_focus0()

        elif ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_TAB:
                if self.focus == 0:
                    self.do_focus1()
                else:
                    self.do_focus0()

            elif ev.key == pygame.K_RETURN or ev.key == pygame.K_KP_ENTER:
                LoginView.confirm_routine()

    # - MÉTIER
    def signal_bad_auth(self):
        self._fin_aff_flottant = time.time() + self.ERR_MSG_DELAY


class LoginCtrl(EventReceiver):
    """
    gère la procédure d'authentification (issues: réussite / échec)
    """

    def __init__(self, ref_mod, ref_view):
        super().__init__()
        self.ref_mod = ref_mod
        self.ref_view = ref_view

    def proc_event(self, ev, source):
        if ev.type == pygame.KEYDOWN:
            self._traitement_touche(ev)

        elif ev.type == MyEvTypes.TrigValidCredentials:
            if self.try_auth_server():
                self.pev(EngineEvTypes.CHANGESTATE, state_ident=glvars.GameStates.TaxPayment)
            else:
                self.ref_view.signal_bad_auth()  # gestion refus -> affichage msg erreur.
                self.ref_mod.reset_fields()

        elif ev.type == pygame.QUIT:
            self.pev(EngineEvTypes.POPSTATE)

    def _traitement_touche(self, ev):
        if ev.key == pygame.K_RETURN or ev.key == pygame.K_KP_ENTER:
            return

        if ev.key == pygame.K_BACKSPACE:
            self.ref_mod.suppr_lettre()
            return

        if ev.key == pygame.K_TAB:
            return  # sert à ignorer caractères TAB ds la saisie

        if ev.key == pygame.K_ESCAPE:
            self.pev(EngineEvTypes.POPSTATE)
            return

        self.ref_mod.ajoute_lettre(ev.unicode)  # sinon, on envoie la lettre à traiter au modèle

    # - MÉTIER
    def try_auth_server(self):
        uname = self.ref_mod.curr_login

        serv = HttpServer.instance()
        target = serv.get_gtm_app_url() + 'do_auth.php?webmode=0'
        dico_params = {
            'username': uname,
            'password': self.ref_mod.curr_pwd
        }

        res = serv.proxied_post(target, dico_params)
        tmp = json.loads(res)

        if (tmp is None) or (not tmp[0]):
            return False
        # exec. ici => login raté
        glvars.nom_utilisateur = uname
        glvars.id_perso = tmp[1]

        target = serv.get_gtm_app_url() + 'maj_solde.php'
        params = {
            'id_perso': glvars.id_perso,
            'updating': 0
        }
        res = serv.proxied_get(target, params)
        tmp = json.loads(res)
        if tmp is None:
            print('WARNING: cannot retrieve players balance!')
            return False
        # enregistrement valeur lue
        solde_gp = int(tmp)

        self.pev(MyEvTypes.PlayerLogsIn, username=uname, solde=solde_gp)
        glvars.username = uname
        glvars.copie_solde = solde_gp
        return True

    @staticmethod
    def persister_login_mdp(l_soumis, p_soumis):
        print('warning appel à persister_login_mdp(...) qui est un mockup')
        return
        # ud = LocalStorage.instance()
        # ud.set_val('stored_username', l_soumis)
        # ud.set_val('stored_pwd', p_soumis)

    def change_pwd_checkbox(self):
        tmp = self.ref_mod.change_pwd_save()
        self.ref_view.change_save_pwd(tmp)

    def change_lang(self, lang):
        print('warning appel à change_lang(...) qui est un mockup')
        return
        # ud = LocalStorage.instance()
        # ud.set_val('lang', lang)

    #def go_submit_cred(self):

        #essaye de s'authentifier auprès du serveur (LegacyApp) avec ce qui ns a été fourni
        #:return: soit None, si échec authentification, soit instance de LegacyAppAuthConnection

        # cfg = ConfigReseau.instance()
        # cfg.renseigneLoginPwd((self.curr_login, self.curr_pwd))
        # try:
        #    tmp = LegacyAppAuthConnection.instance()
        #    return tmp
        # except Exception:
        #    return None

        # tmp = ConnexionSurTl(
        #     settings.BASEURL2,
        #     self.curr_login,
        #     self.curr_pwd
        # )

        # self._manager.post(
        #    SubmitUserCred(self.ref_mod.curr_login, self.ref_mod.curr_pwd)
        # )

        # TODO persister Mdp que si lutilisateur le demande !
        # TODO remettre la case à cocher permettant de le spécifier
        # l_soumis = self.ref_mod.curr_login
        # p_soumis = self.ref_mod.curr_pwd
        #
        # self.game_serv = GameServer.instance()
        # cred_ok, id_av_recu = self.game_serv.legacy_app_auth(
        #     l_soumis,
        #     p_soumis
        # )
        #
        # if not cred_ok:  # vérification en restant dans le mode ecran_login
        #     print('server: access denied. Check your login, password.')
        #     self.ref_view.affiche_erreur(True)
        #     return
        #
        # # -- on sait que le login est faisable...
        # if not self.ref_mod.get_save_pwd():
        #     p_soumis = ''
        # LoginCtrl.persister_login_mdp(l_soumis, p_soumis)  # ecriture username [, password] sur le disque
        #
        # # avatar_id a déjà été enregistré ds les var. globales
        # # -- on passe dans le mode Loading
        # self._manager.post(
        #     UnitedEvent(Dingus2EvTypes.CHANGESTATE, state_ident=ST_LOADING)
        # )


class LoginState(BaseGameState):

    def __init__(self, gs_id, name):
        super().__init__(gs_id, name)
        self.m = self.v = self.c = None

    def enter(self):
        self.m = LoginModel()
        self.v = LoginView(self.m, glvars.colors['c_lightpurple'], glvars.colors['c_purple'])
        self.c = LoginCtrl(self.m, self.v)
        self.resume()

    def release(self):
        self.pause()
        self.m = self.v = self.c = None

    def pause(self):
        self.c.turn_off()
        self.v.turn_off()

    def resume(self):
        self.v.turn_on()
        self.c.turn_on()
