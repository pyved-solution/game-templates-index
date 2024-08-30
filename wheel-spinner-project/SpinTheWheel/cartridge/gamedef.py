import json
import math
import random

from . import glvars
from . import pimodules


pyv = pimodules.pyved_engine
pyv.bootstrap_e()
pygame = pyv.pygame
netw = pimodules.network  # important! used for get/post

screen = None
r4 = pygame.Rect(32, 32, 128, 128)
kpressed = set()
labels = [None, None]
ft = pygame.font.Font(None, 21)
gameserver_host = None

# TODO is there a way to enable pyved to provide metadata for the current game being executed??
SLUG_CART = 'SpinTheWheel'
scr_size = None

# ---------------
# pygame.display.setCaption("Spin the Wheel Game")
ft_obj = pygame.font.Font(None, 52)
# Colors
BLACK = "#2d3047"
WHITE = (255, 255, 255)
RED = "#c8553d"
GREEN = "#588b8b"
BLUE = "#93b7be"
ORANGE = "#f28f3b"
PEACH = "#ffd5c2"

col_names = {
    WHITE: "white",
    RED: "red",
    GREEN: "green",
    BLUE: "blue",
    ORANGE: "orange",
    PEACH: "peach",
}

BG_COL = BLACK
CURSOR_COL = WHITE
# Define the wheel's wedges
NUM_WEDGES = 6

# ATTENTION: grosse astuce!
# comme on recherche l'alignement entre le cuseurs qui se trouve en haut de l'écran (et pas l'angle 0)
# et puis comme on dessine les wedges dans un ordre qui est inversé par rapport à la rotation appliquée
# sur la roue, nous devons à la fois selectionner le 1er element différemment
# ET utiliser l'ordre inverser pour que le calcul de wedge actuel + l'image affichée soit en cohérence
disp_order_WEDGE_COLORS = [RED, GREEN, BLUE, ORANGE, PEACH, WHITE]

WEDGE_COLORS = [WHITE, RED, GREEN, BLUE, ORANGE, PEACH]
WEDGE_COLORS.reverse()

ANGLE_PER_WEDGE = 360 / NUM_WEDGES
WHEEL_RADIUS = 200
angles_thresholds = [(i * ANGLE_PER_WEDGE - 30, i * ANGLE_PER_WEDGE + 30) for i in range(6)]

# Wheel rotation
# 0 --> milieu du peach, -30..30 est donc l'intervalle où on est ds peach
current_angle = 0  # degrés & clockwise
spinning = False
speed = 0
deceleration = 0.08  # Constant deceleration
final_target_angle = 0
tmp_disp = None  # label to disp final wedge color
LABEL_POS = (320, 540)


def gen_initial_speed():
    return random.uniform(6.0, 21.667)  # the random spin speed, initially applied


def draw_wheel(center_x, center_y, angle):
    for i in range(NUM_WEDGES):
        start_angle = math.radians(angle + i * ANGLE_PER_WEDGE)
        end_angle = math.radians(angle + (i + 1) * ANGLE_PER_WEDGE)

        # Calculate the points for the wedge polygon
        start_x = center_x + WHEEL_RADIUS * math.cos(start_angle)
        start_y = center_y + WHEEL_RADIUS * math.sin(start_angle)
        end_x = center_x + WHEEL_RADIUS * math.cos(end_angle)
        end_y = center_y + WHEEL_RADIUS * math.sin(end_angle)

        # Draw the wedge
        points = [(center_x, center_y), (start_x, start_y), (end_x, end_y)]
        pygame.draw.polygon(screen, disp_order_WEDGE_COLORS[i], points)


def get_wcolor_under_cursor(curr_angle):
    global WEDGE_COLORS
    # Center of the wheel
    # center_x, center_y = WIDTH // 2, HEIGHT // 2
    # The angle where the cursor is pointing (upwards is 90 degrees)
    # cursor_angle = 90  # 90 degrees is the upward direction

    # Adjust the angle to see which wedge the cursor points to
    print(curr_angle)
    adjusted_angle = curr_angle % 360
    print('adjusted->', adjusted_angle)

    # Determine the wedge under the cursor
    for rank in range(0, 6):
        intv = angles_thresholds[rank]
        if intv[0] < adjusted_angle <= intv[1]:
            return WEDGE_COLORS[rank]
    return WEDGE_COLORS[0]  # because numbers below 0.0 arent supported by the for loop above


def fetch_endpoint_gameserver() -> str:
    # read the content from remote file "servers.json", and provide the ad-hoc URL
    # the game host is provided by what can be read on "http://pyvm.kata.games/servers.json"
    tmp = netw.get(
        'http://pyvm.kata.games', '/servers.json'
    ).to_json()
    print(tmp)
    game_server_infos = tmp[SLUG_CART]
    target_game_host = game_server_infos['url']
    return target_game_host


def paint_game(scr):
    # Draw the wheel
    global current_angle, spinning, speed, tmp_disp
    WIDTH, HEIGHT = scr.get_size()

    center_x, center_y = WIDTH // 2, HEIGHT // 2
    draw_wheel(center_x, center_y, current_angle)

    # Spin the wheel
    if spinning:
        current_angle -= speed
        speed -= deceleration
        if speed < 0.0001:
            spinning = False
            speed = 0
            wedge_color = get_wcolor_under_cursor(current_angle)
            wedge_name = col_names[wedge_color]
            # print(f"The wheel stopped at {wedge_name.capitalize()}!")
            tmp_disp = ft_obj.render(wedge_name.capitalize(), True, wedge_color,
                                     "#ffffff" if wedge_color != WHITE else "#000000")

    # Draw the cursor
    pygame.draw.polygon(screen, CURSOR_COL, [(center_x - 10, 50), (center_x + 10, 50), (center_x, 90)])
    if tmp_disp:
        screen.blit(tmp_disp, LABEL_POS)


def test_my_luck() -> tuple:
    """
    :return: a pair of integer values. The second one can be None
    """
    global gameserver_host
    print('call test my luck ------..........')
    # we have to use .text on the result bc we wish to pass a raw Serial to the model class
    netw_reply = netw.get('', gameserver_host, data={'jwt': glvars.stored_jwt})
    try:  # stop if error, stop right now as it will be easier to debug
        json_obj = json.loads(netw_reply.text)
        a, b = json_obj["serverNumber1"], json_obj["serverNumber2"]
        return a, b
    except json.JSONDecodeError:
        print(' --Warning-- : cant decode the JSON reply, after game server script has been called!')
        return None, None


@pyv.declare_begin
def init_game(vmst=None):
    global screen, gameserver_host, scr_size

    pyv.init(wcaption='Untitled pyved-based Game')

    glvars.stored_jwt = netw.get_jwt()
    glvars.stored_username = netw.get_username()
    screen = pyv.get_surface()
    scr_size = screen.get_size()
    print("jwt:", glvars.stored_jwt)
    print("username:", netw.get_username())

    gameserver_host = fetch_endpoint_gameserver()


@pyv.declare_update
def upd(time_info=None):
    global labels, spinning, tmp_disp, speed

    wanna_spin = False
    for ev in pygame.event.get():
        # manage game exit
        if ev.type == pygame.QUIT:
            pyv.vars.gameover = True
        elif ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_ESCAPE:
                pyv.vars.gameover = True
            elif ev.key == pygame.K_SPACE:
                wanna_spin = True
        # manage mouse clicking
        elif ev.type == pygame.MOUSEBUTTONDOWN:
            wanna_spin = True

    # ---------------
    #  logic update
    # ---------------
    if wanna_spin:
        if not spinning:
            # TODO use the precomputed server-side number
            if False:
                print('spinning!')
                spin_result = test_my_luck()
                print('rez:', spin_result)

            # Start the spinning
            spinning = True
            tmp_disp = None
            # initial_angle = current_angle % (90*6)  # Save the starting angle
            speed = gen_initial_speed()
            # Random target angle (1-3 full spins)
            # final_target_angle = initial_angle + random.uniform(360, 1080)

    # refresh screen
    screen.fill(BG_COL)
    paint_game(pyv.get_surface())
    pyv.flip()


@pyv.declare_end
def done(vmst=None):
    pyv.close_game()
