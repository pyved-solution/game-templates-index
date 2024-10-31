from .glvars import pyv
pyv.bootstrap_e()

from .classes import *  # this imports: pygame, EngineEvTypes
from . import classes  # storage for map_viewer, maps, etc
from .custom_events import MyEvTypes

# TODO need to unify this ?
#  You should always use what is already in pyv.*
# import demolib.animobs as animobs
# import demolib.dialogue as dialogue
# import demolib.pathfinding as pathfinding
# from demolib.defs import MyEvTypes
# import math
# TODO investigate polarbear crash
# if this line isnt added, after pyv.init, we may have problems:
# pyv.polarbear.my_state.screen = pyv.vars.screen

kpressed = set()
# - new gl vars
# global variables
path_ctrl = None
tilemap_height = tilemap_width = 0
evm = None


# ---------------------
#  handy functions
# ---------------------
def _load_maps():
    global maps, tilemap_width, tilemap_height
    maps.append(
        pyv.isometric.model.IsometricMap.load(['cartridge'], 'test_map.tmj')
    )
    # maps.append(
    #    pyv.isometric.model.IsometricMap.load(['cartridge'], 'test_map2.tmx')
    # )
    tilemap_width, tilemap_height = maps[0].width, maps[0].height


def _add_map_entities(gviewer):
    classes.my_pc = Character(10, 10)
    classes.my_npc = NPC(15, 15)

    # too many hacks, no?
    tm = maps[0]
    list(tm.objectgroups.values())[0].contents.append(classes.my_pc)
    list(tm.objectgroups.values())[0].contents.append(classes.my_npc)
    # tm2 = maps[1]
    # list(tm2.objectgroups.values())[0].contents.append(classes.my_pc)
    # list(tm2.objectgroups.values())[0].contents.append(classes.my_npc)
    gviewer.set_focused_object(classes.my_pc)
    # force: center on avatar op.
    # mypc.x += 0.5


def init(vmst=None):
    global evm
    pyv.init(pyv.LOW_RES_MODE, wcaption='IsometricRPG Tech Demo')
    evm = pyv.get_ev_manager()
    evm.setup(MyEvTypes)

    _load_maps()
    classes.map_viewer = pyv.isometric.IsometricMapViewer(  # TODO unify
        maps[0], pyv.vars.screen,
        up_scroll_key=pygame.K_UP, down_scroll_key=pygame.K_DOWN,
        left_scroll_key=pygame.K_LEFT, right_scroll_key=pygame.K_RIGHT
    )
    _add_map_entities(classes.map_viewer)

    cursor_image = pyv.vars.images['half-floor-tile']
    cursor_image.set_colorkey((255, 0, 255))
    classes.map_viewer.cursor = pyv.isometric.extras.IsometricMapQuarterCursor(0, 0, cursor_image, maps[0].layers[1])

    classes.map_viewer.turn_on()

    pctrl = PathCtrl()
    pctrl.turn_on()
    bctrl = BasicCtrl()
    bctrl.turn_on()

    #gctrl = pyv.get_game_ctrl()
    #gctrl.turn_on()


def update(time_info=None):
    # for ev in pygame.event.get():
    #     if ev.type == pygame.QUIT:
    #         pyv.vars.gameover = True
    #     elif ev.type == pygame.KEYDOWN:
    #         kpressed.add(ev.key)
    #     elif ev.type == pygame.KEYUP:
    #         kpressed.remove(ev.key)

    # - logic
    evm.post(EngineEvTypes.Update, info_t=time_info)
    evm.post(EngineEvTypes.Paint, screen=pyv.vars.screen)
    evm.update()

    # do not draw directly, use events!
    # scr = pyv.vars.screen

    # scr.fill('paleturquoise3')
    # if len(kpressed):
    #     pyv.draw_rect(scr, 'orange', (15, 64, 100, 100))
    pyv.flip()


def close(vmst=None):
    pyv.close_game()
    print('gameover!')
