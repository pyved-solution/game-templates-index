# from . import pimodules
from . import shared
from . import systems
from .world import blocks_create, player_create, ball_create
import json
# import pyved_engine as pyv
import requests
from . import pimodules


pyv = pimodules.pyved_engine


THECOLORS = pyv.pygame.color.THECOLORS

MyEvTypes = pyv.game_events_enum((
    'ElementDrop',  # contient column_idx et elt_type
    'Earnings',  # contient value
    'NewRound',
    'GuiLaunchRound',
    'ForceUpdateRounds',  # contient new_val
    # 'BombExplodes'
))

# pyv = pimodules.pyved_engine
pygame = pyv.pygame
my_mod = None
ev_manager = None
gscreen = None
replayed = False

# ------------------
# taille (px) attendue pour les <stamps> img = 149x175
# ------------------
STAMPW, STAMPH = 149, 175


class LsGameModel(pyv.Emitter):
    BOMB_CODE = -1
    BONUS_CODE = 0
    binfx, binfy = 100, 88
    BLOCK_SPEED = 32

    def __init__(self, serial):
        super().__init__()
        print('-'*60)
        print('SERIAL RECEIVED:')
        print(serial)
        print('-' * 60)
        print()

        self.li_events, self.li_gains = json.loads(serial)
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
            if not(e[0] < self.current_tirage):
                break
            self.cursor += 1

        for k in range(5):
            e = self.li_events[self.cursor+k]
            # avant: (sans anim)
            # self.pev(MyEvTypes.ElementDrop, column=int(e[1][1]), elt_type=e[4])
            # self.pev(MyEvTypes.ElementDrop, column=int(e[1][1]), elt_type=e[3])
            # self.pev(MyEvTypes.ElementDrop, column=int(e[1][1]), elt_type=e[2])
            if e[4] == cls.BONUS_CODE or e[3] == cls.BONUS_CODE or e[2] == cls.BONUS_CODE:
                self.remainning_rounds += 2
            self.pev(MyEvTypes.ForceUpdateRounds, new_val=self.remainning_rounds)
            # avec anim
            # for c in range(5):
            #    for r in range(3):
            column_no = int(e[1][1])
            for row_no in range(3):
                key = f'c{column_no}r{row_no}'
                elt_type = e[2+row_no]
                self.allboxes[key] = [
                    cls.binfx + column_no * 153,  # computing the position
                    -200,
                    STAMPW, STAMPH,
                    elt_type
                ]
                if elt_type == cls.BOMB_CODE:
                    self.dangerous_columns.add(column_no)
        self.cursor += 5

        self.curr_box = 'c0r2'  # for animation
        self.autoplay = True

        self.pev(MyEvTypes.Earnings, value=self.li_gains[self.current_tirage])

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

    def update(self):
        cls = self.__class__
        if self.curr_box is None:
            return

        if self.curr_box not in self.anim_ended:
            self.allboxes[self.curr_box][1] += cls.BLOCK_SPEED
            n = int(self.curr_box[3])
            targety = cls.binfy + n * (STAMPH+4)

            if self.allboxes[self.curr_box][1] > targety:  # detection de "collision"
                self.allboxes[self.curr_box][1] = targety
                # passe à l'anim suivante
                self.anim_ended[self.curr_box] = True

                if not self.select_next_box():
                    self.curr_box = None
                    self.autoplay = False

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
                    -200,
                    STAMPW, STAMPH,
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


class MyController(pyv.EvListener):
    def __init__(self, mod):
        super().__init__()
        self.mod = mod

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

    def on_earnings(self, ev):
        print('congrats! You have earned:', ev.value)

    def on_update(self, ev):
        self.mod.update()
        if not self.mod.autoplay:
            self.mod.try_proc_bombs()  # can pursue the animation!


class LsView(pyv.EvListener):
    color_mapping = {
        1: THECOLORS['papayawhip'],
        2: THECOLORS['antiquewhite2'],
        3: THECOLORS['paleturquoise3'],
        4: THECOLORS['gray31'],
        5: THECOLORS['plum2'],
        6: THECOLORS['seagreen3'],
        7: THECOLORS['sienna1']
    }

    # spr_sheet = pyv.gfx.JsonBasedSprSheet('cartes')
    def __init__(self, refmod: LsGameModel):
        super().__init__()
        self.grid = [
            [None, None, None] for _ in range(5)
        ]
        self.line_idx_by_column = dict()
        for k in range(5):
            self.line_idx_by_column[k] = 2
        self.mod = refmod
        self.ft = pyv.pygame.font.Font(None, 22)
        self.label_rounds_cpt = self.ft.render(str(refmod.get_rounds()), False, 'orange')

    def on_mousedown(self, ev):
        self.pev(MyEvTypes.GuiLaunchRound)

    def on_element_drop(self, ev):
        k = self.line_idx_by_column[ev.column]
        self.line_idx_by_column[ev.column] -= 1
        self.grid[ev.column][k] = ev.elt_type  # affectation

    def on_new_round(self, ev):
        # reset stack position
        for k in range(5):
            self.line_idx_by_column[k] = 2

    def on_force_update_rounds(self, ev):
        self.label_rounds_cpt = self.ft.render(str(ev.new_val), False, 'orange')

    def on_paint(self, ev):
        cls = __class__
        ev.screen.fill(pyv.pal.c64['blue'])

        # -----------
        # paint grid
        # -----------
        binfx, binfy = 100, 88
        for col_no in range(5):
            for row_no in range(3):
                a, b = col_no * 153 + binfx, row_no * 179 + binfy,
                r4infos = [a, b, STAMPW, STAMPH]
                cell_v = self.grid[col_no][row_no]
                if cell_v is None:
                    pyv.draw_rect(ev.screen, 'red', r4infos, 1)
                elif 1 <= cell_v < 8:
                    pyv.draw_rect(ev.screen, cls.color_mapping[cell_v], r4infos)
                elif cell_v == self.mod.BONUS_CODE:
                    ev.screen.blit(pyv.vars.images['canada-orange'], r4infos[:2])

        # ------------
        # paint counter
        # ------------
        ev.screen.blit(self.label_rounds_cpt, (180, 64))

        # ------------
        # paint falling blocks
        # ------------
        for k, blockinfos in self.mod.allboxes.items():
            elt_type = blockinfos[4]
            if elt_type == self.mod.BOMB_CODE:
                color = 'red'
            elif elt_type == self.mod.BONUS_CODE:
                color = 'black'
            else:
                color = cls.color_mapping[elt_type]
            pyv.draw_rect(ev.screen, color, blockinfos[:4])


@pyv.declare_begin
def init_game(vmst=None):
    global my_mod, ev_manager, gscreen
    pyv.init()
    ev_manager = pyv.get_ev_manager()
    ev_manager.setup(MyEvTypes)

    gscreen = pyv.get_surface()
    # shared.screen = screen
    pyv.init(wcaption='Lucky Stamps: the game')
    pyv.define_archetype('player', ('body', 'speed', 'controls'))
    pyv.define_archetype('block', ('body',))
    pyv.define_archetype('ball', ('body', 'speed_Y', 'speed_X'))
    blocks_create()
    player_create()
    ball_create()
    pyv.bulk_add_systems(systems)

    # - fetch info depuis le serveur
    url = "https://hiddenpath.kata.games/game_configs/lucky-stamps.json"
    response = requests.get(url)
    response_json = response.json()
    target_host = response_json['url']

    # get tirage result
    print('accès sur', target_host)
    response = requests.get(target_host)
    tirage_result = response.text

    # - algo juste pour tester
    my_mod = LsGameModel(tirage_result)

    v = LsView(my_mod)
    c = MyController(my_mod)
    v.turn_on()
    c.turn_on()


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


@pyv.declare_update
def updatechess(info_t):
    global ev_manager
    ev_manager.post(pyv.EngineEvTypes.Update, curr_t=info_t)
    ev_manager.post(pyv.EngineEvTypes.Paint, screen=gscreen)
    ev_manager.update()
    pyv.flip()


@pyv.declare_end
def done(vmst=None):
    pyv.close_game()
    print('gameover!')
