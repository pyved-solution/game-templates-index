#import katagames_sdk.capsule.engine_ground.conf_eng as cgm_conf
#import katagames_sdk.engine as kataen
from app.puzzle.TetColors import TetColors
import katagames_sdk as katasdk

pygame = katasdk.import_pygame()

# ----------------------
#  CONSTANTS
# ----------------------
DEV_MODE = True
GAME_ID = 8  # 8 pour blokuman, c codé en dur coté serv
SKIP_MINING = False
SQ_SIZE = 20
BORDER_SIZE = 3
MAX_FPS = 45
VERSION = '0.20.1a'
RESSOURCE_LOC = ['assets']
CHOSEN_LANG = 'fr'


#  GLOBAL VARS
# ----------------------
# engine
username = None
acc_id = None

# specific
solde_gp = None
border_fade_colour = None
colour_map = None
song = None
snd_channels = dict()
num_lastchannel = 0  # pr alterner entre 0 et 1
copie_solde = None
colors = dict()
fonts = dict()
num_challenge = None  # sera un entier
chall_seed = 1  # sera un entier déterminant cmt générateur aléatoire va sortir les données du problème d'optim.
multiplayer_mode = None  # sera déterminé en fct de s'il y a des joueurs "remote"
server_host = None  # recevra un str
server_port = None  # recevra un int
server_debug = None


# ----------------------
#  UTIL. FUNCTIONS
# ----------------------
# def cli_logout():
#     global nom_utilisateur, solde_gp, id_perso
#     nom_utilisateur = solde_gp = id_perso = None


def load_server_config():
    import os
    f = open(os.path.join('server.cfg'))

    config_externe = f.readlines()
    global server_host, server_port, server_debug
    k = int(config_externe[0])
    server_debug = False if (k == 0) else True
    server_host = config_externe[1].strip("\n")
    server_port = int(config_externe[2])


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

    if not katasdk.runs_in_web():

        if song is None:
            pygame.mixer.music.load('assets/chiptronic.ogg')
            song = 1
        pygame.mixer.music.play(-1)


def playsfx(pygamesound):
    global snd_channels, num_lastchannel
    if not katasdk.runs_in_web():

        num_lastchannel = (num_lastchannel + 1) % 2
        snd_channels[num_lastchannel].play(pygamesound)


def init_fonts_n_colors():
    from fonts_n_colors import my_fonts, my_colors
    import os

    global border_fade_colour, colour_map, colors, fonts
    border_fade_colour = pygame.Color(50, 50, 50)

    # - BLOc standardisé -
    pygame.font.init()
    for name, v in my_colors.items():
        colors[name] = pygame.Color(v)
    ressource_loc_li = ['.']
    for name, t in my_fonts.items():
        if t[0] is not None:
            tmp = list(ressource_loc_li)
            tmp.append(t[0])
            source = os.path.join(*tmp)
        else:
            source = None
        fonts[name] = pygame.font.Font(source, t[1])
    print('chargement fonts_n_colors *** OK!')

    # pygame.font.init()
    # for name, v in my_colors.items():
    #     colors[name] = pygame.Color(v)
    # for name, t in my_fonts.items():
    #     tmp = list(RESSOURCE_LOC)
    #     tmp.append(t[0])
    #     source = os.path.join(*tmp)
    #     fonts[name] = pygame.font.Font(source, t[1])

    # bonus algo, helper pour afficher tetromino sprites...
    colour_map = {
        TetColors.Gray: colors['c_gray2'],
        TetColors.Clear: colors['bgspe_color'],  #colors['c_lightpurple'],
        TetColors.Pink: colors['c_skin']
    }


