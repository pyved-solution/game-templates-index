import glvars
import katagames_sdk.engine as kataen
from katagames_sdk.engine import EngineEvTypes
from katagames_sdk.capsule import event as kevent


pygame = kataen.import_pygame()


class CreditsView(kevent.EventReceiver):
    def __init__(self):
        super().__init__()

        font = glvars.fonts['moderne']
        self.labels = list()
        for txt in (
                'prog. par thomas iwaszko', 'musique https://patrickdearteaga.com',
                '', 'visitez http://ludo.store', '', 'ECHAP pour revenir...'
        ):
            self.labels.append(
                font.render(txt, False, glvars.colors['c_lightpurple'])
            )

    def proc_event(self, ev, source):
        if ev.type == EngineEvTypes.PAINT:
            ev.screen.fill(glvars.colors['bgspe_color'])

            basey = 150
            midx = kataen.get_screen().get_width()//2
            offset = 33
            for k, etq in enumerate(self.labels):
                deltax = etq.get_size()[0]//2
                ev.screen.blit(etq, (midx-deltax, basey+k*offset))


class CreditsCtrl(kevent.EventReceiver):
    def proc_event(self, ev, source):
        if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
            self.pev(EngineEvTypes.POPSTATE)


class CreditsState(kataen.BaseGameState):
    def __init__(self, state_ident, state_name):
        super().__init__(state_ident, state_name)
        self.v = self.c = None

    def enter(self):
        self.v = CreditsView()
        self.c = CreditsCtrl()
        for compo in (self.v, self.c):
            compo.turn_on()

    def release(self):
        for compo in (self.c, self.v):
            compo.turn_off()
        self.v = self.c = None
