import katagames_engine as kengi


MyEvTypes = kengi.event.enum_ev_types(
    # - LoginState
    'LoginStUsernameChanges',  # contains txt
    'LoginStPwdChanges',  # contains txt(not a plain pwd str!)
    'LoginStFocusChanges',  # contains focusing_username=True/False
    'TrigValidCredentials',  # no attr
    'PlayerLogsIn',  # sent after succesful auth, contains username:str, solde:int

    # - Puzzle state
    'NewPieces',  # bag has been re-filled, no attr
    'ScoreChanges',  # contient score=int
    'GameLost',
    'LineDestroyed',
    'BlocksCrumble',

    # - TitleScreen state
    'ChoiceChanges',  # contient code
    'BalanceChanges',  # contiendra value (un int)
    'DemandeTournoi',

    # - Taxpayment state
    'LoadingBarMoves',

    # 'ItemGetsPlaced',  # contient cell une paire ij, ref_repr_g la référence sur item cliquable
    # 'ItemDragged',  # contient ref_item
    # 'ItemDrops',  # item cliquable déposé contient ref_item

    # 'LoginModUpdate',  # contient valeurs pr: login, pwd
    # 'FakeLogin',
    # 'ContentChanges',  # quand un item est pris/déposé
)

# - pr auto inspection, mais c pas obligatoire!
# CgmEvent.inject_custom_names(MyEvTypes)  # pour avoir les noms affichés par CgmEvent.__str__
