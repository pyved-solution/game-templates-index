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
        pyv.get_ev_manager().post(EngineEvTypes.StatePush, state_ident=glvars.MyGameStates.CasinoState)
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
        offset = 44
        sh = pyv.get_surface().get_height()
        if netw.get_jwt() is None or netw.get_user_id() is None:
            self.is_logged = False
        else:
            self.is_logged = True

        if not self.is_logged:
            self.labels[1] = pyv.gui.Label(
                (32, (1 * offset) - 250 + sh // 2),
                'user is not auth, please login before running that game',
                txt_size=32
            )
            return

        self.labels[1] = pyv.gui.Label(
            (32, (1*offset)-250+sh//2),
            'user_infos'+str(netw.get_user_infos(netw.get_user_id())),
            txt_size=32
        )

        if self.is_logged:
            tested_token = netw.get_jwt()
            rtest = netw.can_pay_game_fee(tested_token, glvars.GAME_PRICE)
            self.can_pay_flag = rtest['can_pay']  # forcing it to be equal to the return of can_pay_fee
            glvars.stored_jwt = tested_token
            print('can pay?? ', self.can_pay_flag)

        # --------
        # chall costs + wealth info
        # --------
        # tmp = netw.get_challenge_entry_price(glvars.GAME_ID)
        # challprice = tmp['entry_price']
        #
        # glvars.stored_jwt = netw.get_jwt()  # store the value that was used to check can_pay_challenge
        # rez = netw.can_pay_challenge(netw.get_jwt(), glvars.GAME_ID)
        # self.can_pay_flag = rez['can_pay']
        #
        # self.labels[2] = pyv.gui.Label(
        #     (32, (2*offset)-250+sh//2),
        #     f"chall costs {challprice} CR, " + ("you can pay" if self.can_pay_flag else "you CANT pay it now"),
        #     txt_size=24
        # )

        # ---------
        # TODO provide info if the user is too poor
        # ---------
        # result_getrank = netw.get_rank(netw.get_user_id(), glvars.GAME_ID)
        # if result_getrank['score'] is None:  # never played
        #     rankmessage = 'no score found, looks like youve never played'
        # else:
        #     a, b = result_getrank['score'], result_getrank['rank']
        #     rankmessage = f"your best score so far is {a}, current rank:{b}"
        # self.labels[3] = pyv.gui.Label(
        #     (32, (3*offset)-250+sh//2),
        #     rankmessage,
        #     txt_size=24
        # )

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
            (-150 + (sw // 2), 100), 'LUCKY STAMPS', txt_size=40, anchoring=pyv.gui.ANCHOR_CENTER
        )
        title.textsize = 122
        title.color = 'darkgreen'

        # tous les labels permettant de voir:
        #  titre jeu + info de statut user...
        self.labels = [
            # fixed rules:
            # 0-> title, 1-> user_infos, 2-> wealthinfo, 3-> current rank
            title,
            pyv.gui.Label((0, 0), '.', txt_size=8),
            pyv.gui.Label((16, 240), f"this game costs {glvars.GAME_PRICE} par play", txt_size=35),
            pyv.gui.Label((0, 0), '.', txt_size=8),
        ]
        self.info_label = pyv.gui.Label((32, -128+sh//2), 'cannot start challenge if youre not auth', txt_size=32)

        # to display user status
        self.is_logged = False
        self.can_pay_flag = False

        self._refresh_user_status()

        self.pltypes_labels = [
            pyv.gui.Label((115, 145), 'unkno type p1', color='darkblue', txt_size=24),
            pyv.gui.Label((115, 205), 'unkno type p2', color='darkblue', txt_size=24),
        ]

        self.buttons = [
            Button(self.large_ft, 'Play game (fees apply)', (80, 333), callback=proc_start),
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
        if not self.active_buttons:
            if self.is_logged and self.can_pay_flag:
                for b in self.buttons:
                    b.set_active()
                self.active_buttons = True

    def on_paint(self, ev):
        ev.screen.fill(BGCOLOR)

        for lab in self.labels:
            lab.draw()

        # if not self.is_logged:
        #     self.info_label.draw()
        # if self.user_infos:
        #     self.user_infos.draw()
        #     self.can_pay_chall_label.draw()

        wi_obj = self.buttons[0]
        tmp = pygame.Rect(wi_obj.collision_rect).inflate(4, 4)
        adhoc_color = 'green' if self.active_buttons else 'red'
        pygame.draw.rect(ev.screen, adhoc_color, tmp)
        wi_obj.draw()

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

        self.icompo = IntroCompo()  # lets reset the state, fully
        self.icompo.turn_on()

    def release(self):
        self.icompo.turn_off()

    def pause(self):
        self.icompo.turn_off()
