from . import pimodules


# aliases
pyv = pimodules.pyved_engine


# ----------------------
#  CONSTANTS
SCR_SIZE = (960, 720)
DEV_MODE = False
SKIP_MINING = False
MAX_FPS = 45
VERSION = '0.20.1a'
RESSOURCE_LOC = ['.']
CHOSEN_LANG = 'fr'
GAME_ID = 5
# ----------------------
#  GLOBAL VARIABLES
song = None
snd_channels = dict()
num_lastchannel = 0  # pr alterner entre 0 et 1


colors = dict()
fonts = dict()

multiplayer_mode = None  # sera déterminé en fct de s'il y a des joueurs "remote"
server_host = None  # recevra un str
server_port = None  # recevra un int
server_debug = None

ev_manager = None  # will be set once the game begins
screen = None  # idem
GameStates = pyv.custom_struct.enum(
    'Menu',
    'Login',
    'Tetris',
    'Credits',
    'TaxPayment'
)
ChoixMenu = pyv.custom_struct.enum(
    'DemoMode',
    'StartChallenge',
    'SeeInfos',
    'QuitGame'
)
# ---------------
# linked to katagames services
# ---------------
user_id = None
username = None  # indique si on est log
stored_session = None  # jwt

cr_balance = None
ready_to_compete = False  # will be True when at the same time user auth + can_pay_challenge has been called

payment_token = None
# num_challenge = None  # sera un entier
chall_seed = None  # sera un entier déterminant cmt générateur aléatoire va sortir les données du problème d'optim.


def cli_logout():
    global nom_utilisateur, solde_gp, id_perso
    nom_utilisateur = solde_gp = id_perso = None


def load_server_config():
    # f = open(os.path.join('..','server.cfg'))
    pass

    # ToDO check if this block necessary, i comment it for web ctx
    # f = open(os.path.join('server.cfg'))
    # config_externe = f.readlines()
    # global server_host, server_port, server_debug
    # k = int(config_externe[0])
    # server_debug = False if (k == 0) else True
    # server_host = config_externe[1].strip("\n")
    # server_port = int(config_externe[2])


def init_sound():
    global snd_channels
    pyg = pyv.pygame
    if len(snd_channels) < 1:
        capital_n = 3
        pyg.mixer.set_num_channels(capital_n)
        for k in range(capital_n):
            snd_channels[k] = pyg.mixer.Channel(k)


def is_sfx_playin():
    global snd_channels
    for cn in range(2):
        if snd_channels[cn].get_busy():
            return True
    return False


def playmusic():
    global snd_channels, song
    if song is None:
        # song = pygame.mixer.Sound('chiptronic.ogg')
        # musicchannel = snd_channels[2]
        # musicchannel.play(song)
        pyv.pygame.mixer.music.load('assets/chiptronic.ogg')
        song = 1
    pyv.pygame.mixer.music.play(-1)


def playsfx(pygamesound):
    # global snd_channels, num_lastchannel
    # num_lastchannel = (num_lastchannel + 1) % 2
    # snd_channels[num_lastchannel].play(pygamesound)
    # TODO this is temp fix, for web ctx
    pygamesound.play()


def init_fonts_n_colors():
    global colors, fonts
    from .fonts_n_colors import my_fonts, my_colors
    pyv.pygame.font.init()
    
    for name, v in my_colors.items():
        colors[name] = pyv.pygame.Color(v)

    for name, t in my_fonts.items():
        # tmp = list(RESSOURCE_LOC)
        # tmp.append(t[0])
        # source = os.path.join(*tmp)
        fonts[name] = pyv.pygame.font.Font(None, t[1])
