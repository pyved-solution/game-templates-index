import math
from .demolib import animobs
from .demolib import dialogue
from .glvars import pyv


# aliases
EngineEvTypes = pyv.events.EngineEvTypes
pygame = pyv.pygame

# - gl variables
current_path = None
current_tilemap = 0
maps = list()
map_viewer = None
conv_viewer = None
conversation_ongoing = False
my_pc = None
my_npc = None


class Character(pyv.isometric.model.IsometricMapObject):
    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y
        self.surf = pyv.vars.images['sys_icon']
        # self.surf.set_colorkey((0,0,255))

    def __call__(self, dest_surface, sx, sy, mymap):
        mydest = self.surf.get_rect(midbottom=(sx, sy))
        dest_surface.blit(self.surf, mydest)


class MovementPath:
    def __init__(self, mapob, dest, mymap):
        self.mapob = mapob
        self.dest = dest
        self.goal = None
        self.mymap = mymap
        self.blocked_tiles = set()
        obgroup = list(mymap.objectgroups.values())[0]
        for ob in obgroup.contents:
            if ob is not mapob:
                self.blocked_tiles.add((ob.x, ob.y))
                if self.pos_to_index((ob.x, ob.y)) == self.pos_to_index(dest):
                    self.goal = ob
        print(mymap)
        self.path = pyv.terrain.AstarPathfinder(
            mymap, self.pos_to_index((mapob.x, mapob.y)), self.pos_to_index(dest), self.tile_is_blocked,
            mymap.clamp_pos_int, blocked_tiles=self.blocked_tiles
        )
        if not self.path.results:
            print("No path found!")

        if self.path.results:
            self.path.results.pop(0)
        self.all_the_way_to_dest = not (
                    dest in self.blocked_tiles or self.tile_is_blocked(mymap, *self.pos_to_index(dest)))
        if self.path.results and not self.all_the_way_to_dest:
            self.path.results.pop(-1)
        self.animob = None

    @staticmethod
    def pos_to_index(pos):
        x = math.floor(pos[0])
        y = math.floor(pos[1])
        return x, y

    @staticmethod
    def tile_is_blocked(mymap, x, y):
        return mymap.tile_is_blocked(x, y)

    def __call__(self):
        # Called once per update; returns True when the action is completed.
        if self.animob:
            self.animob.update()
            if self.animob.needs_deletion:
                self.animob = None
        if not self.animob:
            if self.path.results:
                if len(self.path.results) == 1 and self.all_the_way_to_dest:
                    nx, ny = self.dest
                    self.path.results = []
                else:
                    nx, ny = self.path.results.pop(0)

                # De-clamp the nugoal coordinates.
                nx = min([nx, nx - self.mymap.width, nx + self.mymap.width], key=lambda x: abs(x - self.mapob.x))
                ny = min([ny, ny - self.mymap.height, ny + self.mymap.height], key=lambda y: abs(y - self.mapob.y))

                self.animob = animobs.MoveModel(
                    self.mapob, dest=(nx, ny), speed=0.25
                )
            else:
                # print((self.mapob.x,self.mapob.y))
                # sx, sy = viewer.screen_coords(self.mapob.x, self.mapob.y, 0, -8)
                # print(viewer.map_x(sx, sy, return_int=False), viewer.map_y(sx, sy, return_int=False))
                return True


class NPC(pyv.isometric.model.IsometricMapObject):
    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y
        self.surf = pyv.vars.images['npc']
        # self.surf.set_colorkey((0,0,255))

    def __call__(self, dest_surface, sx, sy, mymap):
        mydest = self.surf.get_rect(midbottom=(sx, sy))
        dest_surface.blit(self.surf, mydest)


# --------------------------------------------
# Define controllers etc
# --------------------------------------------
class BasicCtrl(pyv.EvListener):

    def on_quit(self, ev):
        pyv.vars.gameover = True

    def on_mouseup(self, ev):
        global map_viewer, my_pc, current_path
        if conversation_ongoing:
            return  # we block all movement when the conversation is active

        cursor = map_viewer.cursor
        if cursor:
            cursor.update(map_viewer, ev)
        current_path = MovementPath(my_pc, cursor.get_pos(), maps[current_tilemap])
        # - debug msg in cas something goes wrong with the pathfinding...
        # print('movement path has been set', current_path)

    # def proc_event(self, gdi):
    #     global conversation_ongoing, map_viewer, mypc, current_tilemap, current_path
    #     if gdi.type == pygame.KEYDOWN:
    #         if gdi.key == pygame.K_ESCAPE:
    #             if conversation_ongoing:
    #                 # abort
    #                 self.pev(MyEvTypes.ConvEnds)
    #             else:
    #                 self.pev(EngineEvTypes.GAMEENDS)
    #         elif gdi.key == pygame.K_d and mypc.x < tilemap_width - 1.5:
    #             mypc.x += 0.1
    #         elif gdi.key == pygame.K_a and mypc.x > -1:
    #             mypc.x -= 0.1
    #         elif gdi.key == pygame.K_w and mypc.y > -1:
    #             mypc.y -= 0.1
    #         elif gdi.key == pygame.K_s and mypc.y < tilemap_height - 1.5:
    #             mypc.y += 0.1
    #         elif gdi.key == pygame.K_TAB:
    #             current_tilemap = 1 - current_tilemap
    #             map_viewer.switch_map(maps[current_tilemap])


class PathCtrl(pyv.EvListener):
    def __init__(self):
        super().__init__()

    def on_update(self, event):
        global current_path, conv_viewer, conversation_ongoing
        if current_path is not None:
            ending_reached = current_path()
            if ending_reached:
                if current_path.goal:
                    conversation_ongoing = True
                    myconvo = dialogue.Offer.from_json(pyv.vars.data['conversation'])  # using data pre-loaded thu pyv
                    conv_viewer = dialogue.ConversationView(myconvo)
                    conv_viewer.turn_on()
                current_path = None

    def on_conv_ends(self, ev):
        global conversation_ongoing
        conversation_ongoing = False  # unlock player movements
        if conv_viewer.active:
            conv_viewer.turn_off()
