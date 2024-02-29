# from . import pimodules
from . import shared
from . import systems
from .world import blocks_create, player_create, ball_create
import json
import pyved_engine as pyv
import requests
# pyv = pyved_engine  # pimodules.pyved_engine
import pyved_engine

THECOLORS = pyv.pygame.color.THECOLORS

MyEvTypes = pyv.game_events_enum((
    'ElementDrop',  # contient column_idx et elt_type
    'Earnings',  # contient value
    'NewRound',
    'GuiLaunchRound',
    'ForceUpdateRounds'  # contient new_val
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
        self.obj = json.loads(serial)
        print(self.obj)
        self.current_tirage = -1
        self.replayed_set = set()
        self.remainning_rounds = 3
        # self.fake_button = pyv.gui.

        self.event_cursor = 0

        # pr gérer animations
        self.allboxes = dict()
        self.anim_ended = dict()
        self.curr_box = None
        self.autoplay = False

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
        li_events, li_gains = self.obj
        for e in li_events:
            if e[0] == self.current_tirage:
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
                c = int(e[1][1])
                for r in range(3):
                    key = f'c{c}r{r}'
                    self.allboxes[key] = [cls.binfx + c * 153, -200, STAMPW, STAMPH, e[r + 2]]  # computes the position

        self.curr_box = 'c0r2'
        self.autoplay = True

        self.pev(MyEvTypes.Earnings, value=li_gains[self.current_tirage])

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

                c = int(self.curr_box[1])
                if n > 0:
                    n -= 1
                else:
                    n = 2
                    c += 1
                self.curr_box = f'c{c}r{n}'
                if self.curr_box == 'c5r2':  # out of bounds
                    self.curr_box = None
                    self.autoplay = False

    def get_rounds(self):
        return self.remainning_rounds

    def next_tirage(self):
        self.current_tirage += 1
        self.remainning_rounds -= 1
        self.pev(MyEvTypes.ForceUpdateRounds, new_val=self.remainning_rounds)
        print('new tirage is:', self.current_tirage)

        self.anim_ended.clear()
        self.pev(MyEvTypes.NewRound)


class MyController(pyv.EvListener):
    def __init__(self, mod):
        super().__init__()
        self.mod = mod

    def on_gui_launch_round(self, ev):
        if self.mod.autoplay:  # ignore re-roll if anim not ended
            return
        if self.mod.get_rounds() > 0:
            self.mod.next_tirage()
            self.mod.init_animation()
        else:
            print('no round left')  # cant re-roll if no roond left!

    def on_element_drop(self, ev):
        print(ev.column, '-', ev.elt_type)

    def on_earnings(self, ev):
        print('congrats! You have earned:', ev.value)

    def on_update(self, ev):
        self.mod.update()


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
