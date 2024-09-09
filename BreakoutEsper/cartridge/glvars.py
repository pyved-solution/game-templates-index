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
screen = None
scr_size = None
prev_time_info = None

player_entity = None
ball_entity = None

# physics
PL_WIDTH, PL_HEIGHT = 110, 25
PLAYER_SPEED = 220

# ball-related
BALL_INIT_POS = 480, 277
BALL_SIZE = 22
MAX_XSPEED_BALL = 225.0
YSPEED_BALL = 288.0
