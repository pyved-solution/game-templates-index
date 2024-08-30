from . import pimodules


screen = ev_manager = None
forced_serial = None

GAME_PRICE = 5

# netw
stored_jwt = None

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
