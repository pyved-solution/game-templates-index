# ------
# engine-related code, do not modify!
# --------

registry = set()
libname_to_alias_mapping = dict()

def get_alias(origin_lib_name):
    return libname_to_alias_mapping[origin_lib_name]

def has_registered(origin_lib_name):
    return origin_lib_name in libname_to_alias_mapping

def register_lib(alias, libname, value):  # handy for dependency injection
    global registry, libname_to_alias_mapping
    libname_to_alias_mapping[libname] = alias
    if alias in registry:
        raise KeyError(f'Cannot register lib "{alias}" more than once!')
    globals()[alias] = value
    registry.add(alias)


# ------
# custom code the gamedev added
# --------
ref_maze = None
ref_visibility_mger = None
ref_player = None

# ref_monsters = None
# ref_player = None

game_paused = False
avatar_sprite_sheet = None
level_count = 1
walkable_cells = []  # list of walkable cells is fully dynamic, we prefer to store it as a gl var
tileset = None
avatar_img = None
monster_img = None
avatar_hp = 100

MAP_W, MAP_H = 24, 24  # CELLS.
# these dimensions match map size that is,
# the size of: actor_state(maze_actor).content

GODMODE = False  # if set to True, ignore fog and see all
CELL_SIDE = 32  # px
GRID_REZ = (CELL_SIDE, CELL_SIDE)
ENDGAME_MSG = 'GAME OVER; Max level= {}'

WALL_COLOR = (8, 8, 24)
HIDDEN_CELL_COLOR = (24, 24, 24)
CELL_COLOR = (106, 126, 105)  # punk green
BLOCK_SIZE = 40
VISION_RANGE = 4
SCR_WIDTH = 960
SCR_HEIGHT = 720
PLAYER_DMG = 10
PLAYER_HP = 100
MONSTER_DMG = 10
MONSTER_HP = 20