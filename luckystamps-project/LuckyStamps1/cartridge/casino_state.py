from json import JSONDecodeError

from . import pimodules
from .shared import MyEvTypes
from . import glvars
import json


pyv = pimodules.pyved_engine
EngineEvTypes = pyv.EngineEvTypes
netw = pimodules.network
pygame = pyv.pygame


class LuckyStamModel(pyv.Emitter):
    BOMB_CODE = -1
    BONUS_CODE = 0
    binfx, binfy = 100, 90
    starting_y = -176
    BLOCK_SPEED = 81  # how fast blocks move

    def __init__(self, serial, li_events=None):
        super().__init__()

        if li_events is not None:
            self.li_events = li_events
            self.li_gains = [0 for _ in range(7)]
        else:
            print('-' * 60)
            print('SERIAL RECEIVED:')
            print(serial)
            print('-' * 60)
            print()
            json_obj = json.loads(serial)
            self.li_events, self.li_gains = json_obj[0], json_obj[1]

        self.total_earnings = 0

        self.current_tirage = -1
        self.replayed_set = set()
        self.remainning_rounds = 3

        # tout ca pr gérer les animations
        self.allboxes = dict()
        self.anim_ended = dict()
        self.dangerous_columns = set()
        self.curr_box = None
        self.autoplay = False
        self.cursor = 0  # in the list of events

    def init_animation(self):
        # TODO solve the problem:
        # we have not detected the explosion properly,
        # that is: we only display the final result of the column,
        # the roll that contains the BOMB is never displayed

        if self.current_tirage in self.replayed_set:
            print('warning: trying to replay twice the same tirage!')
            return
        self.replayed_set.add(self.current_tirage)

        cls = self.__class__

        print('___replaying events, tirage:', self.current_tirage)

        # puts the cursor on the first event that matching the current round
        while self.cursor < len(self.li_events):
            e = self.li_events[self.cursor]
            if not (e[0] < self.current_tirage):
                break
            self.cursor += 1

        for k in range(5):
            e = self.li_events[self.cursor + k]
            # avant: (sans anim)
            # self.pev(MyEvTypes.ElementDrop, column=int(e[1][1]), elt_type=e[4])
            # self.pev(MyEvTypes.ElementDrop, column=int(e[1][1]), elt_type=e[3])
            # self.pev(MyEvTypes.ElementDrop, column=int(e[1][1]), elt_type=e[2])

            # avec anim
            # for c in range(5):
            #    for r in range(3):
            column_no = int(e[1][1])
            for row_no in range(3):
                key = f'c{column_no}r{row_no}'
                elt_type = e[2 + row_no]
                self.allboxes[key] = [
                    cls.binfx + column_no * 153,  # computing the position
                    cls.starting_y,
                    glvars.STAMPW, glvars.STAMPH,
                    elt_type
                ]
                if elt_type == cls.BOMB_CODE:
                    self.dangerous_columns.add(column_no)
        self.cursor += 5

        self.curr_box = 'c0r2'  # for animation
        self.autoplay = True

        if self.li_gains[self.current_tirage] != 0:
            self.total_earnings += self.li_gains[self.current_tirage]
            self.pev(MyEvTypes.EarningsUpdate, value=self.total_earnings)

    def select_next_box(self):
        # returns True if we can select another box to animate
        c = int(self.curr_box[1])
        n = int(self.curr_box[3])
        if n > 0:
            n -= 1
        else:
            n = 2
            c += 1

        self.curr_box = f'c{c}r{n}'
        if self.curr_box == 'c5r2':
            return False
        if self.curr_box in self.anim_ended:  # out of bounds or no anim
            return False
        return True

    def _increm_nb_turns_if_needed(self):
        # exit if we spot a single bomb
        for c in range(5):
            for n in range(3):
                key = f"c{c}r{n}"
                elt_type = self.allboxes[key][4]
                if elt_type == self.__class__.BOMB_CODE:
                    return
        for c in range(5):
            for n in range(3):
                key = f"c{c}r{n}"
                elt_type = self.allboxes[key][4]
                if elt_type == self.__class__.BONUS_CODE:  # if bonus and no bomb left, we increm rounds
                    self.remainning_rounds += 2
                    self.pev(MyEvTypes.ForceUpdateRounds, new_val=self.remainning_rounds)

    def update(self):
        cls = self.__class__
        if self.curr_box is None:
            return

        if self.curr_box not in self.anim_ended:
            self.allboxes[self.curr_box][1] += cls.BLOCK_SPEED
            n = int(self.curr_box[3])
            targety = cls.binfy + n * (glvars.STAMPH + 4) - 2

            if self.allboxes[self.curr_box][1] > targety:  # detection de "collision"
                self.allboxes[self.curr_box][1] = targety
                # passe à l'anim suivante
                self.anim_ended[self.curr_box] = True

                if not self.select_next_box():
                    # ok, animation has fully ended!
                    print('anim fully ended')
                    self.curr_box = None
                    self.autoplay = False
                    # we perform this check at the very end!
                    self._increm_nb_turns_if_needed()

    def get_rounds(self):
        return self.remainning_rounds

    # def next_step(self):
    #     # if bombs left -> go replace the adhoc column
    #     if self.nb_bombs > 0 and not self.autoplay:
    #         self.proc_bomb()

    def next_tirage(self):
        print('CALL NXT TIRAGE!')
        self.current_tirage += 1
        self.remainning_rounds -= 1
        # self.cursor = 0
        self.pev(MyEvTypes.ForceUpdateRounds, new_val=self.remainning_rounds)
        self.anim_ended.clear()
        self.pev(MyEvTypes.NewRound)

    def try_proc_bombs(self):
        if self.autoplay:
            raise ValueError('FATAL: That method shouldnt be called unless stamps movement is over!')

        if len(self.dangerous_columns) > 0:
            print('dangerous columns:', self.dangerous_columns)

            e = self.li_events[self.cursor]
            print('cursor==', self.cursor, e)
            print('boom, {} explodes!'.format(e[1]))
            self.cursor += 1
            column_no = int(e[1][1])
            self.dangerous_columns.remove(column_no)

            for row_no in range(3):
                key = f'c{column_no}r{row_no}'
                elt_type = e[2 + row_no]
                self.allboxes[key] = [
                    self.__class__.binfx + column_no * 153,  # computing the position
                    self.__class__.starting_y,
                    glvars.STAMPW, glvars.STAMPH,
                    elt_type
                ]
                if elt_type == self.__class__.BOMB_CODE:
                    self.dangerous_columns.add(column_no)

            # restore animations
            self.curr_box = 'c{}r2'.format(column_no)  # for animation
            for r in range(3):
                key = 'c{}r{}'.format(column_no, r)
                del self.anim_ended[key]
            self.autoplay = True


class LuckyStamView(pyv.EvListener):
    elt_type_to_imgname_mapping = {
        -1: 'lion',
        0: 'bonus-rolls',
        1: 'brightpink-prince',
        2: 'young-prince',
        3: 'rare-shilling',
        4: 'medaillon-queen',
        5: 'deepblue-queen',
        6: 'seven-pence',
        7: 'canada-orange',
    }

    # color_mapping = {
    #     1: THECOLORS['papayawhip'],
    #     2: THECOLORS['antiquewhite2'],
    #     3: THECOLORS['paleturquoise3'],
    #     4: THECOLORS['gray31'],
    #     5: THECOLORS['plum2'],
    #     6: THECOLORS['seagreen3'],
    #     7: THECOLORS['sienna1']
    # }

    # spr_sheet = pyv.gfx.JsonBasedSprSheet('cartes')
    def __init__(self, refmod):
        super().__init__()
        self.grid = [
            [None, None, None] for _ in range(5)
        ]
        self.line_idx_by_column = dict()
        for k in range(5):
            self.line_idx_by_column[k] = 2
        self.mod = refmod
        self.ft = pyv.pygame.font.Font(None, 22)

        self._label_rounds_cpt = None
        self.label_earnings = None
        self._refresh_cpt()
        self._refresh_earnings()

    def _refresh_cpt(self):
        self.label_rounds_cpt = self.ft.render(str(self.mod.get_rounds()), False, 'orange')

    def _refresh_earnings(self):
        self.label_earnings = self.ft.render('earings: {} credits'.format(self.mod.total_earnings), False, 'orange')

    def on_mousedown(self, ev):
        self.pev(MyEvTypes.GuiLaunchRound)

    def on_earnings_update(self, ev):
        print('call refresh earnings')
        self._refresh_earnings()

    def on_element_drop(self, ev):
        k = self.line_idx_by_column[ev.column]
        self.line_idx_by_column[ev.column] -= 1
        self.grid[ev.column][k] = ev.elt_type  # affectation

    def on_new_round(self, ev):
        # reset stack position
        for k in range(5):
            self.line_idx_by_column[k] = 2

    def on_force_update_rounds(self, ev):
        self._refresh_cpt()

    def on_paint(self, ev):
        ev.screen.fill(pyv.pal.japan['darkblue'])

        # -----------
        # paint grid
        # -----------
        binfx, binfy = 100, 88
        # for col_no in range(5):
        #     for row_no in range(3):
        #         a, b = col_no * 153 + binfx, row_no * 179 + binfy,
        #         r4infos = [a, b, STAMPW, STAMPH]
        #         cell_v = self.grid[col_no][row_no]
        #         if cell_v is None:
        #             pyv.draw_rect(ev.screen, pyv.pal.punk['darkblue'], r4infos, 1)
        #         elif 1 <= cell_v < 8:
        #             pyv.draw_rect(ev.screen, cls.color_mapping[cell_v], r4infos)
        #         elif cell_v == self.mod.BONUS_CODE:
        #             ev.screen.blit(pyv.vars.images['canada-orange'], r4infos[:2])

        # ------------
        # paint counter + earnings
        # ------------
        ev.screen.blit(self.label_rounds_cpt, (180, 64))
        ev.screen.blit(self.label_earnings, (400+180, 64))

        # ------------
        # paint falling blocks
        # ------------
        for k, blockinfos in self.mod.allboxes.items():
            elt_type = blockinfos[4]
            # if elt_type == self.mod.BOMB_CODE:
            #     pyv.draw_rect(ev.screen, 'red', blockinfos[:4])
            #
            # elif elt_type == self.mod.BONUS_CODE:
            #     pyv.draw_rect(ev.screen, 'black', blockinfos[:4])
            #
            # elif elt_type == 1:
            #     ev.screen.blit(
            #         pyv.vars.images['img/young-prince'],
            #         (blockinfos[0], blockinfos[1]))
            #
            # elif elt_type == 2:

            img = pyv.vars.images[self.__class__.elt_type_to_imgname_mapping[elt_type]]
            ev.screen.blit(img, (blockinfos[0], blockinfos[1]))

            # else:
            #     color = self.__class__.color_mapping[elt_type]
            #     pyv.draw_rect(ev.screen, color, blockinfos[:4])


# @pyv.declare_update
# def upd(time_info=None):
#     global replayed, my_mod
#     if shared.prev_time_info:
#         dt = (time_info - shared.prev_time_info)
#     else:
#         dt = 0
#     shared.prev_time_info = time_info
#     pyv.systems_proc(dt)
#     if not replayed:
#         replayed = True
#         my_mod.replay_ev()
#     pyv.flip()

# ------------------------------------
#  nah

# class EcsPatternWrapper(pyv.EvListener):
#     # we need to wrap the ECS this way, because right now (March 24)
#     # Ive got no idea of how to structure game states + ECS together
#     # in the future, we may find a much better way to handle this
#
#     def on_update(self, ev):
#         info_t = ev.curr_t
#
# def updatechess(info_t):
#     global ev_manager
#     ev_manager.post(pyv.EngineEvTypes.Update, curr_t=info_t)
#     ev_manager.post(pyv.EngineEvTypes.Paint, screen=gscreen)
#     ev_manager.update()
#     pyv.flip()


class LuckyStamController(pyv.EvListener):
    def __init__(self, mod):
        super().__init__()
        self.mod = mod

    def on_keydown(self, ev):
        global rez, auth_user_id, gl_user_session
        if ev.key == pygame.K_SPACE:
            print('dummy function get_version !!!')
            print(netw.get_version())
            print()

            print('What i do here, is basically retrieving the info if im Auth or NOT!!!')
            print()
            print('@' * 80)
            gs = glvars.TEST_GAME_ID
            print("jwt:", netw.get_jwt())
            print("username:", netw.get_username())

            # auth_user_id = DEFAULT_USER_ID if netw.get_user_id() is None else netw.get_user_id()
            auth_user_id = netw.get_user_id()

            print('NEW user_id that we will use: ', auth_user_id)
            print()

            print("fetched user_infos", netw.get_user_infos(auth_user_id))

            # for the dummy jwt, rather press L
            # print(
            #     f"TEST de can_pay_challenge (gameid {gs} user_id {auth_user_id} )",
            #     netw.can_pay_challenge(netw.get_jwt(), gs)
            # )
            # real jwt
            print('i plan to test netw with the REAL jwt')
            print('jwt:', gl_user_session)
            print(netw.can_pay_challenge(gl_user_session, glvars.TEST_GAME_ID))

        # elif ev.key == pygame.K_RETURN:
        #    print('get ready for chall payvent!')
        #    jwt = netw.get_jwt()
        #    rez = netw.pay_challenge(jwt, TEST_GAME_ID)
        #    print('after calling pay_challenge we have', rez)

        elif ev.key == pygame.K_BACKSPACE:
            print('<Trying to fake auth>')

            rez = netw.auth('fgamer1', 'bidonbidon')
            print(rez)
            gl_user_session = rez['jwt']
            auth_user_id = rez['user_id']
            print('new user id!! ', auth_user_id)
            # mytoken = 'faketoken'
            # print(msg_post_register = netw.register_score(mytoken, 3500))

        elif ev.key == pygame.K_v:
            print('detection du V!!!')  # getrank devrait etre testé aussi

        elif ev.key == pygame.K_l:
            print('faut avoir fait SPACE , et BACKSPACE ... avant !!!')
            print('>>peut payer?')
            # dummy jwt sur can_pay_challeng
            netw.can_pay_challenge(netw.get_jwt(), glvars.TEST_GAME_ID)

            print('>>go paiement')
            r = netw.pay_challenge(gl_user_session, glvars.TEST_GAME_ID)
            payment_token = r['tokenCode']

            # print('REGISTER SCORE')
            # score_val = glvars.DUMMY_SCORE
            # print(netw.register_score(payment_token, score_val))

            print('GET RANK')
            print(netw.get_rank(glvars.TEST_GAME_ID, auth_user_id))
            print('---------------')

        elif ev.key == pygame.K_x:
            # un peu ancien
            print('infos')
            print(netw.get_user_infos(auth_user_id))
            print('can pay p2e?')
            print(netw.can_pay_p2e(glvars.TEST_GAME_ID, auth_user_id, 5))

        elif ev.key == pygame.K_p:
            print('donation: du pay P2e sans rien recevoir en retour!')
            print(netw.pay_p2e(glvars.TEST_GAME_ID, auth_user_id, 5))
            print('---------------')

        elif ev.key == pygame.K_ESCAPE:
            self.pev(EngineEvTypes.StatePop)

        # elif ev.key == pygame.K_c:
        #     print('les trois der functions de l\'api CHALLENGE **************')
        #     print('PAY CHALL')
        #     json_obj_reply = netw.pay_challenge('jwt_for_real', TEST_GAME_ID)
        #     print(json_obj_reply)
        #     token = json_obj_reply['tokenCode']

    def on_gui_launch_round(self, ev):
        if not self.mod.autoplay:  # ignore re-roll if anim not ended
            if self.mod.get_rounds() > 0:
                self.mod.next_tirage()
                self.mod.init_animation()
            else:
                print('no round left')  # cant re-roll if no roond left!
        else:
            print('ctrl tries to re-roll but autoplay is still active')

    def on_element_drop(self, ev):
        print(ev.column, '-', ev.elt_type)

    def on_earnings_update(self, ev):
        print('[Ctrl] Detection: you will earn a total of {}'.format(ev.value))

    def on_quit(self, ev):
        pyv.vars.gameover = True

    def on_update(self, ev):
        self.mod.update()
        if not self.mod.autoplay:
            self.mod.try_proc_bombs()  # can pursue the animation!


class CasinoState(pyv.BaseGameState):
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
        # shared.screen = screen
        pyv.init(wcaption='Lucky Stamps: the game')

        # - fetch info depuis le serveur
        if glvars.forced_serial is None:
            print('-----> forced_serial est à None <-----')

            # the game host is provided by what can be read here "pyvm.kata.games/servers.json"
            game_server_infos = pimodules.network.get(
                'https://pyvm.kata.games', '/servers.json'  # note that it is HTTPS! All game are loaded via https in the pyvm
            ).to_json()['LuckyStamps1']

            target_game_host = game_server_infos['url']

            # we have to use .text on the result bc we wish to pass a raw Serial to the model class
            netw_reply = pimodules.network.get('', target_game_host, data={'jwt': glvars.stored_jwt})

            try:  # stop if error, stop right now as it will be easier to debug
                json.loads(netw_reply.text)
            except JSONDecodeError:
                raise ValueError('Error in decoding the JSON (reply) right after calling play.php')

            tirage_result = netw_reply.text
        else:
            print(' ** ]]]]]]]]]]]]] mode: forced serial activ **')
            tirage_result = glvars.forced_serial

        self.m = LuckyStamModel(tirage_result)
        self.v = LuckyStamView(self.m)
        self.c = LuckyStamController(self.m)
        self.v.turn_on()
        self.c.turn_on()

    def release(self):
        self.c.turn_off()
        self.v.turn_off()
        print('exit the casino state...')
