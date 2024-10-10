import json

from .MenuView import MenuView
from ... import glvars
from ...glvars import pyv, netw
from ...ev_types import MyEvTypes


pygame = pyv.pygame


class MenuModel(pyv.Emitter):
    """
    stocke l'info. si le joueur est connecté ou nom
    """
    COUT_PARTIE = 10

    def __init__(self):
        super().__init__()
        self._curr_choice = None

    def reset_choice(self):
        if self.is_logged():
            self._curr_choice = glvars.ChoixMenu.StartChallenge
        else:
            self._curr_choice = glvars.ChoixMenu.DemoMode
        self.pev(MyEvTypes.ChoiceChanges, code=self._curr_choice)

    def get_curr_choice(self):
        return self._curr_choice

    def move(self, direction: int):
        # assert direction in (-1, +1)

        self._curr_choice += direction

        if glvars.ready_to_compete:
            if self._curr_choice == glvars.ChoixMenu.DemoMode:
                self._curr_choice += direction
        else:
            if self._curr_choice == glvars.ChoixMenu.StartChallenge:
                self._curr_choice += direction

        if self._curr_choice > glvars.ChoixMenu.last_code:
            self.reset_choice()
        elif self._curr_choice < 0:
            self._curr_choice = glvars.ChoixMenu.last_code

        # return
        # if not self.is_logged():
        #     if self._curr_choice == self.CHOIX_START:
        #         self._curr_choice += direction
        #     if self._curr_choice > self.CHOIX_QUIT:
        #         self._curr_choice = self.CHOIX_LOGIN
        #     elif self._curr_choice < self.CHOIX_LOGIN:
        #         self._curr_choice = self.CHOIX_QUIT
        #     self.pev(MyEvTypes.ChoiceChanges, code=self._curr_choice)
        #     return
        # # on est connecté
        # if self._curr_choice == self.CHOIX_LOGIN:
        #     self._curr_choice += direction
        # if self._curr_choice > self.CHOIX_QUIT:
        #     self._curr_choice = self.CHOIX_START
        # elif self._curr_choice < self.CHOIX_START:
        #     self._curr_choice = self.CHOIX_QUIT
        print('curr _choice ----> ', self._curr_choice)
        self.pev(MyEvTypes.ChoiceChanges, code=self._curr_choice)

    def is_logged(self):
        return glvars.username is not None

    def mark_auth_done(self, user, solde_gp):
        self._logged_in = True
        glvars.cr_balance = solde_gp
        glvars.username = user

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
            return 'Anonymous'
        return glvars.username

    def set_solde(self, val):
        glvars.cr_balance = val
        glvars.ev_manager.post(
            MyEvTypes.BalanceChanges, value=val
        )

    def get_solde(self):
        if not self.is_logged():
            raise Exception('demande solde alors que _logged_in à False')
        return glvars.cr_balance


class MenuCtrl(pyv.EvListener):
    POLLING_FREQ = 4  # sec. de délai entre deux appels serveur

    def __init__(self, mod, view):
        super().__init__()
        self.ref_mod = mod
        self.ref_view = view
        self.nextmode_buffer = None
        self.last_pol = None
        self.polling_mode = True

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
                if self.nextmode_buffer in (glvars.ChoixMenu.StartChallenge, glvars.ChoixMenu.DemoMode):
                    # can start without auth /with auth
                    if self.nextmode_buffer == glvars.ChoixMenu.StartChallenge:  # on etait log
                        self.pev(MyEvTypes.DemandeTournoi)

                    # je push state tetris
                    self.pev(pyv.EngineEvTypes.StatePush, state_ident=glvars.GameStates.Tetris)

                elif self.nextmode_buffer == glvars.ChoixMenu.QuitGame:
                    pyv.vars.gameover = True

                # reset du champ concerné
                self.nextmode_buffer = None
            return  # ---------------------------------------------------------------

        if self.ref_mod.is_logged():
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

    # event management
    def on_demande_tournoi(self, ev):
        # TODO vérif qu'on a utilisé aussi netw.can_pay_challenge qq part

        # TODO
        # meilleur gestion d'errerus si jamais le token_code n'es pas passé par le server pour une qq raison!
        tmp = netw.pay_challenge(glvars.stored_session, glvars.GAME_ID)
        if tmp['reply_code'] == 200:
            print('******* ok jai pu payer tournoi !  ****')
            glvars.chall_seed = netw.get_challenge_seed(glvars.GAME_ID)['challenge_seed']
            print('SEED ->', glvars.chall_seed)

        else:
            raise ValueError('when calling netw.pay_challenge, reply_code=', tmp['reply_code'])

        glvars.payment_token = tmp['token_code']

    # def proc_event(self, ev, source):
    #     if ev.type == MyEvTypes.DemandeTournoi:
    #         if self.ref_mod.can_bet() and self._procedure_debut_challenge():
    #             self.pev(EngineEvTypes.PUSHSTATE, state_ident=glvars.GameStates.Tetris)
    #         return  # ---------------------------------------------------------------------------

        # ------------- feature spéciale : faux login ----------
        # if glvars.DEV_MODE:
        #     if ev.type == PygameBridge.KEYDOWN:
        #         if ev.key == K_F10:
        #             self._logged_in = True
        #             self.polling_mode = False
        #             self.ref_mod.force_fakelogin()

    def _procedure_debut_challenge(self) -> bool:
        raise NotImplementedError
        # code below is kept as a reference
        # it is 100% deprecated in May 2024

        # :return: bool disant si oui ou non, la procédure s'est déroulé correctement

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

    def _recup_solde_serveur(self):  # new version (May 24)
        infos = netw.get_user_infos(glvars.user_id)
        # TODO error handling!!!
        # the returned infos are in the format:
        # {'reply_code': 200, 'message': '', 'username': 'Mickeys38', 'balance': 5991}
        return infos['balance']

    # def _recup_solde_serveur(self):
    #     if glvars.DEV_MODE:
    #         print('envoi serveur...')
    #     target = self.serv.get_gtm_app_url() + 'maj_solde.php'
    #     params = {
    #         'id_perso': glvars.id_perso,
    #         'updating': 0
    #     }
    #     res = self.serv.proxied_get(target, params)
    #     tmp = json.loads(res)
    #     if tmp is None:
    #         raise Exception('cannot retrieve players balance!')
    #     return int(tmp)

    def impacte_retour_login(self):
        if glvars.username:
            self.ref_mod.mark_auth_done(glvars.username, glvars.cr_balance)

            self.ref_view.refresh_graphic_state()
        if self.ref_mod.is_logged():
            print('Current rank of user:', netw.get_rank(glvars.user_id, glvars.GAME_ID))


class MenuState(pyv.BaseGameState):

    def __init__(self, gs_id):

        super().__init__(gs_id)  # , name)
        self.v = self.m = self.c = None
        self.der_lstate = None

    def enter(self):
        if self.m is None:
            self.m = MenuModel()

        # ----
        # mise à jour variables globales quant au statut auth/no-auth
        if netw.get_jwt() is None or netw.get_user_id() is None:
            pass
        else:
            # is auth --> hell, YEAH
            glvars.username = netw.get_username()
            glvars.stored_session = netw.get_jwt()
            glvars.user_id = netw.get_user_id()
            # Now, can i pay this challenge?
            glvars.ready_to_compete = netw.can_pay_challenge(
                glvars.stored_session,
                glvars.GAME_ID
            )

        self.m.reset_choice()
        self.v = MenuView(self.m)
        self.v.turn_on()

        if self.c is None:
            self.c = MenuCtrl(self.m, self.v)
        self.c.turn_on()

        glvars.init_sound()
        # we disabled for now, the music
        # glvars.playmusic()

    def resume(self):
        self.m.reset_choice()

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
