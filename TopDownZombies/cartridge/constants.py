from .glvars import pyv


pyv.bootstrap_e()

# TODO not constant

def runs_in_web():  # this is a very bad practice and should never exist!
    # "a game is a valid pyv game"
    # if and only if it runs without modification in the web ctx after running in the local ctx
    return False


def cload_img(source):
    try:
        # - deprecated
        if not runs_in_web():
            s = 'assets/' + source
        else:
            s = source
        return pyv.pygame.image.load(s)
    except FileNotFoundError:
        return pyv.vars.images[source.split('.')[0]]


NO_SOUND = True
NO_FOG = True
MAX_FPS = None  # uncap fps in local, too


# some colors (R, G, B)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARKGREY = (40, 40, 40)
LIGHTGREY = (100, 100, 100)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

FONT_NAME = 'arial'

# game settings
# Ensure no partial squares with these values
# old
# WINDOW_WIDTH = 1024  # 16 * 64 or 32 * 32 or 64 * 16
WINDOW_WIDTH = 832  # 13x64
# old
# WINDOW_HEIGHT = 768  # 16 * 48 or 32 * 24 or 64 * 12
WINDOW_HEIGHT = 704  # 11x64
FPS = 60
TITLE = "Zombie Top-down Shooter"
BGCOLOR = LIGHTGREY

# Usu. in pows of 2 e.g. 8, 16, 32, 64, etc.
TILESIZE = 64
GRIDWIDTH = WINDOW_WIDTH / TILESIZE
GRIDHEIGHT = WINDOW_HEIGHT / TILESIZE

WALL_IMG = 'tile_179.png'

# Player settings
PLAYER_MAX_HEALTH = 100
PLAYER_SPEED = 250
PLAYER_ROT_SPEED = 250  # degrees per second
PLAYER1_IMG = 'manBlue_gun.png'
PLAYER2_IMG = '(zombie)hitman_gun.png'
PLAYER_HIT_RECT = pyv.pygame.Rect(0, 0, 35, 35)  # needs to be Rect to get center (not Surface)
# By default, player facing right, so offset the bullet 30 to the right (x) and 10 down (y)
BARREL_OFFSET = pyv.pygame.math.Vector2(30, 10)
PLAYER_HEALTH_BAR_HEIGHT = 20
PLAYER_HEALTH_BAR_WIDTH = 100

# Weapon settings
# BULLET_IMG = 'bullet.png' # Using Surface instead.
# MAYBE: Create a Weapon class instead of dictionaries in our settings file
WEAPONS = dict()
WEAPONS['pistol'] = {
    'bullet_speed': 750,
    'bullet_lifetime': 1250,
    'fire_rate': 425,
    'kickback': 200,
    'bullet_spread': 6,
    'damage': 10,
    'bullet_count': 1,
    'bullet_usage': 1

}
WEAPONS['shotgun'] = {
    'bullet_speed': 500,
    'bullet_lifetime': 500,
    'fire_rate': 1000,
    'kickback': 500,
    'bullet_spread': 24,
    'damage': 8,
    'bullet_count': 5,
    'bullet_usage': 1
}
WEAPONS['uzi'] = {
    'bullet_speed': 1000,
    'bullet_lifetime': 750,
    'fire_rate': 175,
    'kickback': 300,
    'bullet_spread': 15,
    'damage': 7,
    'bullet_count': 1,
    'bullet_usage': 1
}

LANDMINE_DAMAGE = 35
LANDMINE_KNOCKBACK = 50

# Mob settings
MOB_IMG = 'zombie1_hold.png'
MOB_SPEEDS = [220, 240, 260]
MOB_HIT_RECT = pyv.pygame.Rect(0, 0, 30, 30)
MOB_DAMAGE = 10
MOB_KNOCKBACK = 25
MOB_AVOID_RADIUS = 70  # in px
MOB_DETECT_RADIUS = 325

# Runner settings
RUNNER_IMG = 'zombie2_hold.png'
RUNNER_SPEEDS = [350, 365]
RUNNER_HIT_RECT = pyv.pygame.Rect(0, 0, 30, 30)
RUNNER_DAMAGE = 15
RUNNER_KNOCKBACK = 30
RUNNER_AVOID_RADIUS = 45  # in px
RUNNER_DETECT_RADIUS = 350

# Items
ITEM_IMAGES = {
    "health": "(zombie)health_icon.png",
    "pistol_ammo": "(zombie)pistol_ammo.png",
    "shotgun_ammo": "(zombie)shotgun_ammo.png",
    "uzi_ammo": "(zombie)uzi_ammo.png",
    "landmine": "(zombie)mine_icon.png",
    "bonus": "(zombie)bonus.png",
    "comms": "(zombie)comms_icon.png",
    "shotgun": "(zombie)shotgun.png",
    "pistol": "(zombie)pistol.png",
    "uzi": "(zombie)uzi.png",
    "placed_mine": "(zombie)landmine.png",
    "tower": "(zombie)cell_tower.png"
}

GUN_IMAGES = {
    "pistol": "(zombie)pistol.png",
    "shotgun": "(zombie)shotgun.png",
    "uzi": "(zombie)uzi.png"
}

# Item effectiveness
HEALTH_PICKUP_AMT = 25
PISTOL_AMMO_PICKUP_AMT = 6
SHOTGUN_AMMO_PICKUP_AMT = 6
UZI_AMMO_PICKUP_AMT = 14

# Effects
MUZZLE_FLASHES = ["(zombies)whitePuff15.png", "(zombies)whitePuff16.png", "(zombies)whitePuff17.png",
                  "(zombies)whitePuff18.png"]
FLASH_DURATION = 40
SPLAT_IMAGES = ['blood-splatter1.png', 'blood-splatter3.png', 'blood-splatter4.png']

ITEM_BOB_RANGE = 50
ITEM_BOB_SPEED = 3

DAMAGE_ALPHA = [i for i in range(0, 255, 20)]
ITEM_ALPHA = [i for i in range(0, 255, 2)]
ITEM_FADE_MIN = 50
ITEM_FADE_MAX = 245
NIGHT_COLOR = (133, 133, 180)
LIGHT_RADIUS = (350, 350)
LIGHT_MASK = '(zombie)light_350_med.png'

# Layers
WALL_LAYER = 1
PLAYER_LAYER = 2
BULLET_LAYER = 3
MOB_LAYER = 2
EFFECTS_LAYER = 4
ITEMS_LAYER = 1

# ----------------------------------
# Sounds
BG_MUSIC = 'assets/Disturbed-Soundscape.ogg'
MENU_MUSIC = 'assets/espionage.ogg'
LVL1_MUSIC = 'assets/City-of-the-Disturbed.ogg'
ZOMBIE_MOAN_SOUNDS = [
    'brains2.wav', 'brains3.wav', 'zombie-roar-1.wav', 'zombie-roar-2.wav',
    'zombie-roar-3.wav', 'zombie-roar-5.wav', 'zombie-roar-6.wav', 'zombie-roar-7.wav'
]
for k in range(len(ZOMBIE_MOAN_SOUNDS)):
    ZOMBIE_MOAN_SOUNDS[k] = 'assets/' + ZOMBIE_MOAN_SOUNDS[k]

ZOMBIE_DEATH_SOUNDS = ['assets/splat-15.wav']
PLAYER_HIT_SOUNDS = ['assets/pain/8.wav', 'assets/pain/9.wav', 'assets/pain/10.wav', 'assets/pain/11.wav']
WEAPON_SOUNDS = {
    'pistol': ['pistol.wav'],
    'shotgun': ['shotgun.wav'],
    'uzi': ['uzi.wav'],
    'empty': ['empty_gun.wav']
}
for k, v in WEAPON_SOUNDS.items():
    WEAPON_SOUNDS[k] = ['assets/' + v[0], ]

EFFECTS_SOUNDS = {
    'level_start': 'level_start.wav',
    'health_up': 'item_pickup.ogg',
    'item_pickup': 'item_pickup.ogg',
    'ammo_pickup': 'ammo_pickup.ogg',
    'gun_pickup': 'gun_pickup.wav',
    'explosion': 'short_explosion.ogg',
    'place_mine1': 'drop_sound.wav',
    'place_mine2': '1beep.mp3'
}
for k, v in EFFECTS_SOUNDS.items():
    EFFECTS_SOUNDS[k] = 'assets/' + v
# -------------


STORIES = {
    'tutorial': ["Been a while since I came out of hiding.",
                 "Supplies are running low and I don't know how much longer "
                 "things can last.", "There's a tower here I can use to communicate with other survivors.",
                 "I just need to find the device for communication.", "Well... won't do any good to just sit here.",
                 "I need to find that comms device... I pray that I can get back to the tower alive."],

    'level1': ["Received a distress call.", "Didn't come with much info. Likely a lone survivor.", "Probably"
                                                                                                   " won't survive.",
               "Still, it's a good excuse to clear the local area of zombies.",
               "Been waiting to bring out the big guns.", "Time to go to work >"],

    'ending': ["THANKS FOR PLAYING!", "IF YOU ENJOYED THIS EXPERIENCE AND WANT ME TO BUILD", "THE REST OF THE GAME,",
               "LET ME KNOW IN THE COMMENTS!", "YOU CAN QUIT THE GAME NOW OR PRESS THE ENTER KEY",
               "TO RETURN TO THE MAIN MENU."]
}

LEVELS = {
    'tutorial.tmx': {
        'objective': 'return_comms',
        'plyr': PLAYER1_IMG,
        'story': STORIES['tutorial'],
        'music': BG_MUSIC
    },

    'level1.tmx': {
        'objective': 'kill_all_zombies',
        'plyr': PLAYER2_IMG,
        'story': STORIES['level1'],
        'music': LVL1_MUSIC
    },

    'level1-chris.tmx': {
        'objective': 'return_comms',
        'plyr': PLAYER1_IMG,
        'story': 'whatever!',
        'music': LVL1_MUSIC
    },

    'ending': {
        'story': STORIES['ending']
    }
}
