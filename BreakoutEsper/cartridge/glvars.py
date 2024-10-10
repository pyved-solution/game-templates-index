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
# custom code added by the gamedev (game specific)
# --------
def interpolate_color(x, y) -> tuple:
    return 150, ((x-BLOCKS_STARTING_X) * 0.27) % 256, ((y-BLOCKS_STARTING_Y) * 1.22) % 256


def set_scr_size(val):
    global scr_size, blocks_limit
    scr_size = val
    blocks_limit = scr_size[0] / (BLOCK_W + BLOCK_SPACING)


# CONSTANTS
# -------------------------------------------------
# physics
PL_WIDTH, PL_HEIGHT = 128, 18
PLAYER_SPEED = 266

# ball-related
BALL_INIT_POS = 480, 277
BALL_SIZE = 22
MAX_XSPEED_BALL = 225.0
YSPEED_BALL = 288.0

# (Size of break-out blocks)
BLOCK_W = 74
BLOCK_H = 35
BLOCK_SPACING = 5
BLOCKS_STARTING_X = 7
BLOCKS_STARTING_Y = 58

# VARIABLES
# -------------------------------------------------
menu_message = None  # to be displayed in the menu gamestate
font = None
screen = None
scr_size = None

classic_ftsize = 38
start_game_label = None
end_game_label = None

prev_time_info = None
player_entity = None
ball_entity = None

blocks = set()
blocks_limit = None
