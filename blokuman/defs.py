import katagames_sdk as katasdk
import katagames_engine as kengi

GameStates = kengi.struct.enum(
    'TitleScreen',  # first in the list => initial gamestate
    'Credits',
    'Puzzle',
    'TaxPayment'
)
