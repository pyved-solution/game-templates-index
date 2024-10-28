from .glvars import pyv

ChessGstates = pyv.struct.enum(
    'Chessintro',
    'Chessmatch',
)

ChessEvents = pyv.game_events_enum((
    'MatchBegins',
    'MoveChosen',  # contains: player_color, from_square, to_square, rook_type, ep_flag
    'Checkmate',  # contains: winner_color
    'Check',
    'CancelMove',  # when playing vs an AI this would cancel 1-2 moves, when PvP this cancels only 1 move
    'PromotionPopup'  # contains: target_square, plcolor [allows the player to select the piece he wants the most!]
))
