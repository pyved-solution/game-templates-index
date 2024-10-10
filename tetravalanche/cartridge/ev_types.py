from .glvars import pyv


MyEvTypes = pyv.game_events_enum((
    'Drop',  # contains new_level
    'Shake',
    'LevelUp',  # contains level

    'ChoiceChanges',  # contient code
    'LineDestroyed',
    'FlatWorld',  # means the shake effect is over
    'BlocksCrumble',
    'GameLost',
    'DemandeTournoi',
    
    # -------------------

    'ItemGetsPlaced',  # contient cell une paire ij, ref_repr_g la référence sur item cliquable
    'ItemDragged',  # contient ref_item
    'ItemDrops',  # item cliquable déposé contient ref_item
    'PlayerLogsIn',  # contient username, solde
    'LoginModUpdate',  # contient valeurs pr: login, pwd
    'TrigValidCredentials',
    'FakeLogin',
    'LoadingBarMoves',
    'BalanceChanges',  # contiendra value (un int)
    'ContentChanges',  # quand un item est pris/déposé
    'TurnEnds',
    'PlayerSelects',
    'SelectResult',
    'GstateUpdate',
    'AttackResult',
    'PlayerDies',
    'PlayerWins',
    'AddDices',
    'ConquestGameStart',
    'ConquestGameOver',
    'LandValueChanges',  # contient land_id, num_dice
    'LandOwnerChanges',  # contient land_id, owner_pid
    'MapChanges',
    'RemotePlayerPasses',  # grâce à ça, le ctrl réseau peut forcer ctrl RemotePlayer à rendre la main normalement
    'PlayerPasses',  # contient [old_pid, new_pid]
    'ForceEcoute',
    'RequestMap'
))
