import glvars
import katagames_sdk.api as katapi
import katagames_engine as kataen
from app.title_screen.TitleModel import TitleModel
from defs import GameStates
from ev_types import MyEvTypes
# from katagames_sdk.capsule.event import CgmEvent  # TODO fix
# from katagames_sdk.capsule.networking.httpserver import HttpServer
# from katagames_sdk.engine import EngineEvTypes
# from katagames_sdk.engine import EventReceiver


pygame = kataen.import_pygame()
kengi = kataen
CgmEvent = kengi.event.CgmEvent
EngineEvTypes = kengi.event.EngineEvTypes


class MenuCtrl(kengi.event.EventReceiver):
    POLLING_FREQ = 4  # sec. de délai entre deux appels serveur

    def __init__(self, mod, view):
        super().__init__()
        self.ref_mod = mod
        self.ref_view = view

        # - prepa de quoi changer de mode de jeu...
        self.nextmode_buffer = None
        self._assoc_cchoix_event = {
            TitleModel.CHOIX_QUIT: None,  # géré via fonction aussi
            TitleModel.CHOIX_CRED: CgmEvent(EngineEvTypes.PUSHSTATE, state_ident=GameStates.Credits),
            TitleModel.CHOIX_START: None,  # celui-ci est géré via un evenement MyEvTypes.DemandeTournoi !
            TitleModel.CHOIX_LOGIN: CgmEvent(MyEvTypes.ChoiceChanges),  # CgmEvent(EngineEvTypes.PUSHSTATE, state_ident=GameStates.Login)
        }

        # - misc
        self.last_pol = None
        self.logged_in = mod.is_logged()
        self.polling_mode = True

        self.serv = None # TODO fix later, HttpServer.instance()

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
                if self.nextmode_buffer == TitleModel.CHOIX_START:
                    self.pev(MyEvTypes.DemandeTournoi)

                elif self.nextmode_buffer == TitleModel.CHOIX_QUIT:
                    if kataen.runs_in_web():
                        katapi.clear_local_session()
                        glvars.username = None
                        glvars.acc_id = None
                        self.ref_mod.reset()
                        self.logged_in = False
                        self.pause_polling()
                        self.ref_view.refresh_graphic_state()
                        print('*** RESET ok ***')
                    else:
                        self.pev(pygame.QUIT)
                else:
                    ev = self._assoc_cchoix_event[self.nextmode_buffer]
                    if ev is not None:
                        kataen.get_manager().post(ev)

                # reset du champ concerné
                self.nextmode_buffer = None

            return

        if self.logged_in:
            if not self.polling_mode:
                return
            if (self.last_pol is None) or (ev.curr_t - self.last_pol > self.POLLING_FREQ):
                self.last_pol = ev.curr_t
                nouv_solde = katapi.get_user_balance(glvars.acc_id)
                self.ref_mod.set_solde(nouv_solde)

    # --------------------------------------
    #  Gestion des évènements
    # --------------------------------------
    def proc_event(self, ev, source):
        if ev.type == EngineEvTypes.LOGICUPDATE:
            self.__handlelogic(ev)

        elif ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_UP:
                self.ref_mod.move(-1)

            elif ev.key == pygame.K_DOWN:
                self.ref_mod.move(1)

            elif ev.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.nextmode_buffer = self.ref_mod.get_curr_choice()
                self.ref_view.validate_effect()

        elif ev.type == MyEvTypes.DemandeTournoi:
            if self.ref_mod.can_bet():
                # toute la comm. réseau se passe bien ?
                katapi.set_curr_game_id(glvars.GAME_ID)
                payment_ok, numero_chall, chall_seed = katapi.pay_for_challenge(glvars.acc_id)
                cond1 = self.ref_mod.is_real_login and payment_ok
                glvars.num_challenge = numero_chall
                glvars.chall_seed = chall_seed
                if (not self.ref_mod.is_real_login) or cond1:
                    self.pev(EngineEvTypes.PUSHSTATE, state_ident=GameStates.Puzzle)
            else:
                print('cant bet says the ctrler')

    def impacte_retour_login(self):
        print('ds impacte_retour_login')
        if glvars.username:
            print('username has been set')
            self.ref_mod.mark_auth_done(glvars.copie_solde)
            self.logged_in = True
            self.ref_view.refresh_graphic_state()
            self.resume_polling()

