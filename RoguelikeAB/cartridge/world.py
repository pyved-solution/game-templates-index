from . import shared
from . import glvars

pyv = glvars.pyv
pyv.bootstrap_e()
pygame = pyv.pygame
Sprsheet = pyv.gfx.Spritesheet


def create_player():
    player = pyv.new_from_archetype('player')
    pyv.init_entity(player, {
        'position': None,
        'controls': {'left': False, 'right': False, 'up': False, 'down': False},
        'damages': shared.PLAYER_DMG,
        'health_point': shared.PLAYER_HP,
        'enter_new_map': True
    })


# def create_wall():
#     wall = pyv.new_from_archetype('wall')
#     pyv.init_entity(wall, {})


def create_monster(position):
    monster = pyv.new_from_archetype('monster')
    pyv.init_entity(monster, {
        'position': position,
        'damages': shared.MONSTER_DMG,
        'health_point': shared.MONSTER_HP,
        'active': False  # the mob will become active, once the player sees it
    })


def create_potion():
    potion = pyv.new_from_archetype('potion')
    pyv.init_entity(potion, {
        'position': None,
        'effect': None
    })


def create_exit():
    exit_ent = pyv.new_from_archetype('exit')
    pyv.init_entity(exit_ent, {})


def update_vision_and_mobs(i, j):
    # --------- updating the state of mobs (->a hidden mob becomes visible !!)
    # we also need to update the state of mobs!
    all_mobs = pyv.find_by_archetype('monster')
    for m in all_mobs:
        if tuple(m.position) in li_visible:
            m.active = True  # mob "activation" --> will track the player
