from . import pimodules


screen = ev_manager = None
forced_serial = None

GAME_PRICE = 5

# netw
stored_jwt = None
GAME_CONFIG_SOURCE = "https://beta.kata.games/game-configs/LuckyStamps1.json"

# FORCED_GAME_HOST = "https://games.gaudia-tech.com/lucky-stamps/testluck.php"  # handy for debug
FORCED_GAME_HOST = None

# ------------------
# taille (px) attendue pour les <stamps> img = 149x175
# ------------------
STAMPW, STAMPH = 149, 175
TEST_GAME_ID = 16
DEFAULT_USER_ID = 8

# used to debug netw.chall_* functions, but its not really needed now
DUMMY_SCORE = 9998

MyGameStates = pimodules.pyved_engine.enum(
    'IntroState',
    'CasinoState'
)
