from . import systems
from .world import blocks_create, player_create, ball_create
import json
# import pyved_engine as pyv
import requests
from . import pimodules
from .LuckyStampsView import LuckyStampsView
from .shared import MyEvTypes


pyv = pimodules.pyved_engine
THECOLORS = pyv.pygame.color.THECOLORS


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
    binfx, binfy = 100, 90
    starting_y = -176
    BLOCK_SPEED = 2*18

    def __init__(self, serial, li_events=None):
        super().__init__()

        if li_events is not None:
            self.li_events = li_events
            self.li_gains = [0 for _ in range(7)]
        else:
            print('-'*60)
            print('SERIAL RECEIVED:')
            print(serial)
            print('-' * 60)
            print()
            self.li_events, self.li_gains = json.loads(serial)

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
            if not(e[0] < self.current_tirage):
                break
            self.cursor += 1

        for k in range(5):
            e = self.li_events[self.cursor+k]
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
                elt_type = e[2+row_no]
                self.allboxes[key] = [
                    cls.binfx + column_no * 153,  # computing the position
                    cls.starting_y,
                    STAMPW, STAMPH,
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

        etype = self.allboxes[self.curr_box][4]
        if etype == self.__class__.BONUS_CODE:
            self.remainning_rounds += 2
            self.pev(MyEvTypes.ForceUpdateRounds, new_val=self.remainning_rounds)
        return True

    def update(self):
        cls = self.__class__
        if self.curr_box is None:
            return

        if self.curr_box not in self.anim_ended:
            self.allboxes[self.curr_box][1] += cls.BLOCK_SPEED
            n = int(self.curr_box[3])
            targety = cls.binfy + n*(STAMPH+4) - 2

            if self.allboxes[self.curr_box][1] > targety:  # detection de "collision"
                self.allboxes[self.curr_box][1] = targety
                # passe à l'anim suivante
                self.anim_ended[self.curr_box] = True

                if not self.select_next_box():
                    # animation ended
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
                    self.__class__.starting_y,
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

    def on_earnings_update(self, ev):
        print('[Ctrl] Detection: you will earn a total of {}'.format(ev.value))

    def on_quit(self, ev):
        pyv.vars.gameover = True

    def on_update(self, ev):
        self.mod.update()
        if not self.mod.autoplay:
            self.mod.try_proc_bombs()  # can pursue the animation!


forced_serial = None

# exemple long:

#forced_serial = """
#[[[0,"C0",3,4,2],[0,"C1",2,5,2],[0,"C2",-1,1,-1],[0,"C3",6,1,4],[0,"C4",1,5,3],[0,"C2",5,2,6],[1,"C0",6,3,-1],[1,"C1",4,4,6],[1,"C2",2,6,7],[1,"C3",6,1,7],[1,"C4",-1,7,7],[1,"C0",7,4,5],[1,"C4",4,3,2],[2,"C0",0,2,1],[2,"C1",4,5,3],[2,"C2",7,1,2],[2,"C3",6,1,6],[2,"C4",1,4,6],[3,"C0",5,4,1],[3,"C1",4,3,3],[3,"C2",4,0,-1],[3,"C3",4,1,2],[3,"C4",6,6,3],[3,"C2",3,3,1],[4,"C0",4,1,-1],[4,"C1",7,4,4],[4,"C2",7,6,1],[4,"C3",6,4,0],[4,"C4",3,1,-1],[4,"C0",3,2,7],[4,"C4",4,5,2],[5,"C0",6,2,5],[5,"C1",5,5,2],[5,"C2",6,3,2],[5,"C3",-1,6,3],[5,"C4",-1,3,6],[5,"C3",6,1,7],[5,"C4",5,7,7],[6,"C0",5,1,5],[6,"C1",3,5,1],[6,"C2",2,6,6],[6,"C3",6,1,2],[6,"C4",0,5,5],[7,"C0",2,6,1],[7,"C1",3,7,2],[7,"C2",1,5,5],[7,"C3",1,4,4],[7,"C4",1,7,5],[8,"C0",2,-1,5],[8,"C1",5,3,1],[8,"C2",5,7,1],[8,"C3",1,2,2],[8,"C4",7,5,3],[8,"C0",6,7,3],[9,"C0",3,6,2],[9,"C1",2,-1,-1],[9,"C2",1,5,7],[9,"C3",5,5,2],[9,"C4",3,3,4],[9,"C1",5,5,6],[10,"C0",7,6,3],[10,"C1",-1,6,6],[10,"C2",5,3,6],[10,"C3",2,0,2],[10,"C4",4,2,6],[10,"C1",0,4,4],[11,"C0",7,4,4],[11,"C1",4,6,4],[11,"C2",2,6,6],[11,"C3",3,7,6],[11,"C4",3,2,7],[12,"C0",7,7,5],[12,"C1",6,7,4],[12,"C2",5,5,1],[12,"C3",7,3,3],[12,"C4",4,6,2]],[0,0,0,0,0,0,0,0,0,0,0,0,0]]

# exemples plus court:

#forced_serial = """
#[[[0,"C0",4,3,1],[0,"C1",-1,-1,3],[0,"C2",3,4,0],[0,"C3",6,7,3],[0,"C4",2,7,-1],[0,"C1",1,3,5],[0,"C4",7,3,3],[1,"C0",4,3,5],[1,"C1",4,6,1],[1,"C2",6,-1,2],[1,"C3",0,2,7],[1,"C4",5,4,1],[1,"C2",6,6,6],[2,"C0",7,5,5],[2,"C1",5,1,2],[2,"C2",6,7,6],[2,"C3",5,7,5],[2,"C4",5,6,3],[3,"C0",3,5,7],[3,"C1",1,-1,-1],[3,"C2",5,1,-1],[3,"C3",7,5,2],[3,"C4",7,2,5],[3,"C1",6,2,2],[3,"C2",3,6,2],[4,"C0",6,7,6],[4,"C1",4,7,4],[4,"C2",-1,-1,3],[4,"C3",2,3,3],[4,"C4",4,7,-1],[4,"C2",1,7,6],[4,"C4",4,4,1],[5,"C0",7,5,7],[5,"C1",3,-1,7],[5,"C2",7,7,2],[5,"C3",6,7,5],[5,"C4",6,3,1],[5,"C1",5,2,1],[6,"C0",-1,5,5],[6,"C1",2,1,-1],[6,"C2",6,1,6],[6,"C3",4,-1,1],[6,"C4",6,1,5],[6,"C0",4,6,4],[6,"C1",3,3,5],[6,"C3",6,4,4]],[0,10,0,0,0,0,0]]
#"""


@pyv.declare_begin
def init_game(vmst=None):
    global my_mod, ev_manager, gscreen, forced_serial
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
    if forced_serial is None:
        url = "https://hiddenpath.kata.games/game_configs/lucky-stamps.json"
        response = requests.get(url)
        response_json = response.json()
        target_host = response_json['url']
        print('accès sur', target_host)
        response = requests.get(target_host)
        tirage_result = response.text
    else:
        tirage_result = forced_serial

    my_mod = LsGameModel(tirage_result)

    # - s'il fallait simplement play une partie sans les gains
    # my_mod = LsGameModel(None
    # li_events =
    # [
    #   [0,"C0",4,3,1],[0,"C1",-1,-1,3],[0,"C2",3,4,0],[0,"C3",6,7,3],[0,"C4",2,7,-1],[0,"C1",1,3,5],[0,"C4",7,3,3],
    #   [1,"C0",4,3,5],[1,"C1",4,6,1],[1,"C2",6,-1,2],[1,"C3",0,2,7],[1,"C4",5,4,1],[1,"C2",6,6,6],[2,"C0",7,5,5],
    #   [2,"C1",5,1,2],[2,"C2",6,7,6],[2,"C3",5,7,5],[2,"C4",5,6,3],[3,"C0",3,5,7],[3,"C1",1,-1,-1],[3,"C2",5,1,-1],
    #   [3,"C3",7,5,2],[3,"C4",7,2,5],[3,"C1",6,2,2],[3,"C2",3,6,2],[4,"C0",6,7,6],[4,"C1",4,7,4],[4,"C2",-1,-1,3],
    #   [4,"C3",2,3,3],[4,"C4",4,7,-1],[4,"C2",1,7,6],[4,"C4",4,4,1],[5,"C0",7,5,7],[5,"C1",3,-1,7],[5,"C2",7,7,2],
    #   [5,"C3",6,7,5],[5,"C4",6,3,1],[5,"C1",5,2,1],[6,"C0",2,5,5],[6,"C1",3,-1,4],[6,"C2",2,2,2],[6,"C3",2,2,2],
    #   [6,"C4",6,1,5],[6,"C1",2,2,2]]
    # )
    v = LuckyStampsView(my_mod)
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
