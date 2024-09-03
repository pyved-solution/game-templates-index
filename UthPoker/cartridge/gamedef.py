"""
[Rules]
Ultimate Texas Hold’em is played against the casino, so you’ll be up against the dealer. There can be multiple players
at the table, but that doesn’t change much at all as your only goal is to beat the dealer. Whether other players win or
lose is of no significance to you.

#1 > after paying Ante+Blind, the dealer gives you 2 cards. You can either: Check / Bet 3x the ante / Bet 4x the ante
(If you decide to bet either 3x or 4x after seeing your hand, the dealer will deal the flop, the turn & the river
without you having any further betting options)

#2 > In case you opt to check, the dealer will deal out the flop. Now you can either: Check / Bet 2x the ante
(If you bet, the dealer will deal the turn & the river without you having any further betting options)

#3 > In case you opt to check, the dealer will deal the turn & the river. This is the final betting round. This time,
you can either: Fold / Bet 1x the ante. You cannot check anymore since the river is out.
"""
from . import common
from . import pimodules
from .game_logic import AnteSelectionState, PreFlopState, FlopState, TurnRiverState, OutcomeState
from .uth_model import UthModel
from .uth_view import UthView


# aliases
pyv = pimodules.pyved_engine
pyv.bootstrap_e()

MyEvTypes = common.MyEvTypes

# const
WARP_BACK = [2, 'niobepolis']
CARD_SIZE_PX = (69, 101)

pyg = pyv.pygame
screen = None
r4 = pyg.Rect(32, 32, 128, 128)
kpressed = set()


# game_obj = PokerUth()
# common.refgame = game_obj
## if not isinstance(common.dyncomp, common.DynComponent):  # only if katasdk is active
##     katasdk.gkart_activation(game_obj)
# game_obj.loop()


ev_manager = None
mod, view = None, None

# import pyved_engine as pyv
@pyv.declare_begin
def begin_uthpoker(vmst=None):
    global screen, ev_manager, mod, view
    # as of pyved v29_9a1 the upscaling seems to be broken in webctx
    # that is why we cant use x2 here. In the future this should be fixed
    pyv.init(mode=1, wcaption='Uth Poker')
    screen = pyv.get_surface()

    ev_manager = pyv.get_ev_manager()
    ev_manager.setup(common.MyEvTypes)

    pkstates = common.PokerStates
    pyv.declare_game_states(
        pkstates, {
            # do this to bind state_id to the ad-hoc class!
            pkstates.AnteSelection: AnteSelectionState,
            pkstates.PreFlop: PreFlopState,
            pkstates.Flop: FlopState,
            pkstates.TurnRiver: TurnRiverState,
            pkstates.Outcome: OutcomeState
        }
    )

    mod = UthModel()
    common.refmodel = mod
    view = UthView(mod)
    common.refview = view
    view.turn_on()

    ev_manager.post(pyv.EngineEvTypes.Gamestart)


@pyv.declare_update
@pyv.declare_update
def update_uthpoker(info_t=None):
    global ev_manager, screen

    ev_manager.post(pyv.EngineEvTypes.Update, curr_t=info_t)
    ev_manager.post(pyv.EngineEvTypes.Paint, screen=screen)

    ev_manager.update()
    pyv.flip()


@pyv.declare_end
def done(vmst=None):
    pyv.close_game()
    print('gameover!')
