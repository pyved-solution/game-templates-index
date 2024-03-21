from . import chdefs
from . import glvars
from . import pimodules


pyv = pimodules.pyved_engine
# TODO activation
# netw = pimodules.network

# - alias
pygame = pyv.pygame
EngineEvTypes = pyv.EngineEvTypes
Button = pyv.gui.Button2

# - contsants
BGCOLOR = 'antiquewhite3'


def proc_start():
    pyv.get_ev_manager().post(EngineEvTypes.StatePush, state_ident=glvars.MyGameStates.Chessmatch)


class IntroCompo(pyv.EvListener):
    """
    main component for this game state
    """

    def _update_playertypes(self):
        chdefs.pltype1 = chdefs.OMEGA_PL_TYPES[self.idx_pl1]
        chdefs.pltype2 = chdefs.OMEGA_PL_TYPES[self.idx_pl2]
        self.pltypes_labels[0].text = chdefs.pltype1
        self.pltypes_labels[1].text = chdefs.pltype2

    def __init__(self):
        super().__init__()

        # model
        self.idx_pl1 = 0
        self.idx_pl2 = 0

        # - v: labels
        # current sig is:
        # (position, text, txtsize=35, color=None, anchoring=ANCHOR_LEFT, debugmode=False)
        sw = pyv.get_surface().get_width()
        self.title = pyv.gui.Label(
            (-150 + (sw // 2), 100), 'The game of chess', txt_size=41, anchoring=pyv.gui.ANCHOR_CENTER
        )
        self.title.textsize = 122
        self.title.color = 'brown'

        self.pltypes_labels = [
            pyv.gui.Label((115, 145), 'unkno type p1', color='darkblue', txt_size=24),
            pyv.gui.Label((115, 205), 'unkno type p2', color='darkblue', txt_size=24),
        ]
        self._update_playertypes()

        # - v: buttons
        def rotatepl1():
            self.idx_pl1 = (self.idx_pl1 + 1) % len(chdefs.OMEGA_PL_TYPES)
            self._update_playertypes()

        def rotatepl2():
            self.idx_pl2 = (self.idx_pl2 + 1) % len(chdefs.OMEGA_PL_TYPES)
            self._update_playertypes()

        def rotleft_pl1():
            self.idx_pl1 = (self.idx_pl1 - 1)
            if self.idx_pl1 < 0:
                self.idx_pl1 = -1 + len(chdefs.OMEGA_PL_TYPES)
            self._update_playertypes()

        def rotleft_pl2():
            self.idx_pl2 = (self.idx_pl2 - 1)
            if self.idx_pl2 < 0:
                self.idx_pl2 = -1 + len(chdefs.OMEGA_PL_TYPES)
            self._update_playertypes()

        self.buttons = [
            Button(None, 'Start Chessmatch', (128, 256), callback=proc_start),
            Button(None, ' > ', (128 + 200 + 25, 140), callback=rotatepl1),
            Button(None, ' < ', (128 - 25 - 60, 140), callback=rotleft_pl1),
            Button(None, ' > ', (128 + 200 + 25, 200), callback=rotatepl2),
            Button(None, ' < ', (128 - 25 - 60, 200), callback=rotleft_pl2),
        ]

        for b in self.buttons:
            b.set_debug_flag()

    def turn_on(self):
        super().turn_on()
        for b in self.buttons:
            b.set_active()

    def turn_off(self):
        super().turn_off()
        for b in self.buttons:
            b.set_active(False)

    def on_paint(self, ev):
        ev.screen.fill('orange')

        # self.title.draw()
        # for lab in self.pltypes_labels:
        #     lab.draw()
        # for b in self.buttons:
        #     b.draw()

    def on_keydown(self, ev):
        if ev.key == pygame.K_ESCAPE:
            pyv.vars.gameover = True

    def on_mousedown(self, ev):
        pyv.get_ev_manager().post(EngineEvTypes.StatePush, state_ident=glvars.MyGameStates.Chessmatch)


class CompeteComponent(pyv.EvListener):
    """
    main component for this game state
    """
    WAIT_DELAY = 1.33  # sec
    CHALL_DURATION = 5  # sec

    def __init__(self):
        super().__init__()
        self.nb_clicks = 0
        self.ft = pygame.font.Font(None, 45)
        self.ft2 = pygame.font.Font(None, 64)
        self.label = self.ft.render('get ready!', False, 'royalblue')
        self.waiting_phase = True

        self.prev_t = None
        self.mouse_b_pressed_flag = False

        self.counter = 0
        self.label_counter = None
        self._refresh_counter()

        self.label_chrono = None
        self._refresh_chrono(CompeteComponent.CHALL_DURATION)
        self.competiting = False

        self.reassuring_msg = None

    def _refresh_counter(self):
        self.label_counter = self.ft2.render(str(self.counter), False, 'red')

    def _refresh_chrono(self, value):
        self.label_chrono = self.ft2.render('remaining time: {:.2f}s'.format(value), False, 'darkred')

    def on_paint(self, ev):
        POS = (32, 32)
        CPOS = (32, 256)
        ev.screen.fill('darkgray')
        if self.waiting_phase:
            ev.screen.blit(self.label, POS)

        else:
            ev.screen.blit(self.label_counter, POS)
            ev.screen.blit(self.label_chrono, CPOS)

            if self.reassuring_msg:
                ev.screen.blit(self.reassuring_msg, (CPOS[0], CPOS[1]+96))

    def on_update(self, ev):
        if self.prev_t is None:
            self.prev_t = ev.curr_t
            return

        if self.waiting_phase:
            if ev.curr_t - self.prev_t > CompeteComponent.WAIT_DELAY:
                self.waiting_phase = False
                self.prev_t = ev.curr_t  # déclenchement chrono
                self.competiting = True

        elif self.competiting:
            elapsed = ev.curr_t - self.prev_t
            remains = CompeteComponent.CHALL_DURATION - elapsed
            if remains <= 0.0:
                self._refresh_chrono(0.0)

                print('Game over!')
                print()
                self.competiting = False

                score = self.counter
                self.reassuring_msg = self.ft.render(f"Final score: {score} was automatically pushed to the server",
                                                     False, 'royalblue')
                # TODO
                # netw.pay_challenge(glvars.stored_jwt)

            else:
                self._refresh_chrono(remains)

    def on_mousedown(self, ev):
        if not self.mouse_b_pressed_flag and self.competiting:
            self.counter += 1
            self._refresh_counter()
            self.mouse_b_pressed_flag = True

    def on_mouseup(self, ev):
        self.mouse_b_pressed_flag = False

    def on_keydown(self, ev):
        if ev.key == pygame.K_ESCAPE:
            self.pev(pyv.EngineEvTypes.StatePop)


class CompeteState(pyv.BaseGameState):

    def __init__(self, ident):
        super().__init__(ident)
        self.compo = CompeteComponent()

    def enter(self):
        self.compo.turn_on()
        print('entered in a new game state!')

    def release(self):
        self.compo.turn_off()
        print('exit the game state: compete')
