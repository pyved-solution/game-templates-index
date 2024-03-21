from . import glvars
from . import pimodules


# aliases
pyv = pimodules.pyved_engine
pygame = pyv.pygame
EngineEvTypes = pyv.EngineEvTypes
Button = pyv.gui.Button2
netw = pimodules.network

# glvars
was_sent = False

# - contsants
BGCOLOR = 'antiquewhite3'


def proc_start():
    global was_sent
    if not was_sent:  # here to avoid nasty bug in web ctx (march 24)
        print('debug: trigger push state')
        pyv.get_ev_manager().post(EngineEvTypes.StatePush, state_ident=glvars.MyGameStates.CompeteNow)
        was_sent = True


class IntroCompo(pyv.EvListener):
    """
    main component for this game state
    """

    # def _update_playertypes(self):
    #     chdefs.pltype1 = chdefs.OMEGA_PL_TYPES[self.idx_pl1]
    #     chdefs.pltype2 = chdefs.OMEGA_PL_TYPES[self.idx_pl2]
    #     self.pltypes_labels[0].text = chdefs.pltype1
    #     self.pltypes_labels[1].text = chdefs.pltype2

    def _refresh_user_status(self):
        sh = pyv.get_surface().get_height()
        self.is_logged = not (netw.get_user_id() is None)
        if self.is_logged:
            self.user_infos = pyv.gui.Label(
                (32, -150+sh//2),
                'user_infos'+str(netw.get_user_infos(netw.get_user_id())),
                txt_size=32
            )

    def __init__(self):
        super().__init__()
        self.sent = False  # to avoid nasty bug in web ctx -> push event is triggered twice!

        # model
        self.idx_pl1 = 0
        self.idx_pl2 = 0
        self.active_buttons = False

        # - view
        self.large_ft = pygame.font.Font(None, 60)

        # LABELS / signature is:
        # (position, text, txtsize=35, color=None, anchoring=ANCHOR_LEFT, debugmode=False)
        sw, sh = pyv.get_surface().get_size()
        title = pyv.gui.Label(
            (-150 + (sw // 2), 100), 'fast Clicker demo', txt_size=40, anchoring=pyv.gui.ANCHOR_CENTER
        )
        title.textsize = 122
        title.color = 'darkblue'

        # TODO ajout d'autres labels permettant de voir auth status
        self.labels = [
            title,
        ]
        self.info_label = pyv.gui.Label((32, -128+sh//2), 'cannot start challenge if youre not auth', txt_size=32)

        self.user_infos = None
        self.is_logged = False
        self._refresh_user_status()

        self.pltypes_labels = [
            pyv.gui.Label((115, 145), 'unkno type p1', color='darkblue', txt_size=24),
            pyv.gui.Label((115, 205), 'unkno type p2', color='darkblue', txt_size=24),
        ]

        # self._update_playertypes()

        # - v: buttons
        # def rotatepl1():
        #     self.idx_pl1 = (self.idx_pl1 + 1) % len(chdefs.OMEGA_PL_TYPES)
        #     self._update_playertypes()
        #
        # def rotatepl2():
        #     self.idx_pl2 = (self.idx_pl2 + 1) % len(chdefs.OMEGA_PL_TYPES)
        #     self._update_playertypes()
        #
        # def rotleft_pl1():
        #     self.idx_pl1 = (self.idx_pl1 - 1)
        #     if self.idx_pl1 < 0:
        #         self.idx_pl1 = -1 + len(chdefs.OMEGA_PL_TYPES)
        #     self._update_playertypes()
        #
        # def rotleft_pl2():
        #     self.idx_pl2 = (self.idx_pl2 - 1)
        #     if self.idx_pl2 < 0:
        #         self.idx_pl2 = -1 + len(chdefs.OMEGA_PL_TYPES)
        #     self._update_playertypes()

        self.buttons = [
            Button(self.large_ft, 'Enter the challenge', (80, 333), callback=proc_start),
            # Button(None, ' > ', (128 + 200 + 25, 140), callback=rotatepl1),
            # Button(None, ' < ', (128 - 25 - 60, 140), callback=rotleft_pl1),
            # Button(None, ' > ', (128 + 200 + 25, 200), callback=rotatepl2),
            # Button(None, ' < ', (128 - 25 - 60, 200), callback=rotleft_pl2),
        ]
        for b in self.buttons:
            b.set_debug_flag()

    def turn_off(self):
        super().turn_off()
        for b in self.buttons:
            b.set_active(False)

    def on_update(self, ev):
        # lock buttons if not locgged
        if self.is_logged and not self.active_buttons:
            for b in self.buttons:
                b.set_active()
            self.active_buttons = True

    def on_paint(self, ev):
        ev.screen.fill(BGCOLOR)

        for lab in self.labels:
            lab.draw()
        if not self.is_logged:
            self.info_label.draw()
        if self.user_infos:
            self.user_infos.draw()

        for b in self.buttons:
            b.draw()

    def on_keydown(self, ev):
        if ev.key == pygame.K_ESCAPE:
            pyv.vars.gameover = True


class ChessintroState(pyv.BaseGameState):
    """
    Goal : that game state will show 1 out of 3 infos:
    - user not auth, you need to auth
    - user auth + CR balance + your best score so far <+> You cannot try again
    - user auth + CR balance + your best score so far <+> Trying will cost you xx CR, click to continue
    """

    def __init__(self, ident):
        super().__init__(ident)
        self.icompo = None

    def enter(self):
        self.icompo = IntroCompo()
        self.icompo.turn_on()

    def resume(self):
        global was_sent
        was_sent = False
        self.icompo.turn_on()

    def release(self):
        self.icompo.turn_off()

    def pause(self):
        self.icompo.turn_off()
