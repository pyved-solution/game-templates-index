from . import pimodules

pyv = pimodules.pyved_engine
enum = pyv.custom_struct.enum
GameStates = enum(
    'TitleScreen',  # first in the list => initial gamestate
    'Credits',
    'Puzzle',
    'TaxPayment'
)
