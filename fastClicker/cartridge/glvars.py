from . import pimodules


ev_manager = screen = None

pyv = pimodules.pyved_engine

MyGameStates = pyv.e_struct.enum(
    'TitleScreen',
    'CompeteNow',
)
