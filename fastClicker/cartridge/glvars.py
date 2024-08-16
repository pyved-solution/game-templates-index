from . import pimodules


GAME_ID = 3

stored_jwt = None
ev_manager = screen = None

pyv = pimodules.pyved_engine

MyGameStates = pyv.custom_struct.enum(
    'TitleScreen',
    'CompeteNow',
)
