from . import pimodules


pyv = pimodules.pyved_engine

MyGameStates = pyv.e_struct.enum(
    'TitleScreen',
    'CompeteNow',
)
