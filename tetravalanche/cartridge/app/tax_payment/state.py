import random
import glvars
from ev_types import MyEvTypes
from katagames_sdk.engine import BaseGameState, EventReceiver, EngineEvTypes
from labels import Labels
from loctexts import tsl
import katagames_sdk.engine as kataen


pygame = kataen.import_pygame()


class TaxPaymentCtrl(EventReceiver):

    def __init__(self):
        super().__init__()
        self.t0 = None

        self.duree_tot = random.uniform(0.2, 1.0)  # sec
        self._percentage = 0
        self.ready_to_exit = False

    def proc_event(self, ev, source):
        if ev.type == EngineEvTypes.LOGICUPDATE:
          
            if glvars.SKIP_MINING:
              self.pev(EngineEvTypes.POPSTATE)
              return
            
            if self.t0 is None:
                self.t0 = ev.curr_t
                return

            # calcul pourcentage ici même
            d = ev.curr_t - self.t0

            if d > self.duree_tot:
                self.pev(EngineEvTypes.POPSTATE)
                return

            ratio = d / self.duree_tot
            p = round(ratio*100)

            if self._percentage != p:
                self._percentage = p
                self.pev(MyEvTypes.LoadingBarMoves, value=p)


class TaxPaymentView(EventReceiver):

    BG_COLOR = glvars.colors['c_purple']
    TXT_COLOR_HL = glvars.colors['c_leafgreen']  # (217, 25, 84)
    TXT_COLOR = glvars.colors['c_lightpurple']  # (110, 80, 90)

    BARRE_M_SIZE = (590, 34)
    PADDING_BARRE_M = 8
    BARRE_M_FOND_COLOR = (160, 160, 160)
    BARRE_M_COLOR = TXT_COLOR_HL

    def __init__(self):
        super().__init__()
        pt_central = (400, 280)

        # src = 'assets/mining_btc.png'
        self.img_crypto_cartoon = pyv.vars.images['mining_btc']

        self._pos_img_crypto = list(pt_central)
        self._pos_img_crypto[0] -= self.img_crypto_cartoon.get_size()[0] // 2
        self._pos_img_crypto[1] -= self.img_crypto_cartoon.get_size()[1] // 2
        self._pos_img_crypto[1] -= 100

        # prépa éléments barre minage
        temp = pygame.Rect((0, 0), self.BARRE_M_SIZE).inflate(self.PADDING_BARRE_M, self.PADDING_BARRE_M)
        self._fond_minage = pygame.Surface(temp.size).convert()
        self._fond_minage.fill(self.BARRE_M_FOND_COLOR)
        self._pos_fond_minage = list(pt_central)
        self._pos_fond_minage[0] -= self._fond_minage.get_size()[0] // 2
        self._pos_fond_minage[1] -= self._fond_minage.get_size()[1] // 2
        self._pos_fond_minage[1] += 55

        self._barre_minage = None
        self._pos_barre_minage = list(self._pos_fond_minage)
        self._pos_barre_minage[0] += self.PADDING_BARRE_M // 2
        self._pos_barre_minage[1] += self.PADDING_BARRE_M // 2
        self._maj_barre_minage(0)

        # prépa. image titre
        self._pos_titre = list(pt_central)
        self._hugefont = glvars.fonts['moderne_big']
        self.etq_titre = self._hugefont.render(tsl(Labels.Minage1), True, self.TXT_COLOR_HL)
        self._pos_titre[0] -= self.etq_titre.get_size()[0] // 2
        self._pos_titre[1] -= self.etq_titre.get_size()[1] // 2
        self._pos_titre[1] += 128

        # prépa. image sous-titre
        self._pos_waitmsg = list(pt_central)
        self._hugefont = glvars.fonts['moderne']
        self.etq_waitmsg = self._hugefont.render(tsl(Labels.Minage2), True, self.TXT_COLOR)
        self._pos_waitmsg[0] -= self.etq_waitmsg.get_size()[0] // 2
        self._pos_waitmsg[1] -= self.etq_waitmsg.get_size()[1] // 2
        self._pos_waitmsg[1] += 165

    def _maj_barre_minage(self, val):
        # print('maj ********** {}'.format(val))
        longueur_estimee = self.BARRE_M_SIZE[0] * (val / 100)
        taille_barre = (int(longueur_estimee), self.BARRE_M_SIZE[1])
        temp = pygame.Rect((0, 0), taille_barre)
        self._barre_minage = pygame.Surface(temp.size).convert()
        self._barre_minage.fill(self.BARRE_M_COLOR)

    def proc_event(self, ev, source):
        if ev.type == EngineEvTypes.PAINT:
            self.draw_content(ev.screen)
        elif ev.type == MyEvTypes.LoadingBarMoves:
            self._maj_barre_minage(ev.value)

    def draw_content(self, screen):
        screen.fill(self.BG_COLOR)
        # affichage centré
        screen.blit(self.img_crypto_cartoon, self._pos_img_crypto)

        # dessin barre minage
        screen.blit(self._fond_minage, self._pos_fond_minage)
        screen.blit(self._barre_minage, self._pos_barre_minage)

        # - dessin textes
        screen.blit(self.etq_titre, self._pos_titre)
        screen.blit(self.etq_waitmsg, self._pos_waitmsg)


class TaxPaymentState(BaseGameState):
    def __init__(self, gs_id, name):
        super().__init__(gs_id, name)
        self.v = self.c = None

    def enter(self):
        self.v = TaxPaymentView()
        self.v.turn_on()
        self.c = TaxPaymentCtrl()
        self.c.turn_on()

    def release(self):
        self.v.turn_off()
        self.c.turn_off()
