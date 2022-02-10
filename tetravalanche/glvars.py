import katagames_sdk as katasdk


kataen = katasdk.engine
pygame = kataen.import_pygame()

my_fonts = {
    # 'larger': ('freesansbold.ttf', 27),
    # 'xl': ('freesansbold.ttf', 35),
    # 'display_font': ('freesansbold.ttf', 22),
    # 'basic': ('freesansbold.ttf', 16),
    # 'medium': ('freesansbold.ttf', 21),

    # -multiples de 16 fortement recommandé
    'tiny_monopx': ('monogram.ttf', 16),
    'sm_monopx': ('monogram.ttf', 28),
    'moderne': ('monogram.ttf', 32),
    'moderne_big': ('monogram.ttf', 64)
}

my_colors = {
    'c_black': '#000000',
    'c_white': '#ffffff',
    'c_cherokee': '#924a40',
    'c_oceanblue': '#84c5cc',

    'c_plum': '#9351b6',
    'c_leafgreen': '#72b14b',
    'c_purple': '#483aaa',
    'c_sunny': '#d5df7c',

    'c_brown': '#99692d',
    'c_mud': '#675200',
    'c_skin': '#c18178',
    'c_gray1': '#606060',

    'c_gray2': '#8a8a8a',
    'c_pastelgreen': '#b3ec91',
    'c_lightpurple': '#867ade',
    'c_gray3': '#b3b3b3',
}


# ----------------------
#  CONSTANTS
DEV_MODE = False
SKIP_MINING = False
MAX_FPS = 45
VERSION = '0.20.1a'
RESSOURCE_LOC = ['.']
CHOSEN_LANG = 'fr'
GAME_ID = 5  # tetravalanche


#  GLOBAL VARIABLES
# ----------------------
# engine
username = None  # indique si on est log
acc_id = None

# specific
song = None
snd_channels = dict()
num_lastchannel = 0  # pr alterner entre 0 et 1
copie_solde = None

colors = dict()
fonts = dict()

num_challenge = None  # sera un entier
chall_seed = None  # sera un entier déterminant cmt générateur aléatoire va sortir les données du problème d'optim.

multiplayer_mode = None  # sera déterminé en fct de s'il y a des joueurs "remote"
server_host = None  # recevra un str
server_port = None  # recevra un int
server_debug = None
solde_gp = None


def init_sound():
    global snd_channels

    if len(snd_channels) < 1:
        capital_n = 3
        pygame.mixer.set_num_channels(capital_n)
        for k in range(capital_n):
            snd_channels[k] = pygame.mixer.Channel(k)


def is_sfx_playin():
    global snd_channels
    for cn in range(2):
        if snd_channels[cn].get_busy():
            return True
    return False


def playmusic():
    global snd_channels, song
    if song is None:
        pygame.mixer.music.load('assets/chiptronic.ogg')
        song = 1
    pygame.mixer.music.play(-1)


def playsfx(pygamesound):
    # TODO this is temp fix, for web ctx
    pygamesound.play()


def init_fonts_n_colors():
    global colors, fonts, my_colors, my_colors
    pygame.font.init()
    
    for name, v in my_colors.items():
        colors[name] = pygame.Color(v)
    for name, t in my_fonts.items():
        fonts[name] = pygame.font.Font(None, t[1])
