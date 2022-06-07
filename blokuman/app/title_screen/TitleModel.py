import glvars
import katagames_sdk.capsule.event as kevent
import katagames_sdk.engine as kataen
from ev_types import MyEvTypes
from katagames_sdk.engine import CogObject
from labels import Labels
from loctexts import tsl


pygame = kataen.import_pygame()


class TitleModel(CogObject):
    """
    stocke l'info. si le joueur est connecté ou nom
    """
    COUT_PARTIE = 10

    BINF_CHOIX = 134
    CHOIX_LOGIN, CHOIX_START, CHOIX_CRED, CHOIX_QUIT = range(BINF_CHOIX, BINF_CHOIX + 4)

    def __init__(self):
        super().__init__()
        self.is_real_login = True
        self._curr_choice = self.CHOIX_LOGIN
        self._logged_in = False

    def reset(self):
        self._logged_in = False

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

    def force_fakelogin(self):
        glvars.solde_gp = 10
        glvars.username = 'ghost'
        kevent.EventManager.instance().post(
            kevent.CgmEvent(MyEvTypes.BalanceChanges, value=10)
        )
        self.is_real_login = False

    def is_logged(self):
        return glvars.username is not None

    def mark_auth_done(self, solde_gp):
        self._logged_in = True
        glvars.solde_gp = solde_gp

    def can_bet(self):
        if not self._logged_in:
            return False
        if self.get_solde() is None:
            return False
        return self.get_solde() >= self.COUT_PARTIE

    def get_username(self):
        if not self.is_logged():
            return tsl(Labels.NomJoueurAnonyme)
        return glvars.username

    def set_solde(self, val):
        glvars.solde_gp = val
        kevent.EventManager.instance().post(
            kevent.CgmEvent(MyEvTypes.BalanceChanges, value=val)
        )

    def get_solde(self):
        if not self.is_logged():
            raise Exception('demande solde alors que _logged_in à False')
        return glvars.solde_gp
